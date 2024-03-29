from __future__ import print_function
import httplib2
import re
import os
import sys
import datetime
from datetime import timezone
from functools import total_ordering

import dateutil.parser
import pytz

from jira.exceptions import JIRAError

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


class WorklogParseError(RuntimeError):
    pass


def import_worklogs(jira, jira_user, worklogconfig, calendar_name, from_day, to_day):
    """
    Imports worklogs using the Google Calendar API and sumbits them to JIRA.
    Calendar entries must start with JIRA issue IDs opitionally followed by
    ':' and comments. Returns total hours logged as timedelta.
    """
    if from_day >= to_day:
        print('Start date must be before end date, start:', from_day, 'end:', to_day)
        return 0

    from_day = _convert_to_datestring(from_day, worklogconfig)
    to_day = _convert_to_datestring(to_day, worklogconfig)
    service = _get_calendar_service(worklogconfig)
    calendarId = _get_calendar_id(service, calendar_name)

    eventsResult = service.events().list(calendarId=calendarId, timeMin=from_day, timeMax=to_day,
                                         maxResults=1000, singleEvents=True, orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No events found in calendar', calendar_name, 'during', from_day, '-', to_day)
        return 0

    durations = []
    prefix_filter = worklogconfig.WORKLOG_PREFIX_FILTER if hasattr(worklogconfig,
            'WORKLOG_PREFIX_FILTER') and worklogconfig.WORKLOG_PREFIX_FILTER else None
    if prefix_filter:
        print('** Filtering worklogs by prefix', prefix_filter)
        events = [event for event in events if
                event['summary'].startswith(prefix_filter)]
    for event in events:
        try:
            gcal_worklog = Worklog.from_gcal(event, worklogconfig.JIRA_TIMEZONE)
            jira_worklogs = [Worklog.from_jira(w)
                    for w in jira.worklogs(gcal_worklog.issue)
                    if w.author.name == jira_user]
            if (jira_worklogs and gcal_worklog in jira_worklogs):
                jira_worklog = next(w for w in jira_worklogs if w == gcal_worklog)
                if gcal_worklog.duration != jira_worklog.duration:
                    raise WorklogParseError('Google worklog for issue %s '
                                            'starting at %s: duration %s differs from JIRA duration %s'
                                            % (gcal_worklog.issue, gcal_worklog.start,
                                               gcal_worklog.duration, jira_worklog.duration))
                print(gcal_worklog.duration, 'hours starting', gcal_worklog.start,
                      'already logged for', gcal_worklog.issue)
            else:
                print('Logging', gcal_worklog.duration, 'hours starting', gcal_worklog.start, 'for', gcal_worklog.issue)
                jira.add_worklog(issue=gcal_worklog.issue,
                                 timeSpentSeconds=gcal_worklog.duration.seconds,
                                 started=gcal_worklog.start,
                                 comment=gcal_worklog.comment)
                durations.append(gcal_worklog.duration)
        except WorklogParseError as e:
            print(e)
        except JIRAError as e:
            print("Issue '" + gcal_worklog.issue + "' does not exist (or other JIRA error):", e)

    return sum(durations, datetime.timedelta(0))


JIRA_ISSUE_REGEX = re.compile('[A-Z\d]+-\d+')


@total_ordering
class Worklog(object):

    @staticmethod
    def from_gcal(event, jira_timezone):
        start = _parse_iso_date(event['start'].get('dateTime'))
        end = _parse_iso_date(event['end'].get('dateTime'))
        duration = end - start
        summary = event['summary']
        summary = event['summary'].split(':', 1)
        issue = summary[0].strip()
        if not JIRA_ISSUE_REGEX.match(issue):
            raise WorklogParseError("'%s' is not a JIRA issue ID" %
                                    issue.encode('utf-8'))
        comment = summary[1].strip() if len(summary) > 1 else ''

        # Dates in JIRA use JIRA server timezone, tzinfo is ignored, hence manual offset calculation is required
        # if timezone support is required in Jira.
        # What's worse, daylight saving time is not taken into account in Jira,
        # see https://jira.atlassian.com/browse/JRASERVER-25855, so it has to
        # be manually subtracted.
        if jira_timezone:
            jira_tz = pytz.timezone(jira_timezone)
            start_localized = jira_tz.localize(start.replace(tzinfo=None))
            start = start_localized.astimezone(timezone.utc)
            if start_localized.dst():
                start -= datetime.timedelta(hours=1)

        return Worklog(start, duration, issue, comment)

    @staticmethod
    def from_jira(jira_worklog):
        start = _parse_iso_date(jira_worklog.started)
        duration = datetime.timedelta(seconds=jira_worklog.timeSpentSeconds)
        return Worklog(start, duration)

    def __init__(self, start, duration, issue=None, comment=None):
        self.start = start
        self.duration = duration
        self.issue = issue
        self.comment = comment

    def __eq__(self, other):
        if type(self) is not type(other):
            return NotImplemented
        return self.start == other.start

    def __lt__(self, other):
        return NotImplemented


def _convert_to_datestring(datestr, conf):
    return datetime.datetime.strptime(datestr, '%Y-%m-%d').isoformat() + conf.TIMEZONE


def _get_calendar_service(conf):
    credentials = _get_credentials(conf)
    return build('calendar', 'v3', credentials=credentials)


def _get_calendar_id(service, calendar_name):
    calendars = service.calendarList().list().execute().get('items', [])
    calendarId = next((c['id'] for c in calendars
                       if c['summary'] == calendar_name), None)
    if calendarId is None:
        raise RuntimeError("Calendar '%s' not found" % calendar_name)
    return calendarId


def _parse_iso_date(datestr):
    return dateutil.parser.parse(datestr)


def _get_credentials(conf):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    credentials = None
    if os.path.exists(conf.CREDENTIAL_FILE):
        credentials = Credentials.from_authorized_user_file(conf.CREDENTIAL_FILE, conf.SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            # avoid mess with argparse
            # sys.argv = [sys.argv[0]]
            flow = InstalledAppFlow.from_client_secrets_file(conf.CLIENT_SECRET_FILE, conf.SCOPES)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        print('Storing Google Calendar credentials to', conf.CREDENTIAL_FILE)
        with open(conf.CREDENTIAL_FILE, 'w') as credentials_token:
            credentials_token.write(credentials.to_json())
    return credentials
