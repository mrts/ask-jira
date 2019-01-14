import os

TIMEZONE = '+02'
JIRA_TIMEZONE = 'Europe/Tallinn'

HOME_DIR = os.path.expanduser('~')
CREDENTIAL_DIR = os.path.join(HOME_DIR, '.credentials')
CREDENTIAL_FILE = os.path.join(CREDENTIAL_DIR, 'ask-jira.json')
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = os.path.join(CREDENTIAL_DIR, 'client_secret.json')
APPLICATION_NAME = 'Ask JIRA'
