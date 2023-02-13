from __future__ import print_function
from __future__ import unicode_literals

import unicodedata
from io import BytesIO
from jira.client import JIRA
from jira.exceptions import JIRAError


def export_import_issues(source_jira, conf, query, portfolio_epics=False):
    dest_jira = JIRA({'server': conf.JIRA['server']},
                basic_auth=(conf.JIRA['user'], conf.JIRA['password']))
    source_issues = source_jira.search_issues(query, maxResults=False)
    if not source_issues:
        print('No issues found for query', query, 'exiting')
        return []
    if portfolio_epics and not _has_portfolio_epic_label(source_issues[0], conf):
        print('Portfolio epics requested, but first issue',
                source_issues[0].key, 'does not have portfolio epic label',
                conf.PORTFOLIO_EPIC_LABEL)
        return []
    result = []
    print('About to export/import', len(source_issues), 'issues')
    _make_dest_issues(source_jira, dest_jira, source_issues, conf, result, None, portfolio_epics)
    return result


def _make_dest_issues(source_jira, dest_jira, source_issues, conf, result, parent, portfolio_epics):
    for source_issue in source_issues:
        if _already_imported(conf, dest_jira, source_issue.key):
            print('Issue', source_issue.key, 'has already been imported, skipping...')
            continue
        if not parent:
            print('Exporting', source_issue.key, end=' ')

        dest_issue = _map_issue(source_jira, dest_jira, source_issue, conf, result, parent, portfolio_epics)

        result.append(dest_issue.key)
        if not parent:
            print('done')


def _map_issue(source_jira, dest_jira, source_issue, conf, result, parent, portfolio_epics):
    # Re-fetch to include comments and attachments.
    source_issue = source_jira.issue(source_issue.key, expand='comments,attachments')
    fields = _get_dest_issue_fields(source_issue.fields, conf)
    if parent:
        fields['parent'] = {'key': parent.key}
    _add_source_jira_issue_key(conf, fields, source_issue.key)
    _map_versions(dest_jira, source_issue, fields, conf)

    dest_issue = dest_jira.create_issue(fields=fields)
    if not parent:
        print('to', dest_issue.key, '...', end=' ')

    _set_epic_link(dest_issue, source_issue, conf, source_jira, dest_jira)
    _set_status(dest_issue, source_issue, conf, dest_jira)

    # Worklogs.
    if conf.INCLUDE_WORKLOGS and source_issue.fields.worklog:
        for worklog in source_issue.fields.worklog.worklogs:
            dest_jira.add_worklog(dest_issue, None, worklog.timeSpentSeconds)

    # Attachments.
    if source_issue.fields.attachment:
        try:
            _add_attachments(dest_issue, dest_jira, source_issue.fields.attachment)
        except JIRAError as e:
            print('ERROR: attachment import failed with status',
                    e.status_code, '...', end=' ')
            dest_jira.add_comment(dest_issue, '*Failed to import attachments*')

    # Subtasks.
    if source_issue.fields.subtasks:
        subtasks = [source_jira.issue(subtask.key) for subtask in
                source_issue.fields.subtasks]
        print('with', len(subtasks), 'subtasks ...', end=' ')
        _make_dest_issues(source_jira, dest_jira, subtasks, conf, result, dest_issue, None)

    # Comments.
    if source_issue.fields.comment.comments:
        _add_comments(dest_issue, dest_jira, source_issue.fields.comment.comments)

    comment = 'Imported from *[{1}|{0}/browse/{1}]*'.format(
            source_jira._options['server'], source_issue.key)
    dest_jira.add_comment(dest_issue, comment)

    if conf.ADD_COMMENT_TO_OLD_ISSUE:
        comment = 'Exported to *[{1}|{0}/browse/{1}]*'.format(
                dest_jira._options['server'], dest_issue.key)
        source_jira.add_comment(source_issue, comment)

    # Portfolio epics.
    if portfolio_epics and _has_portfolio_epic_label(source_issue, conf):
        _map_sub_epics(source_jira, dest_jira, source_issue, dest_issue, conf, result)

    return dest_issue


