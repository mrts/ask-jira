# ask-jira

Python app that uses the Jira API for aggregate and complex reports
that are not possible with filters or gadgets in Jira web UI.

Features:

* sum time tracking information for the given JQL query

## Installation

    git clone https://github.com/mrts/ask-jira.git
    cd ask-jira
    virtualenv venv
    . venv/scripts/activate # or venv/bin/activate in non-Windows
    pip install --requirement=requirements.txt
    cp jiraconfig-sample.py jiraconfig.py
    # edit jiraconfig.py
    ./ask-jira.py # for testing, will print available projects

## Running

    ./ask-jira.py sum_timetracking_for_jql 'project = PROJ and sprint in openSprints()'
