import keyring

JIRA = {
    "server": "https://example.com/jira/",
    "user": "user",
    "password": keyring.get_password("system", "user")
}