def _map_sub_epics(source_jira, dest_jira, source_issue, dest_issue, conf, result):
    print('with sub-epics:')
    # Get all linked sub-epics and import them recursively.
    for linked_issue in source_issue.fields.issuelinks:
        if linked_issue.type.name == conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_NAME and \
            hasattr(linked_issue, conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_DIRECTION):
            if conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_DIRECTION == "inwardIssue":
                sub_epic = linked_issue.inwardIssue
            else:
                sub_epic = linked_issue.outwardIssue
            # Test if sub_epic already exists. Use that or create a new
            # Search always returns an iterator, but it may be empty
            # It then throws StopIteration, instead of giving us issue
            try:
                new_sub_epic = next(_already_imported(conf, dest_jira, sub_epic))
                print('Issue', sub_epic, 'has already been imported, link only...')
            except StopIteration:
                new_sub_epic = _map_issue(source_jira, dest_jira, sub_epic, conf, result, None, True)
            # Always create link, no matter if it was existing issue or new
            # If SWAP, change direction
            # If searched outwardIssue, or if searched inward, but SWAP is true
            inIssue  = dest_issue.key
            outIssue = new_sub_epic.key
            # If searched inwardIssue and no SWAP, or if searched outward, but SWAP is true
            if  (conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_DIRECTION == 'inwardIssue' and not conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_SWAP ) or \
                (conf.PORTFOLIO_EPIC_SUB_EPIC_SOURCE_LINK_DIRECTION == 'outwardIssue' and conf.PORTFOLIO_EPIC_SUB_EPIC_TARGET_LINK_SWAP):
                outIssue = dest_issue.key
                inIssue  = new_sub_epic.key
            
            dest_jira.create_issue_link(type=conf.PORTFOLIO_EPIC_SUB_EPIC_TARGET_LINK_NAME,
                    inwardIssue= inIssue, outwardIssue= outIssue )
            # TODO: add portfolio epic label to target
    print('Sub-epics of', source_issue.key, 'done.')


def _already_imported(conf, dest_jira, issue_key):
    if conf.CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY:
        # TODO: make the ~ operator configurable as well
        return dest_jira.search_issues("'{}' ~ '{}'".format(
            conf.CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY[0], issue_key))
    return False


def _add_source_jira_issue_key(conf, fields, issue_key):
    if conf.CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY:
        fields[conf.CUSTOM_FIELD_FOR_SOURCE_JIRA_ISSUE_KEY[1]] = issue_key


def _map_versions(dest_jira, source_issue, fields, conf):
    source_versions = getattr(source_issue.fields, 'fixVersions')
    if source_versions is not None:
        target_versions = []
        for version in source_versions:
            # We create the current version if it does not exist in the target JIRA project.
            target_version = _get_target_version_by_name(dest_jira, conf, getattr(version, 'name'))
            if target_version is None:
                target_version = dest_jira.create_version(getattr(version, 'name'), conf.JIRA['project'])

            target_versions.append({'id': getattr(target_version, 'id')})

        # Support multiple versions per ticket.
        fields['fixVersions'] = target_versions


def _has_portfolio_epic_label(source_issue, conf):
    return conf.PORTFOLIO_EPIC_LABEL in source_issue.fields.labels


def _get_target_version_by_name(jira, conf, name):
    """
    Get an existing version by name for the current project.

    :param jira: current jira resource
    :param conf: JIRA configurations
    :param name: name of the version to check
    """
    versions = jira.project_versions(conf.JIRA['project'])
    for version in versions:
        if getattr(version, 'name') == name:
            return version

    return None


def _get_dest_issue_fields(fields, conf):
    result = {}
    result['project'] = conf.JIRA['project']
    for name in ('summary', 'description', 'labels', 'environment'):
        value = getattr(fields, name)
        if value is not None:
            result[name] = value
    for fieldname in ('priority', 'issuetype', 'assignee', 'reporter'):
        value = getattr(fields, fieldname)
        if value:
            value = getattr(value, 'name')
            fieldname_map = getattr(conf, fieldname.upper() + '_MAP')
            if value in fieldname_map:
                mapped_value = fieldname_map[value]
            else:
                try:
                    mapped_value = getattr(conf, 'DEFAULT_' + fieldname.upper())
                except AttributeError:
                    raise AttributeError("Failed to find '%(value)s' in "
                            '%(fieldname)s_MAP and DEFAULT_%(fieldname)s is not set' %
                            {'value': value, 'fieldname': fieldname.upper()})
            result[fieldname] = {'name': mapped_value}
    if conf.CUSTOM_FIELD:
        result[conf.CUSTOM_FIELD[0]] = conf.CUSTOM_FIELD[1]
    if conf.CUSTOM_FIELD_MAP:
        for sourcename in conf.CUSTOM_FIELD_MAP.keys():
            targetname = conf.CUSTOM_FIELD_MAP[sourcename]
            value = getattr(fields, sourcename, None)
            if value:
                result[targetname] = value
    return result


