from playwright.sync_api import Page


def install_product_notice_handler(page: Page) -> None:
    """Close the 'product notices' modal whenever it blocks an action."""
    modal = page.locator(".productNotices")

    def _close():
        close_button = modal.get_by_role("button", name="Close")
        if close_button.count():
            close_button.first.click()
        else:
            page.keyboard.press("Escape")

    page.add_locator_handler(modal, _close)