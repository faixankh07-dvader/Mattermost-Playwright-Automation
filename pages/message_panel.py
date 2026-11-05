from playwright.sync_api import Page


class MessagePanel:
    def __init__(self, page: Page):
        self.page = page
        self.channel_view = page.get_by_test_id("channel_view")
        self.input = page.get_by_test_id("post_textbox")
        self.send_button = page.get_by_test_id("SendMessageButton")
        self.edit_box = page.get_by_test_id("edit_textbox")
        self.delete_modal = page.locator("#deletePostModal")
        self.confirm_delete = self.delete_modal.get_by_role("button", name="Delete", exact=True)

    def open_channel(self, team_name: str, channel_name: str):
        self.page.goto(f"/{team_name}/channels/{channel_name}")

    def send(self, text: str):
        self.input.fill(text)
        self.send_button.click()

    def post_text(self, text: str):
        return self.channel_view.locator("p").filter(has_text=text)

    def open_post_menu(self, post_id: str, text: str):
        self.post_text(text).hover()
        self.page.get_by_test_id(f"PostDotMenu-Button-{post_id}").click()

    def edit_post(self, post_id: str, old_text: str, new_text: str):
        self.open_post_menu(post_id, old_text)
        self.page.get_by_test_id(f"edit_post_{post_id}").click()
        self.edit_box.fill(new_text)
        self.channel_view.get_by_role("button", name="Save").click()

    def delete_post(self, post_id: str, text: str):
        self.open_post_menu(post_id, text)
        self.page.get_by_test_id(f"delete_post_{post_id}").click()
        self.confirm_delete.click()