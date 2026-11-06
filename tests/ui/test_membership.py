import re
import uuid

import pytest
from playwright.sync_api import expect

from pages.channel_page import ChannelPage
from utils.api_client import MattermostAPI


@pytest.mark.tc("MMQA-T45")
def test_removed_member_loses_private_channel(api, team, make_user, auth_state, new_context, base_url):
    username, password = make_user()
    member_id = api.get_user(username)["id"]
    member_api = MattermostAPI(base_url, username, password)

    suffix = uuid.uuid4().hex[:8]
    display = f"Removal {suffix}"
    channel = api.create_channel(team["id"], f"removal-{suffix}", display, private=True)
    try:
        api.add_to_channel(channel["id"], member_id)

        page = new_context(storage_state=auth_state(username, password)).new_page()
        ChannelPage(page).dismiss_onboarding()
        page.goto(f"/{team['name']}/channels/{channel['name']}")
        sidebar_link = page.get_by_role("link", name=re.compile(re.escape(display), re.IGNORECASE))
        expect(sidebar_link).to_be_visible()  # control: the member sees the channel

        api.remove_from_channel(channel["id"], member_id)

        # server side: a post after removal is rejected and never delivered
        attempt = member_api.request(
            "POST", "/posts", json={"channel_id": channel["id"], "message": "after removal"}
        )
        assert attempt.status_code == 403
        assert all(p["message"] != "after removal" for p in api.get_channel_posts(channel["id"]))

        # client side: after a refresh the channel is gone
        page.reload()
        expect(sidebar_link).to_have_count(0)
        mine = member_api.request("GET", f"/users/me/teams/{team['id']}/channels").json()
        assert channel["id"] not in [c["id"] for c in mine]
    finally:
        api.archive_channel(channel["id"])