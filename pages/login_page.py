import re
from playwright.sync_api import Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.username = page.get_by_test_id("login-id-input")
        self.password = page.get_by_role("textbox", name="Password")
        self.submit = page.get_by_role("button", name="Log in")
        self.error = page.get_by_text("The email/username or password is invalid.")

    def open(self):
        self.page.goto("/")
        self.page.wait_for_url(re.compile(r"/(landing|login)"))
        if "landing" in self.page.url:
            self.page.get_by_role("link", name="View in Browser").click()

    def login(self, username: str, password: str):
        self.username.fill(username)
        self.password.fill(password)
        self.submit.click()