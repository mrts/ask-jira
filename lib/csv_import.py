from __future__ import print_function
import csv
import datetime
from datetime import timezone
import pytz
import re
from functools import total_ordering

from jira.exceptions import JIRAError
import dateutil.parser

class WorklogParseError(RuntimeError):
    pass

# FIXME: Add docs to README
# FIXME: reuse code between this and google_calendar.py
JIRA_ISSUE_REGEX = re.compile(r'[A-Z][A-Z0-9]+-\d+')

# FIXME
# Tee lehest koopia, et oleks ainult vajalikud tulbad.
# Lisa kommentaar, mis läheb Jirasse.
# Lae alla TSV.

@total_ordering
class Worklog(object):

    @staticmethod
    def from_csv(row, jira_timezone):
        # FIXME
        issue = row['Jira pilet'].strip()
        date_str = row['Kuupäev'].strip()
        hours_str = row['Tunnid'].strip()
        comment = row['Kommentaar'].strip()

        if not JIRA_ISSUE_REGEX.match(issue):
            raise WorklogParseError(f"'{issue}' is not a valid JIRA issue ID.")

        try:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise WorklogParseError(f"Invalid date format: '{date_str}'. Expected 'YYYY-MM-DD'.")

        try:
            hours = float(hours_str.replace(',', '.'))
        except ValueError:
            raise WorklogParseError(f"Invalid hours format: '{hours_str}'. Expected a number.")

        duration = datetime.timedelta(hours=hours)
        start = date.replace(hour=9, minute=0, second=0, microsecond=0)  # Assume work starts at 9 AM

        # Adjust for JIRA timezone
        if jira_timezone:
            jira_tz = pytz.timezone(jira_timezone)
            start_localized = jira_tz.localize(start)
            start = start_localized.astimezone(timezone.utc)
            if start_localized.dst():
                start -= datetime.timedelta(hours=1)

        return Worklog(start, duration, issue, comment)

    @staticmethod
    def from_jira(jira_worklog):
        start = dateutil.parser.parse(jira_worklog.started)
        duration = datetime.timedelta(seconds=jira_worklog.timeSpentSeconds)
        return Worklog(start, duration)

    def __init__(self, start, duration, issue=None, comment=None):
        self.start = start
        self.duration = duration
        self.issue = issue
        self.comment = comment

    def __eq__(self, other):
        if not isinstance(other, Worklog):
            return NotImplemented
        return self.start == other.start and self.duration == other.duration

    def __lt__(self, other):
        if not isinstance(other, Worklog):
            return NotImplemented
        return self.start < other.start

def import_worklogs(jira, jira_user, worklogconfig, csvfile):
    """
    Imports worklogs from a CSV file and submits them to JIRA.
    CSV entries must have columns 'Jira issue', 'Date', 'Worked hours'.
    Returns total hours logged as a timedelta object.
    """
    durations = []
    jira_timezone = getattr(worklogconfig, 'JIRA_TIMEZONE', None)

    try:
        with open(csvfile, encoding='utf-8') as csvfile_obj:
            reader = csv.DictReader(csvfile_obj, delimiter='\t')
            for row in reader:
                try:
                    csv_worklog = Worklog.from_csv(row, jira_timezone)
                    jira_worklogs = [
                        Worklog.from_jira(w)
                        for w in jira.worklogs(csv_worklog.issue)
                        if w.author.name == jira_user
                    ]
                    if csv_worklog in jira_worklogs:
                        print(
                            f"{csv_worklog.duration} hours starting {csv_worklog.start} "
                            f"already logged for {csv_worklog.issue}"
                        )
                    else:
                        print(
                            f"Logging {csv_worklog.duration} hours starting {csv_worklog.start} "
                            f"for {csv_worklog.issue}"
                        )
                        jira.add_worklog(
                            issue=csv_worklog.issue,
                            timeSpentSeconds=int(csv_worklog.duration.total_seconds()),
                            started=csv_worklog.start,
                            comment=csv_worklog.comment,
                        )
                        durations.append(csv_worklog.duration)
                except WorklogParseError as e:
                    print(f"Error parsing worklog: {e}")
                except JIRAError as e:
                    print(f"JIRA error for issue '{csv_worklog.issue}': {e}")
    except FileNotFoundError:
        print(f"CSV file not found: {csvfile}")
        return datetime.timedelta(0)

    total_duration = sum(durations, datetime.timedelta())
    return total_duration