_g_epic_map = {}

def _set_epic_link(dest_issue, source_issue, conf, source_jira, dest_jira):
    source_epic_key = getattr(source_issue.fields, conf.SOURCE_EPIC_LINK_FIELD_ID)
    if not source_epic_key:
        return
    global _g_epic_map
    if source_epic_key not in _g_epic_map:
        target_epic = _already_imported(conf, dest_jira, source_epic_key)
        if target_epic:
            print('epic {} has already been imported, skipping...'.format(source_epic_key), end=' ')
            target_epic = target_epic[0]
        else:
            print('importing epic {} ...'.format(source_epic_key), end=' ')
            source_epic = source_jira.issue(source_epic_key)
            epic_fields = _get_dest_issue_fields(source_epic.fields, conf)
            epic_fields[conf.TARGET_EPIC_NAME_FIELD_ID] = getattr(
                    source_epic.fields, conf.SOURCE_EPIC_NAME_FIELD_ID)
            _add_source_jira_issue_key(conf, epic_fields, source_epic_key)
            target_epic = dest_jira.create_issue(fields=epic_fields)
        _g_epic_map[source_epic_key] = target_epic
    target_epic = _g_epic_map[source_epic_key]
    dest_jira.add_issues_to_epic(target_epic.key, [dest_issue.key])
    print('linked to epic', target_epic.key, '...', end=' ')


def _set_status(dest_issue, source_issue, conf, dest_jira):
    # Do nothing if status transitions are disabled.
    if not conf.STATUS_TRANSITIONS:
        return

    issue_type = dest_issue.fields.issuetype.name
    status_name = source_issue.fields.status.name

    transitions = None
    transition_map = getattr(conf, "STATUS_TRANSITIONS_ISSUETYPE", None)
    if transition_map:
        if issue_type in transition_map:
            transition_map = transition_map[issue_type]
        else:
            transition_map = None
    if not transition_map:
        transition_map = conf.STATUS_TRANSITIONS

    transitions = transition_map[status_name]
    if not transitions:
        return
    # Allow single string and WithResolution values by converting them to a tuple.
    if isinstance(transitions, str) or isinstance(transitions, conf.WithResolution):
        transitions = (transitions,)

    for transition_name in transitions:
        if isinstance(transition_name, conf.WithResolution):
            resolution = conf.RESOLUTION_MAP[source_issue.fields.resolution.name]
            dest_jira.transition_issue(dest_issue, transition_name.transition_name,
                    fields={'resolution': {'name': resolution}})
        else:
            dest_jira.transition_issue(dest_issue, transition_name)


def _add_comments(issue, jira, comments):
    for comment in comments:
        jira.add_comment(issue, u"*Comment by {0}*:\n{1}"
                .format(comment.author.displayName, comment.body))


def _add_attachments(issue, jira, attachments):
    for attachment in attachments:
        with BytesIO() as buf:
            for chunk in attachment.iter_content():
                buf.write(chunk)
            jira.add_attachment(issue,
                    filename=_normalize_filename(attachment.filename),
                    attachment=buf)


def _normalize_filename(value):
    return unicodedata.normalize('NFKD', value).encode('ascii',
            'ignore').decode('ascii')


# -------------------------------------
# TODO:
# - more mappings from http://stackoverflow.com/a/26043914/258772
# - components, fixVersions (use create_version())
# - estimates and timelogs
#   - tried, no luck, even though seems to have been working:
#     https://answers.atlassian.com/questions/211138/defining-original-estimation-value-via-api

# Not doing:
# - keep original key: JIRA does not support this
# - comment authors map -- cannot change comment authors easily, Google for
#   reasons
