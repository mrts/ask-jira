# ask-jira

Python app that uses the JIRA API for automated tasks and aggregate or complex reports
that are not possible with filters or gadgets in JIRA web UI.

Features:

* `export_import_issues_for_jql`: export issues from one JIRA instance to
  another with comments and attachments (see *Export/import* below)

* `list_epics_stories_and_tasks_for_jql`: print a Markdown-compatible tree
  of epics, stories and subtasks that match the given JQL query

* `projects`: List available JIRA projects (mainly for testing)

* `fields`: List available JIRA field names and IDs

* `sum_timetracking_for_jql`: Sum original estimate, time spent and time
  remaining for all issues that match the given JQL query

* `import_worklogs_from_google_calendar`: Import worklog entries from Google
  Calendar to corresponding JIRA tasks

## Installation

    git clone https://github.com/mrts/ask-jira.git

    cd ask-jira

    python -m venv venv
    . venv/scripts/activate # when using Git BASH from Git for Windows
    # . venv/bin/activate # in non-Windows environments
    pip install --requirement=requirements.txt

    cp jiraconfig-sample.py jiraconfig.py

    # edit jiraconfig.py

    ./ask-jira.py projects # for testing, will print available projects

JIRA server configuration is picked up from `jiraconfig.py`.

## Usage

Run the command with

    $ ./ask-jira.py <command> <command-specific parameters>

Here's the default help:

    $ ./ask-jira.py
    usage: ask-jira.py [-h] command

    positional arguments:
     command   the command to run, available commands:
               'export_import_issues_for_jql': Export issues from one JIRA instance
                 to another with comments and attachments
               'fields': List available JIRA field names and IDs
               'import_worklogs_from_google_calendar': Import worklog entries from Google Calendar
                 to corresponding JIRA tasks
               'list_epics_stories_and_tasks_for_jql': Print a Markdown-compatible tree of epics,
                 stories and subtasks that match the given JQL query
               'projects': List available JIRA projects
               'sum_timetracking_for_jql': Sum original estimate, time spent
                 and time remaining for all issues that match the given JQL query
               'transitions': List available JIRA transitions for the given issue

    optional arguments:
      -h, --help  show this help message and exit

## Examples

    # current sprint velocity
    ./ask-jira.py sum_timetracking_for_jql 'project = PROJ and sprint in openSprints() and status = Closed'

    ./ask-jira.py list_epics_stories_and_tasks_for_jql 'project = PROJ and type = Epic'

## Export/import

The `export_import_issues_for_jql` task exports issues from one JIRA instance
to another with comments, attachments, epics and sub-tasks.

Source JIRA server configuration is picked up from `jiraconfig.py`.

