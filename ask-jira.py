#!/usr/bin/env python

import sys
import pprint
from jira.client import JIRA

from lib import timetracking

import jiraconfig as conf

# actions

def projects(jira, printer):
    projects = jira.projects()
    printer("Available Jira projects:")
    printer([project.name for project in projects])

def sum_timetracking_for_jql(jira, printer):
    jql = sys.argv[2]
    results = timetracking.sum_timetracking_for_jql(jira, jql)
    printer(results)

# main

def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "projects"
    action = globals()[action]
    jira = JIRA({'server': conf.JIRA_SERVER},
                basic_auth=(conf.JIRA_USER, conf.JIRA_PASSWORD))
    action(jira, pprint.pprint)


if __name__ == "__main__":
    main()
