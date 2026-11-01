import os
import re
import uuid

import pytest
import requests
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import MattermostAPI
from utils.ui_auth import login

ADMIN_USER = os.environ["MM_ADMIN_USER"]
ADMIN_PASS = os.environ["MM_ADMIN_PASS"]


# ---------- API fixtures (from Step 2) ----------

@pytest.fixture(scope="session")
def api(base_url):
    return MattermostAPI(base_url, ADMIN_USER, ADMIN_PASS)


@pytest.fixture(scope="session")
def team(api):
    return api.get_team(os.environ["MM_TEAM"])


# ---------- UI session fixtures (Step 3) ----------

@pytest.fixture(scope="session")
def auth_state(browser, base_url, tmp_path_factory):
    """Log in once per user via the UI and cache the saved session."""
    cache = {}

    def _get(username: str, password: str) -> str:
        if username not in cache:
            context = browser.new_context(base_url=base_url)
            page = context.new_page()
            login(page, username, password)
            page.wait_for_url(re.compile(r"/channels/"))
            path = tmp_path_factory.getbasetemp() / f"{username}.json"
            context.storage_state(path=str(path))
            context.close()
            cache[username] = str(path)
        return cache[username]

    return _get


@pytest.fixture
def admin_page(new_context, auth_state):
    context = new_context(storage_state=auth_state(ADMIN_USER, ADMIN_PASS))
    return context.new_page()

@pytest.fixture
def make_user(api, team):
    created = []

    def _make(team_admin: bool = False):
        username = f"auto{uuid.uuid4().hex[:8]}"
        password = "Auto@12345"
        user = api.create_user(username, password)
        api.add_to_team(team["id"], user["id"])
        if team_admin:
            api.set_team_admin(team["id"], user["id"], True)
        created.append(user["id"])
        return username, password

    yield _make

    for user_id in created:
        try:
            api.deactivate_user(user_id)
        except requests.HTTPError:
            pass