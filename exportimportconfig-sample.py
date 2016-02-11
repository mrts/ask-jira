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

CUSTOM_FIELD = ('customfield_11086', {'value': 'Custom value'})
