import re

import pytest
from playwright.sync_api import expect


@pytest.mark.tc("MMQA-T21")
def test_system_admin_can_open_system_console(admin_page):
    admin_page.goto("/admin_console")
    expect(admin_page).to_have_url(re.compile(r"/admin_console"))


@pytest.mark.parametrize(
    "team_admin",
    [
        pytest.param(True, marks=pytest.mark.tc("MMQA-T28"), id="team_admin"),
        pytest.param(False, marks=pytest.mark.tc("MMQA-T32"), id="member"),
    ],
)
def test_non_admin_cannot_open_system_console(team_admin, make_user, auth_state, new_context):
    username, password = make_user(team_admin=team_admin)
    context = new_context(storage_state=auth_state(username, password))
    page = context.new_page()

    page.goto("/admin_console")

    expect(page).not_to_have_url(re.compile(r"/admin_console"))
    expect(page).to_have_url(re.compile(r"/channels/"))