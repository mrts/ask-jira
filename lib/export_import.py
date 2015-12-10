import json
from io import BytesIO

def export_import_issues(jira1, jira2, project, query):
    issues = jira1.search_issues(query, maxResults=1000)
    result = []
    _make_new_issues(jira1, jira2, issues, project, result, None)
    return result

def _make_new_issues(jira1, jira2, issues, project, result, parent):
    for issue in issues:
        # re-fetch to include comments and attachments
        issue = jira1.issue(issue.key, expand='comments,attachments')
        fields = _get_new_issue_fields(issue.fields)
        fields['project'] = project
        if parent:
            fields['parent'] = {'key': parent.key}

        new_issue = jira2.create_issue(fields=fields)

        if issue.fields.subtasks:
            subtasks = [jira1.issue(subtask.key) for subtask in
                    issue.fields.subtasks]
            _make_new_issues(jira1, jira2, subtasks, project, result, new_issue)
        if issue.fields.comment.comments:
            _add_comments(jira2, new_issue, issue.fields.comment.comments)
        if issue.fields.attachment:
            _add_attachments(jira2, new_issue, issue.fields.attachment)

        jira2.add_comment(new_issue, 'Imported from {0}'.format(issue.key))

        result.append(new_issue.key)

def _get_new_issue_fields(fields):
    result = {}
    for name in ('summary', 'description'): #, 'created', 'updated' -- cannot
        value = getattr(fields, name)
        if value is not None:
            result[name] = value
    for name in ('priority', 'issuetype'): # 'status', -- cannot
        result[name] = {'name': getattr(getattr(fields, name), 'name')}
    return result

def _add_comments(jira, issue, comments):
    for comment in comments:
        jira.add_comment(issue, u"Comment by {0}: {1}"
                .format(comment.author.name, comment.body))

def _add_attachments(jira, issue, attachments):
    for attachment in attachments:
        with BytesIO() as buf:
            for chunk in attachment.iter_content():
                buf.write(chunk)
            jira.add_attachment(issue, filename=attachment.filename,
                    attachment=buf)

# -------------------------------------
# TODO:
# - configurable maxResults
# - more mappings from http://stackoverflow.com/a/26043914/258772
# - reporter, assignee, components, fixVersions
# - keep original key? (optional, may collide in target project)
# - comment authors map
