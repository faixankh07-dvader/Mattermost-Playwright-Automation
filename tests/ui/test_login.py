import os
import re
import pytest
import uuid
import requests
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
    login_page = LoginPage(page)
    login_page.open()
    expect(login_page.username).to_be_visible()
    login_page.username.press("Enter")
    expect(page.get_by_text("Please enter your email or username")).to_be_visible()
    expect(page).to_have_url(re.compile(r"/login"))

@pytest.mark.tc("MMQA-T16")
def test_logout_ends_session(page: Page, base_url):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    protected_url = page.url

    page.get_by_role("button", name="User's account menu").click()
    page.get_by_role("menuitem", name="Log out").click()
    expect(page).to_have_url(re.compile(r"/login"))

    # server side: the old session no longer works
    assert page.request.get(f"{base_url}/api/v4/users/me").status == 401

    # browser side: a protected URL in a fresh tab of the same browser context goes to login
    fresh = page.context.new_page()
    fresh.goto(protected_url)
    expect(fresh).to_have_url(re.compile(r"/login"), timeout=15000)
    expect(fresh.get_by_test_id("login-id-input")).to_be_visible(timeout=15000)

@pytest.mark.tc("MMQA-T17")
def test_session_persists_after_refresh(page: Page):
    login(page, USER, PASSWORD)
    expect(page).to_have_url(re.compile(r"/channels/"))
    page.reload()
    expect(page).to_have_url(re.compile(r"/channels/"))

@pytest.mark.tc("MMQA-T13")
def test_login_fails_for_nonexistent_user(page: Page, base_url, make_user):
    ghost = f"nouser{uuid.uuid4().hex[:8]}"
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(ghost, "Whatever@123")
    expect(login_page.error).to_be_visible()
    expect(page).to_have_url(re.compile(r"/login"))

    # the server must not reveal whether the account exists
    real_user, _ = make_user()
    api_url = f"{base_url}/api/v4/users/login"
    nonexistent = requests.post(api_url, json={"login_id": ghost, "password": "Whatever@123"})
    wrong_password = requests.post(api_url, json={"login_id": real_user, "password": "Wrong@12345"})
    assert nonexistent.status_code == wrong_password.status_code == 401
    assert nonexistent.json()["id"] == wrong_password.json()["id"]