#!/usr/bin/env python

from __future__ import print_function

import sys
import pprint
from jira.client import JIRA

from lib import timetracking
from lib import subissues

import jiraconfig as conf

# actions

def projects(jira):
    projects = jira.projects()
    print("Available Jira projects:")
    pprint.pprint([project.name for project in projects])

def sum_timetracking_for_jql(jira):
    jql = sys.argv[2]
    results = timetracking.sum_timetracking_for_jql(jira, jql)
    pprint.pprint(results)

def list_epics_stories_and_tasks_for_jql(jira):
    jql = sys.argv[2]
    results = subissues.list_epics_stories_and_tasks(jira, jql)
    print(results)

# main

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "projects"
    action = globals()[action]
    jira = JIRA({'server': conf.JIRA_SERVER},
                basic_auth=(conf.JIRA_USER, conf.JIRA_PASSWORD))
    action(jira)


if __name__ == "__main__":
    main()
