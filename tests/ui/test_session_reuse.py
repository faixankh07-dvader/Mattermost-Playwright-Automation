import re
from playwright.sync_api import expect


def test_admin_starts_logged_in(admin_page):
    admin_page.goto("/")
    expect(admin_page).to_have_url(re.compile(r"/channels/"))