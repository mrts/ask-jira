JIRA2 = {
    "server": "https://example.com/jira2/",
    "user": "user2",
    "password": "password2"
    "project": "PROJECTKEY",
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

STATUS_TRANSITIONS = {
    'Open': None,
    'Reopened': None,
    'In Progress': ('Start work',),
    'In Testing': ('Start work', 'Work done', 'Review passed'),
    'Resolved': ('Start work', 'Work done', 'Review passed', 'Testing passed'),
    'Closed': ('Start work', 'Work done', 'Review passed', 'Testing passed'),
}

ADD_COMMENT_TO_OLD_ISSUE = True

CUSTOM_FIELD = ('customfield_11086', {'value': 'Custom value'})
