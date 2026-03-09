import keyring

JIRA = {
    "server": "https://example.com/jira/",
    "user": "user",
    "password": keyring.get_password("system", "user"),
    # Optional for untrusted TLS:
    # "verify": False,
    #
    # For a browser-exported Jira session instead of password auth, use:
    #
    # "auth": {
    #     "type": "cookie_session",
    # },
    # "cookie_file": "~/Downloads/jira-cookies.json",
    #
    # The cookie file may be:
    # - a simple JSON object: {"cookie_name": "cookie_value"}
    # - a browser-extension JSON export with [{"name": "...", "value": "..."}]
    # - a Netscape cookies.txt export
}
