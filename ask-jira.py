#!/usr/bin/env python

from __future__ import print_function

import sys
import pprint
import argparse
import inspect
from jira.client import JIRA

from lib import timetracking
from lib import subissues
from lib import export_import
from utils.smart_argparse_formatter import SmartFormatter

import jiraconfig as conf

# helpers

def _make_jql_argument_parser(parser):
    parser.add_argument("jql", help="the JQL query used in the command")
    return parser

# commands

def projects(jira, args):
    """List available JIRA projects"""
    projects = jira.projects()
    print("Available JIRA projects:")
    pprint.pprint([project.name for project in projects])

def fields(jira, args):
    """List available JIRA field names and IDs"""
    print("Available JIRA fields (name, id):")
    pprint.pprint([(field['name'], field['id']) for field in jira.fields()])

def sum_timetracking_for_jql(jira, args):
    """Sum original estimate, time spent
    and time remaining for all issues that match the given JQL query"""
    results = timetracking.sum_timetracking_for_jql(jira, args.jql)
    pprint.pprint(results)

sum_timetracking_for_jql.argparser = _make_jql_argument_parser

def list_epics_stories_and_tasks_for_jql(jira, args):
    """Print a Markdown-compatible tree of epics,
    stories and subtasks that match the given JQL query"""
    results = subissues.list_epics_stories_and_tasks(jira, args.jql)
    print(results)

list_epics_stories_and_tasks_for_jql.argparser = _make_jql_argument_parser

def export_import_issues_for_jql(jira1, args):
    """Export issues from one JIRA instance
    to another with comments and attachments"""
    import exportimportconfig
    exported_issues = export_import.export_import_issues(jira1,
            exportimportconfig, args.jql)
    print('Successfully imported', exported_issues)

export_import_issues_for_jql.argparser = _make_jql_argument_parser

# main

def _main():
    argparser = _make_main_argument_parser()
    command = _get_command(argparser)
    args = _parse_command_specific_arguments(command, argparser)
    jira = JIRA({'server': conf.JIRA['server']},
                basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    command(jira, args)

# helpers

def _make_main_argument_parser():
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    parser.add_argument("command", help="R|the command to run, available " +
            "commands:\n{0}".format(_list_local_commands()))
    return parser

def _get_command(argparser):
    def print_help_and_exit():
        argparser.print_help()
        sys.exit(1)
    if len(sys.argv) < 2:
        print_help_and_exit()
    command = sys.argv[1]
    if not command[0].isalpha():
        print_help_and_exit()
    if command not in globals():
        print("Invalid command: {0}\n".format(command), file=sys.stderr)
        print_help_and_exit()
    command = globals()[command]
    return command

def _list_local_commands():
    sorted_globals = list(globals().items())
    sorted_globals.sort()
    commands = [(var, obj.__doc__) for var, obj in sorted_globals
        if not var.startswith('_')
           and inspect.isfunction(obj)]
    return "\n".join("'{0}': {1}".format(name, doc) for name, doc in commands)

def _parse_command_specific_arguments(command, argparser):
    if hasattr(command, 'argparser'):
        command_argparser = command.argparser(argparser)
        return command_argparser.parse_args()
    return None

if __name__ == "__main__":
    _main()
