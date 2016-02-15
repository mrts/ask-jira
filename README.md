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

## Installation

    git clone https://github.com/mrts/ask-jira.git

    cd ask-jira

    virtualenv venv
    . venv/scripts/activate # or venv/bin/activate in non-Windows
    pip install --requirement=requirements.txt

    cp jiraconfig-sample.py jiraconfig.py
    # edit jiraconfig.py

    ./ask-jira.py projects # for testing, will print available projects

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
               'list_epics_stories_and_tasks_for_jql': Print a Markdown-compatible tree of epics,
                 stories and subtasks that match the given JQL query
               'projects': List available JIRA projects
               'sum_timetracking_for_jql': Sum original estimate, time spent
                 and time remaining for all issues that match the given JQL query

    optional arguments:
      -h, --help  show this help message and exit

## Examples

    ./ask-jira.py sum_timetracking_for_jql 'project = PROJ and sprint in openSprints()'
    ./ask-jira.py list_epics_stories_and_tasks_for_jql 'project = PROJ and type = Epic'

## Export/import

The `export_import_issues_for_jql` task exports issues from one JIRA instance
to another with comments, attachments, epics and sub-tasks.

It needs special configuration in `exportimportconfig.py` (see sample in `exportimportconfig-sample.py`):

* `PRIORITY_MAP`: map source JIRA priorities to target priorities, e.g. `'Major': 'Medium'`
* `ISSUETYPE_MAP`: map source JIRA issue types to target issue types,  e.g. `'New Feature': 'Story'`
* `ASSIGNEE_MAP`: map source JIRA assignees to target assignees
* `REPORTER_MAP`: map source JIRA reporters to target reporters (usually identical to `ASSIGNEE_MAP`)
* `SOURCE_EPIC_LINK_FIELD_ID`: ID of the epic field in source JIRA, find it by calling `fields`, look for *Epic Link*
* `SOURCE_EPIC_NAME_FIELD_ID`: ID of the epic field in source JIRA, find it by calling `fields`, look for *Epic Name*
* `TARGET_EPIC_NAME_FIELD_ID`: ID of the epic field in **target** JIRA, find it by changing configuration to use target JIRA and calling `fields`, look for *Epic Name*
* `STATUS_TRANSITIONS`: map of source JIRA statuses to list of workflow transition names in target JIRA that result in equivalent status, `None` for no transition
* `ADD_COMMENT_TO_OLD_ISSUE`: if `True`, add comment to source JIRA issue that it was exported to new issue in target JIRA with issue link
* `CUSTOM_FIELD`: a single custom field that you can set to a default value for all issues (set to `None` if not needed)

Note that epics and sub-tasks should be excluded from the source JIRA query as
they are automatically imported via the parent task. The the recommended
snippet to add to the query is:

    AND issuetype not in subTaskIssueTypes() AND issuetype != Epic

Full example:

    ./ask-jira.py export_import_issues_for_jql 'project = PROJ
        AND status not in (Closed, Done, Fixed, Resolved)
        AND issuetype not in subTaskIssueTypes()
        AND issuetype != Epic'
