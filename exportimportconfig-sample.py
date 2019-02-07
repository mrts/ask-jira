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

ASSIGNEE_MAP = {
        'usera': 'user1',
        'userb': 'user2',
}

REPORTER_MAP = ASSIGNEE_MAP

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

ADD_COMMENT_TO_OLD_ISSUE = True

CUSTOM_FIELD = ('customfield_11086', {'value': 'Custom value'})

#NO_AUTO_CREATE_EPICS = True
#NO_AUTO_CREATE_SUBTASKS = True

