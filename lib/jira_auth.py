from __future__ import print_function

import json
from pathlib import Path

from jira.client import JIRA


def create_jira_client(jira_config):
    normalized_config = dict(jira_config)
    normalized_config = _load_external_cookie_config(normalized_config)

    options = {'server': normalized_config['server']}
    if 'verify' in normalized_config:
        options['verify'] = normalized_config['verify']
    if 'headers' in normalized_config:
        options['headers'] = normalized_config['headers']
    if 'cookies' in normalized_config:
        options['cookies'] = normalized_config['cookies']

    auth_config = _normalize_auth_config(normalized_config)
    jira_kwargs = _build_jira_kwargs(auth_config, normalized_config)
    return JIRA(options, **jira_kwargs)


def _normalize_auth_config(jira_config):
    if 'auth' in jira_config:
        auth_config = dict(jira_config['auth'])
        auth_config.setdefault('user', jira_config.get('user'))
        auth_config.setdefault('password', jira_config.get('password'))
        auth_config.setdefault('access_token', jira_config.get('access-token'))
        if 'type' not in auth_config:
            if auth_config.get('password'):
                auth_config['type'] = 'basic'
            elif auth_config.get('access_token'):
                auth_config['type'] = 'jira_token'
            elif jira_config.get('cookies'):
                auth_config['type'] = 'cookie_session'
        return auth_config

    if 'password' in jira_config:
        return {
            'type': 'basic',
            'user': jira_config.get('user'),
            'password': jira_config.get('password'),
        }
    if 'access-token' in jira_config:
        return {
            'type': 'jira_token',
            'access_token': jira_config.get('access-token'),
        }
    if jira_config.get('cookies'):
        return {'type': 'cookie_session'}

    raise RuntimeError(
        "Configuration does not contain supported authentication settings. "
        "Use legacy 'password'/'access-token' keys or configure JIRA['auth']."
    )


def _build_jira_kwargs(auth_config, jira_config):
    auth_type = auth_config.get('type')
    if auth_type == 'basic':
        return {'basic_auth': (auth_config['user'], auth_config['password'])}
    if auth_type == 'jira_token':
        return {'token_auth': auth_config['access_token']}
    if auth_type == 'cookie_session':
        if not jira_config.get('cookies'):
            raise RuntimeError("Cookie-session authentication requires 'cookies' or 'cookie_file'.")
        return {'validate': True}

    raise RuntimeError(
        "Unsupported Jira auth type {!r}. Supported values: basic, jira_token, cookie_session."
        .format(auth_type)
    )


def _load_external_cookie_config(jira_config):
    cookie_file = jira_config.get('cookie_file')
    if not cookie_file:
        return jira_config

    cookie_path = Path(cookie_file).expanduser()
    if not cookie_path.exists():
        raise RuntimeError("Cookie file not found: {0}".format(cookie_path))

    cookies = _parse_cookie_file(cookie_path)
    merged_config = dict(jira_config)
    if jira_config.get('cookies'):
        merged_cookies = dict(cookies)
        merged_cookies.update(jira_config['cookies'])
        merged_config['cookies'] = merged_cookies
    else:
        merged_config['cookies'] = cookies
    return merged_config


def _parse_cookie_file(cookie_path):
    text = cookie_path.read_text()
    stripped = text.lstrip()
    if stripped.startswith('{') or stripped.startswith('['):
        return _parse_json_cookie_export(json.loads(text))
    return _parse_netscape_cookie_file(text)


def _parse_json_cookie_export(payload):
    if isinstance(payload, dict):
        if 'cookies' in payload:
            payload = payload['cookies']
        else:
            return {str(name): str(value) for name, value in payload.items()}

    if not isinstance(payload, list):
        raise RuntimeError("Unsupported JSON cookie export format.")

    cookies = {}
    for item in payload:
        if not isinstance(item, dict):
            raise RuntimeError("Unsupported JSON cookie entry: {0!r}".format(item))
        name = item.get('name')
        value = item.get('value')
        if name is None or value is None:
            continue
        cookies[str(name)] = str(value)
    return cookies


def _parse_netscape_cookie_file(text):
    cookies = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        parts = stripped.split('\t')
        if len(parts) != 7:
            raise RuntimeError("Unsupported Netscape cookie line: {0}".format(line))
        cookies[parts[5]] = parts[6]
    return cookies
