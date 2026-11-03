import re

import pytest
from pages.channel_page import ChannelPage
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

    expect(page).to_have_url(re.compile(r"/channels/"), timeout=15000)
    expect(page).not_to_have_url(re.compile(r"/admin_console"))

@pytest.mark.tc("MMQA-T21")
def test_system_admin_sees_system_console_in_menu(admin_page, team):
    admin_page.goto(f"/{team['name']}/channels/town-square")
    admin_page.get_by_role("button", name="Product switch menu").click()
    link = admin_page.get_by_role("link", name="System Console")
    expect(link).to_be_visible()
    link.click()
    expect(admin_page).to_have_url(re.compile(r"/admin_console"))


@pytest.mark.parametrize(
    "team_admin",
    [
        pytest.param(True, marks=pytest.mark.tc("MMQA-T28"), id="team_admin"),
        pytest.param(False, marks=pytest.mark.tc("MMQA-T32"), id="member"),
    ],
)
def test_non_admin_menu_hides_system_console(team_admin, team, make_user, auth_state, new_context):
    username, password = make_user(team_admin=team_admin)
    context = new_context(storage_state=auth_state(username, password))
    page = context.new_page()

    page.goto(f"/{team['name']}/channels/town-square")
    ChannelPage(page).dismiss_onboarding()

    menu_button = page.get_by_role("button", name="Product switch menu")
    menu_button.click()

    page.goto("/admin_console")

    expect(page).to_have_url(re.compile(r"/channels/"), timeout=15000)
    expect(page).not_to_have_url(re.compile(r"/admin_console"))