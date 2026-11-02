import uuid

import pytest
from playwright.sync_api import expect

from pages.message_panel import MessagePanel


@pytest.mark.tc("MMQA-T50")
def test_edit_own_message(admin_page, api, team, message_channel):
    post = api.create_post(message_channel["id"], "original message")
    panel = MessagePanel(admin_page)
    panel.open_channel(team["name"], message_channel["name"])

    panel.edit_post(post["id"], "original message", "edited message")

    expect(panel.post_text("edited message")).to_be_visible()
    expect(panel.channel_view.get_by_role("button", name="Edited")).to_be_visible()
    expect(panel.post_text("original message")).to_have_count(0)
    assert api.get_post(post["id"])["message"] == "edited message"


@pytest.mark.tc("MMQA-T51")
def test_delete_own_message(admin_page, api, team, message_channel):
    post = api.create_post(message_channel["id"], "message to delete")
    panel = MessagePanel(admin_page)
    panel.open_channel(team["name"], message_channel["name"])

    panel.delete_post(post["id"], "message to delete")

    expect(panel.post_text("message to delete")).to_have_count(0)
    remaining = [p["id"] for p in api.get_channel_posts(message_channel["id"])]
    assert post["id"] not in remaining


@pytest.mark.tc("MMQA-T48")
@pytest.mark.parametrize(
    "text, should_post",
    [
        pytest.param("", False, id="empty"),
        pytest.param("   ", False, id="whitespace"),
        pytest.param("a" * 16383, True, id="max-length"),
        pytest.param("a" * 16384, False, id="over-max"),
    ],
)
def test_message_length_boundaries(admin_page, api, team, message_channel, text, should_post):
    panel = MessagePanel(admin_page)
    panel.open_channel(team["name"], message_channel["name"])

    panel.input.fill(text)
    panel.input.press("Enter")

    # Send a sentinel afterwards. Once it shows up, anything the first
    # attempt was going to post has already arrived.
    sentinel = f"sentinel-{uuid.uuid4().hex[:6]}"
    panel.input.fill("")
    panel.send(sentinel)
    expect(panel.post_text(sentinel)).to_be_visible()

    user_posts = [p for p in api.get_channel_posts(message_channel["id"]) if p["type"] == ""]
    assert len(user_posts) == (2 if should_post else 1)