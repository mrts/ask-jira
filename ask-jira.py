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
from lib import google_calendar
from utils.smart_argparse_formatter import SmartFormatter

import jiraconfig as conf

# helpers

def _make_jql_argument_parser(parser):
    parser.add_argument("jql", help="the JQL query used in the command")
    return parser


def _make_jql_and_optional_portfolio_epics_argument_parser(parser):
    parser = _make_jql_argument_parser(parser)
    parser.add_argument("--portfolio-epics", action="store_true", help="flag for enabling portfolio epic import")
    return parser


def _make_transitions_argument_parser(parser):
    parser.add_argument("issue", help="the JIRA issue key used in the command")
    return parser


# commands

def projects(jira, args):
    """List available JIRA projects"""
    print("Available JIRA projects:")
    pprint.pprint([project.name for project in jira.projects()])


def fields(jira, args):
    """List available JIRA field names and IDs"""
    print("Available JIRA fields (name, id):")
    pprint.pprint([(field['name'], field['id']) for field in jira.fields()])


def transitions(jira, args):
    """List available JIRA transitions for the given issue"""
    print("Available JIRA transitions:")
    pprint.pprint(jira.transitions(args.issue))

transitions.argparser = _make_transitions_argument_parser


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


def export_import_issues_for_jql(jira, args):
    """Export issues from one JIRA instance
    to another with comments and attachments"""
    import exportimportconfig
    exported_issues = export_import.export_import_issues(jira,
            exportimportconfig, args.jql, args.portfolio_epics)
    if exported_issues:
        print('Successfully imported', exported_issues)

export_import_issues_for_jql.argparser = _make_jql_and_optional_portfolio_epics_argument_parser


def import_worklogs_from_google_calendar(jira, args):
    """Import worklog entries from Google Calendar
    to corresponding JIRA tasks"""
    import worklogconfig
    hours = google_calendar.import_worklogs(jira, conf.JIRA['user'],
            worklogconfig, args.calendar, args.fromdate, args.todate)
    print('Logged', hours, 'hours')


def _import_worklogs_argument_parser(parser):
    parser.add_argument("calendar", help="the calendar name to import "
            "worklogs from")
    parser.add_argument("fromdate", help="import date range start, "
            "in yyyy-mm-dd format")
    parser.add_argument("todate", help="import date range end, "
            "in yyyy-mm-dd format")
    return parser

import_worklogs_from_google_calendar.argparser = _import_worklogs_argument_parser


# main

def _main():
    command_name, command = _get_command()
    args = _parse_command_specific_arguments(command_name, command)
    jira = JIRA({'server': conf.JIRA['server']}, # add 'verify': False if HTTPS cert is untrusted
                basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    command(jira, args)


# helpers

def _make_main_argument_parser():
    parser = argparse.ArgumentParser(formatter_class=SmartFormatter)
    parser.add_argument("command", help="R|the command to run, available " +
            "commands:\n{0}".format(_list_local_commands()))
    return parser


def _get_command():
    argparser = _make_main_argument_parser()
    def print_help_and_exit():
        argparser.print_help()
        sys.exit(1)
    if len(sys.argv) < 2:
        print_help_and_exit()
    command_name = sys.argv[1]
    if not command_name[0].isalpha():
        print_help_and_exit()
    if command_name not in globals():
        print("Invalid command: {0}\n".format(command_name), file=sys.stderr)
        print_help_and_exit()
    command = globals()[command_name]
    return command_name, command


def _list_local_commands():
    sorted_globals = list(globals().items())
    sorted_globals.sort()
    commands = [(var, obj.__doc__) for var, obj in sorted_globals
        if not var.startswith('_')
           and inspect.isfunction(obj)]
    return "\n".join("'{0}': {1}".format(name, doc) for name, doc in commands)


def _parse_command_specific_arguments(command_name, command):
    if not hasattr(command, 'argparser'):
        return None
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help=command_name)
    command_argparser = command.argparser(parser)
    return command_argparser.parse_args()


if __name__ == "__main__":
    _main()
