import os
import re
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect, Error
from pages.login_page import LoginPage
from utils.ui_auth import login

load_dotenv()
USER = os.environ["MM_ADMIN_USER"]
PASSWORD = os.environ["MM_ADMIN_PASS"]

@pytest.mark.tc("MMQA-T11")
def test_login_with_valid_credentials(page: Page):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))


@pytest.mark.tc("MMQA-T12")
def test_login_fails_with_wrong_password(page: Page):
    login(page, USER, "WrongPassword1")
    expect(page.get_by_text(re.compile("password is invalid", re.I))).to_be_visible()
    expect(page).not_to_have_url(re.compile(r"/channels/"))

@pytest.mark.tc("MMQA-T15")
def test_login_blocked_with_empty_fields(page: Page):
    LoginPage(page).open()
    page.get_by_role("button", name="Log in").click(force=True)
    expect(page).to_have_url(re.compile(r"/login"))

@pytest.mark.tc("MMQA-T16")
def test_logout_ends_session(page: Page, base_url):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    page.get_by_role("button", name="User's account menu").click()
    page.get_by_role("menuitem", name="Log out").click()
    expect(page).to_have_url(re.compile(r"/login"))
    try:
        page.go_back()
    except Error:
        pass  # logged-out app redirects away from the cached page, aborting the navigation
    page.reload()
    expect(page).to_have_url(re.compile(r"/login"))
    expect(page.get_by_test_id("login-id-input")).to_be_visible()
    # server-side check: the old session cookie must no longer work
    assert page.request.get(f"{base_url}/api/v4/users/me").status == 401

@pytest.mark.tc("MMQA-T17")
def test_session_persists_after_refresh(page: Page):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    page.reload()
    expect(page).to_have_url(re.compile(r"/channels/"))