import os
import uuid

import pytest
import requests
from playwright.sync_api import expect

from pages.message_panel import MessagePanel
from pages.search_panel import SearchPanel
from utils.api_client import MattermostAPI


@pytest.mark.tc("MMQA-T64")
def test_basic_search_and_jump_to_message(admin_page, api, team, message_channel):
    term = f"zebrafish{uuid.uuid4().hex[:8]}"
    match_text = f"{term} release notes"
    decoy_text = f"unrelated {uuid.uuid4().hex[:8]} message"
    api.create_post(message_channel["id"], match_text)
    api.create_post(message_channel["id"], decoy_text)

    admin_page.goto(f"/{team['name']}/channels/town-square")
    search = SearchPanel(admin_page)
    search.search(term)

    expect(search.jump_links).to_have_count(1)
    expect(admin_page.get_by_text(decoy_text)).to_have_count(0)

    search.jump_links.click()
    expect(MessagePanel(admin_page).post_text(match_text)).to_be_visible()


@pytest.fixture
def search_data(api, team, message_channel, make_user, base_url):
    term = f"zebrafish{uuid.uuid4().hex[:8]}"
    other = api.create_channel(team["id"], f"srchb-{uuid.uuid4().hex[:8]}", "Search B")
    username, password = make_user()
    api.add_to_channel(message_channel["id"], api.get_user(username)["id"])

    api.create_post(message_channel["id"], f"{term} admin in a")
    MattermostAPI(base_url, username, password).create_post(message_channel["id"], f"{term} member in a")
    api.create_post(other["id"], f"{term} admin in b")

    yield {"term": term, "channel": message_channel["name"], "member": username}

    try:
        api.archive_channel(other["id"])
    except requests.HTTPError:
        pass


@pytest.mark.tc("MMQA-T65")
@pytest.mark.parametrize(
    "template, expected",
    [
        pytest.param("", 3, id="no-filter"),
        pytest.param("from:{member}", 1, id="from-member"),
        pytest.param("from:{admin}", 2, id="from-admin"),
        pytest.param("in:{channel}", 2, id="in-channel"),
        pytest.param("from:{admin} in:{channel}", 1, id="from-and-in"),
    ],
)
def test_search_filters_narrow_results(template, expected, admin_page, team, search_data):
    filters = template.format(
        admin=os.environ["MM_ADMIN_USER"],
        member=search_data["member"],
        channel=search_data["channel"],
    )
    admin_page.goto(f"/{team['name']}/channels/town-square")
    search = SearchPanel(admin_page)
    search.search(f"{filters} {search_data['term']}".strip())

    expect(search.jump_links).to_have_count(expected)