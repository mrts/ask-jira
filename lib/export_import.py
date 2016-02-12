from __future__ import print_function

from io import BytesIO
from jira.client import JIRA
from jira.exceptions import JIRAError

def export_import_issues(export_jira, import_conf, query):
    import_jira = JIRA({'server': import_conf.JIRA['server']},
                basic_auth=(import_conf.JIRA['user'], import_conf.JIRA['password']))
    issues = export_jira.search_issues(query, maxResults=1000)
    result = []
    print('About to export/import', len(issues), 'issues')
    _make_new_issues(export_jira, import_jira, issues, import_conf, result, None)
    return result

def _make_new_issues(jira1, jira2, issues, conf, result, parent):
    for issue in issues:
        if not parent:
            print('Exporting', issue.key, end=' ')
        # re-fetch to include comments and attachments
        issue = jira1.issue(issue.key, expand='comments,attachments')
        fields = _get_new_issue_fields(issue.fields, conf)
        if parent:
            fields['parent'] = {'key': parent.key}

        new_issue = jira2.create_issue(fields=fields)
        if not parent:
            print('to', new_issue.key, '...', end=' ')

        _set_epic_link(issue, new_issue, conf, jira1, jira2)

        if issue.fields.comment.comments:
            _add_comments(jira2, new_issue, issue.fields.comment.comments)
        if issue.fields.attachment:
            try:
                _add_attachments(jira2, new_issue, issue.fields.attachment)
            except JIRAError as e:
                print('ERROR: attachment import failed with status',
                        e.status_code, '...', end=' ')
        if issue.fields.subtasks:
            subtasks = [jira1.issue(subtask.key) for subtask in
                    issue.fields.subtasks]
            print('with', len(subtasks), 'subtasks ...', end=' ')
            _make_new_issues(jira1, jira2, subtasks, conf, result, new_issue)

        comment = 'Imported from *[{1}|{0}/browse/{1}]*'.format(
                jira1._options['server'], issue.key)
        jira2.add_comment(new_issue, comment)

        result.append(new_issue.key)
        if not parent:
            print('done')

def _get_new_issue_fields(fields, conf):
    result = {}
    result['project'] = conf.JIRA['project']
    for name in ('summary', 'description', 'labels'):
        value = getattr(fields, name)
        if value is not None:
            result[name] = value
    for name in ('priority', 'issuetype', 'assignee', 'reporter'): # 'status', -- cannot
        value = getattr(fields, name)
        if value:
            value = getattr(value, 'name')
            name_map = getattr(conf, name.upper() + '_MAP')
            result[name] = {'name': name_map[value]}
    if conf.CUSTOM_FIELD:
        result[conf.CUSTOM_FIELD[0]] = conf.CUSTOM_FIELD[1]
    return result

_g_epic_map = {}

def _set_epic_link(old_issue, new_issue, conf, jira1, jira2):
    source_epic_key = getattr(old_issue.fields, conf.SOURCE_EPIC_LINK_FIELD_ID)
    if not source_epic_key:
        return
    global _g_epic_map
    if source_epic_key not in _g_epic_map:
        source_epic = jira1.issue(source_epic_key)
        epic_fields = _get_new_issue_fields(source_epic.fields, conf)
        epic_fields[conf.TARGET_EPIC_NAME_FIELD_ID] = getattr(
                source_epic.fields, conf.SOURCE_EPIC_NAME_FIELD_ID)
        target_epic = jira2.create_issue(fields=epic_fields)
        _g_epic_map[source_epic_key] = target_epic
    target_epic = _g_epic_map[source_epic_key]
    jira2.add_issues_to_epic(target_epic.key, [new_issue.key])
    print('linked to epic', target_epic.key, '...', end=' ')

def _add_comments(jira, issue, comments):
    for comment in comments:
        jira.add_comment(issue, u"*Comment by {0}*:\n{1}"
                .format(comment.author.displayName, comment.body))

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
# - components, fixVersions
# - estimates and timelogs
# - jira1.add_comment("Exported to ...")
# - keep original key? (optional, may collide in target project)
# - comment authors map -- cannot change comment authors easily
