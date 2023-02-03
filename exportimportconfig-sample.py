from collections import namedtuple

JIRA = {
    'server': 'https://example.com/jira2/',
    'user': 'user2',
    'password': 'password2',
    'project': 'PROJECTKEY',
}

PRIORITY_MAP = {
        'Blocker': 'Blocker',
        'Critical': 'Critical',
        'Major': 'Major',
        'Minor': 'Minor',
        'Trivial': 'Trivial',
}

DEFAULT_PRIORITY = 'Major'

ISSUETYPE_MAP = {
        'Epic': 'Epic',
        'Story': 'Story',
        'Improvement': 'Story',
        'New Feature': 'Story',
        'Change request': 'Story',
        'Task': 'Task',
        'Bug': 'Bug',
        'Sub-task': 'Sub-task',
        'Development': 'Sub-task',
        'Design': 'Sub-task',
        'Technical task': 'Sub-task',
}

DEFAULT_ISSUETYPE = 'Task'

ASSIGNEE_MAP = {
        'usera': 'user1',
        'userb': 'user2',
}

DEFAULT_ASSIGNEE = 'user3'

REPORTER_MAP = ASSIGNEE_MAP

DEFAULT_REPORTER = DEFAULT_ASSIGNEE

SOURCE_EPIC_LINK_FIELD_ID = 'customfield_10251'
SOURCE_EPIC_NAME_FIELD_ID = 'customfield_10252'
TARGET_EPIC_NAME_FIELD_ID = 'customfield_10009'

WithResolution = namedtuple('WithResolution', 'transition_name')

RESOLUTION_MAP = {
    'Fixed': 'Fixed',
    "Won't Fix": "Won't Fix",
    'Later': "Won't Fix",
    'Duplicate': 'Duplicate',
    'Incomplete': 'Incomplete',
    'Cannot Reproduce': 'Cannot Reproduce',
    'Fixed as is': 'Fixed',
    'Fixed with minor changes': 'Fixed',
    'Fixed with changes': 'Fixed',
    'Fixed quite differently': 'Fixed',
    'Released': 'Done',
    'Resolved': 'Done',
    'Verified': 'Done',
    'Unresolved': "Won't Fix",
    'Done': 'Done',
}

# Note that transition names are different from status names.
# Set STATUS_TRANSITIONS to None if you want to disable status transition mapping.
STATUS_TRANSITIONS = {
    'Open': None,
    'Reopened': None,
    'In Progress': ('Start work',),
    'In Testing': ('Start work', 'Work done', 'Review passed'),
    'Resolved': ('Start work', 'Work done', 'Review passed',
        WithResolution('Testing passed')),
    'Closed': ('Start work', 'Work done', 'Review passed',
        WithResolution('Testing passed')),
}

STATUS_TRANSITIONS_ISSUETYPE = {
    'Sub-task': {
        'To Do': None,
        'In Progress': ('In Progress',),
        'Review': ('In Progress',),
        'Done': ('Done',),
    },
    'Task': {
        'To Do': None,
        'In Progress': ('In Progress',),
        'Review': ('In Progress',),
        'Done': ('Done',),
    }
}

INCLUDE_WORKLOGS = True
ADD_COMMENT_TO_OLD_ISSUE = True

PORTFOLIO_EPIC_LABEL = 'porfolio-epic'
PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_NAME = 'sub-epic'
PORTFOLIO_EPIC_SUB_EPIC_TARGET_LINK_NAME = 'sub-epic'

CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY = ('Text 1', 'customfield_10132')

CUSTOM_FIELD = ('customfield_11086', {'value': 'Custom value'})
# For the Tempo team field, use:
# CUSTOM_FIELD = ('customfield_11086', 'Team name')
# See https://community.atlassian.com/t5/Jira-Software-questions/Can-you-update-the-Tempo-team-field-using-automation/qaq-p/1355359

CUSTOM_FIELD_MAP = {
        'customfield_10200': 'customfield_11320', # User Story
        'customfield_10008': 'customfield_10004', # Story Points
        'customfield_10010': 'customfield_11321', # Acceptance Criteria
        'customfield_10401': 'customfield_11311', # Current Behavior
        'customfield_10402': 'customfield_11312', # Expected Behavior
}

