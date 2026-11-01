import re
from playwright.sync_api import Page

class ChannelPage:
    def __init__(self, page: Page):
        self.page = page
        self.add_channels = page.get_by_role("button", name="Add Channels")
        self.create_new_channel = page.get_by_text("Create new channel")
        self.channel_name = page.get_by_role("textbox", name="Channel name")
        self.public_option = page.get_by_role("button", name="Globe Circle Solid Icon")
        self.create_button = page.get_by_role("button", name="Create channel")

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