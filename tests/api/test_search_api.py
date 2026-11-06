import uuid

import pytest

from utils.api_client import MattermostAPI


@pytest.mark.tc("MMQA-T66")
def test_search_excludes_private_channel_for_non_member(api, team, make_user, base_url):
    term = f"zebrafish{uuid.uuid4().hex[:8]}"
    private = api.create_channel(
        team["id"], f"priv-{uuid.uuid4().hex[:8]}", "Private search", private=True
    )
    try:
        api.create_post(private["id"], f"{term} secret")
        username, password = make_user()
        member_api = MattermostAPI(base_url, username, password)

        # control: the creator is a member, so the term must be searchable
        assert len(api.search_posts(team["id"], term)) == 1

        # a non-member must get nothing
        assert member_api.search_posts(team["id"], term) == []

        # once added to the channel, the same search finds it
        api.add_to_channel(private["id"], api.get_user(username)["id"])
        assert len(member_api.search_posts(team["id"], term)) == 1
    finally:
        api.archive_channel(private["id"])


@pytest.mark.tc("MMQA-T67")
def test_search_reflects_edit_and_delete(api, team, message_channel):
    old = f"alphaterm{uuid.uuid4().hex[:8]}"
    new = f"betaterm{uuid.uuid4().hex[:8]}"
    post = api.create_post(message_channel["id"], f"{old} first draft")
    assert [p["id"] for p in api.search_posts(team["id"], old)] == [post["id"]]

    api.edit_post(post["id"], f"{new} final draft")
    assert api.search_posts(team["id"], old) == []
    assert [p["id"] for p in api.search_posts(team["id"], new)] == [post["id"]]

    api.delete_post(post["id"])
    assert api.search_posts(team["id"], new) == []