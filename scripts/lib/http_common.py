"""Shared HTTP session setup for scripts that talk to Forge/GitHub."""

import requests

USER_AGENT = "puppetlabs-roundup-bot/1.0"


def make_session() -> requests.Session:
    """Return a requests.Session with the project's standard User-Agent set."""
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    return session
