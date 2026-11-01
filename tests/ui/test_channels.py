import re
import uuid

import pytest
import requests
from playwright.sync_api import expect

from pages.channel_page import ChannelPage
from utils.api_client import MattermostAPI


@pytest.fixture
def channel_name():
    return f"e2e-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def cleanup_channel(api, team):
    names = []
    yield names
    for name in names:
        try:
            channel = api.get_channel_by_name(team["id"], name)
            api.archive_channel(channel["id"])
        except requests.HTTPError:
            pass  # channel kabhi bana hi nahi, cleanup ki zaroorat nahi


@pytest.mark.tc("MMQA-T42")
def test_create_public_channel(admin_page, api, team, channel_name, cleanup_channel, make_user, base_url):
    cleanup_channel.append(channel_name)
    channel = ChannelPage(admin_page)

    channel.open_team(team["name"])
    channel.create_public_channel(channel_name)

    expect(admin_page).to_have_url(re.compile(rf"/channels/{channel_name}$"))
    expect(channel.sidebar_item(channel_name)).to_be_visible()

    admin_page.reload()
    expect(channel.sidebar_item(channel_name)).to_be_visible()

    created = api.get_channel_by_name(team["id"], channel_name)
    assert created["type"] == "O"  # O = public
    member = api.get_channel_member(created["id"], api.me["id"])
    assert member["scheme_admin"] is True  # creator Channel Admin banta hai

    username, password = make_user()
    member_api = MattermostAPI(base_url, username, password)
    visible = [c["name"] for c in member_api.list_public_channels(team["id"])]
    assert channel_name in visible