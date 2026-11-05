import uuid

import pytest
from playwright.sync_api import expect

from pages.channel_page import ChannelPage
from pages.message_panel import MessagePanel
from utils.api_client import MattermostAPI




@pytest.mark.tc("MMQA-T41")
@pytest.mark.parametrize(
    "refresh",
    [
        pytest.param(False, id="live"), 
        pytest.param(True, id="after-refresh"),
    ],
)
def test_delete_option_removed_after_channel_admin_demotion(
    refresh, api, team, message_channel, make_user, auth_state, new_context
):
    username, password = make_user()
    user_id = api.get_user(username)["id"]
    api.add_to_channel(message_channel["id"], user_id)
    api.set_channel_admin(message_channel["id"], user_id, True)
    post = api.create_post(message_channel["id"], "post by admin")

    page = new_context(storage_state=auth_state(username, password)).new_page()
    panel = MessagePanel(page)
    panel.open_channel(team["name"], message_channel["name"])
    ChannelPage(page).dismiss_onboarding()
    delete_item = page.get_by_test_id(f"delete_post_{post['id']}")

    # precondition: a Channel Admin is offered Delete on someone else's post
    panel.open_post_menu(post["id"], "post by admin")
    expect(delete_item).to_be_visible()
    page.keyboard.press("Escape")

    api.set_channel_admin(message_channel["id"], user_id, False)
    if refresh:
        page.reload()
        ChannelPage(page).dismiss_onboarding()

    panel.open_post_menu(post["id"], "post by admin")
    expect(delete_item).to_have_count(0, timeout=10000)


@pytest.mark.tc("MMQA-T1")
@pytest.mark.tc("MMQA-T52")
@pytest.mark.parametrize(
    "refresh",
    [
        pytest.param(False, id="live"),
        pytest.param(True, id="after-refresh"),
    ],
)
def test_message_from_other_user_appears_in_open_channel(
    refresh, api, team, message_channel, make_user, auth_state, new_context, base_url
):
    receiver, receiver_pw = make_user()
    sender, sender_pw = make_user()
    for name in (receiver, sender):
        api.add_to_channel(message_channel["id"], api.get_user(name)["id"])

    page = new_context(storage_state=auth_state(receiver, receiver_pw)).new_page()
    panel = MessagePanel(page)
    panel.open_channel(team["name"], message_channel["name"])
    ChannelPage(page).dismiss_onboarding()
    expect(panel.input).to_be_visible()  # channel loaded, then left idle

    text = f"live-{uuid.uuid4().hex[:8]}"
    MattermostAPI(base_url, sender, sender_pw).create_post(message_channel["id"], text)

    if refresh:
        page.reload()
        ChannelPage(page).dismiss_onboarding()
    expect(panel.post_text(text)).to_be_visible(timeout=10000)