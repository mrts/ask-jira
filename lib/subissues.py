from __future__ import unicode_literals

def list_epics_stories_and_tasks(jira, query):
    result = []
    epics = jira.search_issues(query, maxResults=1000,
            fields="summary,description")
    for epic in epics:
        result.append(_to_string(epic))
        stories = jira.search_issues('"Epic Link" = %s' % epic.key)
        for story in stories:
            result.append(_to_string(story, 1))
            tasks = jira.search_issues('parent = %s' % story.key)
            for task in tasks:
                result.append(_to_string(task, 2))
    return '\n'.join(result)

def _to_string(issue, level=0):
    offset = level * '    '
    result = '{0}* {1.key}: {1.fields.summary}'
    if issue.fields.description:
        lines = issue.fields.description.splitlines()
        result += '  \n'
        result += '  \n'.join(offset +
                (line if not line.startswith('*') else '\\' + line)
                for line in lines)
    return result.format(offset, issue)
