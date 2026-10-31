import os
import re
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

load_dotenv()
USER = os.environ["MM_ADMIN_USER"]
PASSWORD = os.environ["MM_ADMIN_PASS"]


def login(page: Page, username: str, password: str):
    page.goto("/")
    page.wait_for_url(re.compile(r"/(landing|login)"))
    if "landing" in page.url:
        page.get_by_role("link", name="View in Browser").click()
    page.get_by_test_id("login-id-input").fill(username)
    page.get_by_role("textbox", name="Password").fill(password)
    page.get_by_role("button", name="Log in").click()             # replace with codegen output


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
    page.goto("/login")
    page.get_by_role("button", name="Log in").click(force=True)
    expect(page).to_have_url(re.compile(r"/login"))


@pytest.mark.tc("MMQA-T16")
def test_logout_ends_session(page: Page):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    page.get_by_role("button", name="User's account menu").click()
    page.get_by_role("menuitem", name="Log out").click()
    expect(page).to_have_url(re.compile(r"/login"))
    page.go_back()
    expect(page).not_to_have_url(re.compile(r"/channels/"))


@pytest.mark.tc("MMQA-T17")
def test_session_persists_after_refresh(page: Page):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    page.reload()
    expect(page).to_have_url(re.compile(r"/channels/"))