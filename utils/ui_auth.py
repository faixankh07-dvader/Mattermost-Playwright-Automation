from playwright.sync_api import Page
from pages.login_page import LoginPage


def login(page: Page, username: str, password: str):
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(username, password)