import re
from playwright.sync_api import Page, expect, TimeoutError as PlaywrightTimeoutError

class ChannelPage:
    def __init__(self, page: Page):
        self.page = page
        self.add_channels = page.get_by_role("button", name="Add Channels")
        self.create_new_channel = page.get_by_text("Create new channel")
        self.channel_name = page.get_by_role("textbox", name="Channel name")
        self.public_option = page.get_by_role("button", name="Globe Circle Solid Icon")
        self.create_button = page.get_by_role("button", name="Create channel")
        self.browse_channels_item = page.get_by_text("Browse channels")
        self.browse_search = page.get_by_role("textbox", name="Search Channels")
        self.onboarding_overlay = page.locator('[data-cy="onboarding-task-list-overlay"]')

    def open_team(self, team_name: str):
        self.page.goto(f"/{team_name}/channels/town-square")

    def create_public_channel(self, name: str):
        self.add_channels.click()
        self.create_new_channel.click()
        self.channel_name.fill(name)
        self.public_option.click()
        self.create_button.click()

    def sidebar_item(self, name: str):
        return self.page.get_by_role("link", name=re.compile(re.escape(name)))

    def browse_channels(self, search: str):
        self.add_channels.click()
        self.browse_channels_item.click()
        self.browse_search.fill(search)

    def browse_row(self, name: str):
        return self.page.get_by_test_id(f"ChannelRow-{name}")

    def dismiss_onboarding(self):
        """New users get an onboarding overlay that blocks clicks; close it if it shows up."""
        try:
            self.onboarding_overlay.wait_for(state="visible", timeout=5000)
        except PlaywrightTimeoutError:
            return  # existing user, no overlay
        self.onboarding_overlay.click(position={"x": 5, "y": 5})
        expect(self.onboarding_overlay).to_be_hidden()