There is special support for ["portfolio epics"](https://www.scaledagileframework.com/epic/),
a SAFe concept. Run `export_import_issues_for_jql` with the `--portfolio-epics`
flag to enable portfolio epic mode. In portfolio epic mode, the argument JQL
must return only top-level portfolio epics and all the linked issues are
recursively migrated along with them. See also configuration settings with
`PORTFOLIO_EPIC` prefix below.

The task needs special configuration in `exportimportconfig.py` (see sample in
`exportimportconfig-sample.py`):

* `JIRA`: the target JIRA server configuration where the issues are exported to
* `PRIORITY_MAP`: map source JIRA priorities to target priorities, e.g. `'Major': 'Medium'`
* `DEFAULT_PRIORITY`: if source JIRA priority is not found in `PRIORITY_MAP` use this priority (optional)
* `ISSUETYPE_MAP`: map source JIRA issue types to target issue types,  e.g. `'New Feature': 'Story'`
* `DEFAULT_ISSUETYPE`: if source JIRA issue type is not found in `ISSUETYPE_MAP` use this issue type (optional)
* `ASSIGNEE_MAP`: map source JIRA assignees to target assignees
* `DEFAULT_ASSIGNEE`: if source JIRA issue type is not found in `ASSIGNEE_MAP` use this issue type (optional)
* `REPORTER_MAP`: map source JIRA reporters to target reporters (usually identical to `ASSIGNEE_MAP`)
* `DEFAULT_REPORTER`: if source JIRA issue type is not found in `REPORTER_MAP` use this issue type (optional)
* `SOURCE_EPIC_LINK_FIELD_ID`: ID of the epic field in source JIRA, find it by calling `fields`, look for *Epic Link*
* `SOURCE_EPIC_NAME_FIELD_ID`: ID of the epic field in source JIRA, find it by calling `fields`, look for *Epic Name*
* `TARGET_EPIC_NAME_FIELD_ID`: ID of the epic field in **target** JIRA, find it by changing configuration to use target JIRA and calling `fields`, look for *Epic Name*
* `PORTFOLIO_EPIC_LABEL`: (porfolio epic mode) for an issue to be considered a porfolio epic, this label must be attached to it
* `PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_NAME`: (porfolio epic mode) only issues that are linked to the portfolio epic with this link name are migrated
* `PORTFOLIO_EPIC_SUB_EPIC_TARGET_LINK_NAME`: (porfolio epic mode) the link name to use in target JIRA to link issues to portfolio epics
* `STATUS_TRANSITIONS`: map of source JIRA statuses to list of workflow transition names in target JIRA that result in equivalent status, `None` for no transition
* `STATUS_TRANSITIONS_ISSUETYPE`: issuetype specific map of source JIRA statuses to list of workflow transition names in target JIRA that result in equivalent status, `None` for no transition. If an issuetype is not in this list, the default `STATUS_TRANSITIONS` are used.
* `RESOLUTION_MAP`: map source JIRA resolutions to target resolutions, only used when a `WithResolution` transition is used in `STATUS_TRANSITIONS`
* `CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY`: custom field in target JIRA for saving the source JIRA issue key, **specifying this avoids duplicate imports**, can be `None`
* `INCLUDE_WORKLOGS`: if `True`, add worklogs from source JIRA issue to the new issue in target JIRA
* `ADD_COMMENT_TO_OLD_ISSUE`: if `True`, add comment to source JIRA issue that it was exported to new issue in target JIRA with issue link
* `CUSTOM_FIELD`: a single custom field that you can set to a default value for all issues (set to `None` if not needed)
* `CUSTOM_FIELD_MAP`: map source JIRA fields to target JIRA fields. This can also be used for system fields that are not mapped out of the box, such as 'environment'

Note that epics and sub-tasks should be excluded from the source JIRA query as
they are automatically imported via the parent task. The recommended
snippet to add to the query is:

    AND issuetype not in subTaskIssueTypes() AND issuetype != Epic

Full example:

    ./ask-jira.py export_import_issues_for_jql 'project = PROJ
        AND status not in (Closed, Done, Fixed, Resolved)
        AND issuetype not in subTaskIssueTypes()
        AND issuetype != Epic'

## Importing worklogs from Google Calendar

The `import_worklogs_from_google_calendar` task helps filling JIRA time reports
from Google Calendar events. The Google Calendar events must be formatted
according to *JIRA-ID: comment* convention, where *JIRA-ID* is the JIRA issue
ID and *comment* is the comment to add to the worklog. The comment is optional.
The script finds the corresponding JIRA issue by ID and adds a worklog with the
event duration to it.

It needs special configuration in `worklogconfig.py` (see sample in
`worklogconfig-sample.py`, you probably need to change the Google Calendar
timezone in `TIMEZONE` and can keep the rest as-is).

You also need to setup API access to Google Calendar in Google Developers
Console as explained [here](https://developers.google.com/google-apps/calendar/quickstart/python#step_1_turn_on_the_api_name).
Be sure to download the OAuth client secret as instructed and save it to
`~/.credentials/client_secret.json`.

### Usage

Usage:

    ./ask-jira.py import_worklogs_from_google_calendar -h
    usage: ask-jira.py [-h] command calendar fromdate todate

    positional arguments:
      command     import_worklogs_from_google_calendar
      calendar    the calendar name to import worklogs from
      fromdate    import date range start, in yyyy-mm-dd format
      todate      import date range end, in yyyy-mm-dd format

Full example:

    ./ask-jira.py import_worklogs_from_google_calendar 'Timereport' 2017-02-23 2017-02-24
