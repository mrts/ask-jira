# ask-jira

Python app that uses the Jira API for automated tasks and aggregate or complex reports
that are not possible with filters or gadgets in Jira web UI.

Features:

* `export_import_issues_for_jql`: export issues from one Jira instance to
  another with comments and attachments

* `list_epics_stories_and_tasks_for_jql`: print a Markdown-compatible tree
  of epics, stories and subtasks that match the given JQL query

* `projects`: List available Jira projects (mainly for testing)

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
               'export_import_issues_for_jql': Export issues from one Jira instance
                 to another with comments and attachments
               'list_epics_stories_and_tasks_for_jql': Print a Markdown-compatible tree of epics,
                 stories and subtasks that match the given JQL query
               'projects': List available Jira projects
               'sum_timetracking_for_jql': Sum original estimate, time spent
                 and time remaining for all issues that match the given JQL query

    optional arguments:
      -h, --help  show this help message and exit

## Examples

    ./ask-jira.py sum_timetracking_for_jql 'project = PROJ and sprint in openSprints()'
    ./ask-jira.py list_epics_stories_and_tasks_for_jql 'project = PROJ and type = Epic'
