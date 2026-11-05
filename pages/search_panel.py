import re

from playwright.sync_api import Page


class SearchPanel:
    def __init__(self, page: Page):
        self.page = page
        self.open_button = page.get_by_role("button", name=re.compile(r"Search$"))
        self.box = page.get_by_role("searchbox", name="Search messages")
        self.jump_links = page.get_by_role("link", name="Jump")

    def search(self, query: str):
        self.open_button.click()
        self.box.fill(query)
        self.box.press("Enter")