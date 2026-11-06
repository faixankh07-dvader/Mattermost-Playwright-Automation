import uuid

import pytest


def _uid() -> str:
    return uuid.uuid4().hex[:8]


@pytest.mark.tc("MMQA-T29")
def test_team_admin_can_create_and_archive_channel(team, new_user):
    _, _, team_admin_api = new_user(team_admin=True)
    channel = team_admin_api.create_channel(team["id"], f"ta-{_uid()}", "TA channel")
    assert channel["type"] == "O"

    team_admin_api.archive_channel(channel["id"])
    archived = team_admin_api.request("GET", f"/channels/{channel['id']}").json()
    assert archived["delete_at"] != 0


@pytest.mark.tc("MMQA-T30")
def test_team_admin_cannot_manage_another_team(api, new_user):
    other = api.create_team(f"other{_uid()}", "Other team")
    try:
        _, _, team_admin_api = new_user(team_admin=True)
        _, victim_id, _ = new_user()

        add = team_admin_api.request(
            "POST", f"/teams/{other['id']}/members",
            json={"team_id": other["id"], "user_id": victim_id},
        )
        assert add.status_code in (403, 404)
        patch = team_admin_api.request(
            "PUT", f"/teams/{other['id']}/patch", json={"display_name": "Hijacked"}
        )
        assert patch.status_code in (403, 404)
        assert api.request("GET", f"/teams/{other['id']}/members/{victim_id}").status_code != 200

        # control: the system admin can manage that same team
        ok = api.request("PUT", f"/teams/{other['id']}/patch", json={"display_name": "Renamed"})
        assert ok.status_code == 200
    finally:
        api.delete_team(other["id"])


@pytest.mark.tc("MMQA-T31")
def test_team_admin_can_promote_member_to_channel_admin(api, message_channel, new_user):
    _, team_admin_id, team_admin_api = new_user(team_admin=True)
    _, member_id, _ = new_user()
    for user_id in (team_admin_id, member_id):
        api.add_to_channel(message_channel["id"], user_id)

    resp = team_admin_api.request(
        "PUT", f"/channels/{message_channel['id']}/members/{member_id}/schemeRoles",
        json={"scheme_user": True, "scheme_admin": True},
    )
    assert resp.status_code == 200
    assert api.get_channel_member(message_channel["id"], member_id)["scheme_admin"] is True


@pytest.mark.tc("MMQA-T35")
def test_member_cannot_unarchive_channel(api, team, new_user):
    _, member_id, member_api = new_user()
    channel = api.create_channel(team["id"], f"arch-{_uid()}", "Archive test")
    try:
        api.add_to_channel(channel["id"], member_id)
        api.archive_channel(channel["id"])

        denied = member_api.request("POST", f"/channels/{channel['id']}/restore")
        assert denied.status_code == 403
        assert api.request("GET", f"/channels/{channel['id']}").json()["delete_at"] != 0

        # control: the system admin can restore it
        assert api.request("POST", f"/channels/{channel['id']}/restore").status_code == 200
    finally:
        api.request("DELETE", f"/channels/{channel['id']}")


@pytest.mark.tc("MMQA-T38")
def test_member_cannot_see_private_channel_they_are_not_in(api, team, new_user):
    _, _, outsider_api = new_user()
    _, insider_id, insider_api = new_user()
    private = api.create_channel(team["id"], f"priv-{_uid()}", "Private hidden", private=True)
    try:
        api.add_to_channel(private["id"], insider_id)

        # control: a member can read it and has it in their channel list
        assert insider_api.request("GET", f"/channels/{private['id']}").status_code == 200
        mine = insider_api.request("GET", f"/users/me/teams/{team['id']}/channels").json()
        assert private["id"] in [c["id"] for c in mine]

        # a non-member cannot reach it by id or by name, and it is not in their list
        assert outsider_api.request("GET", f"/channels/{private['id']}").status_code in (403, 404)
        by_name = outsider_api.request(
            "GET", f"/teams/{team['id']}/channels/name/{private['name']}"
        )
        assert by_name.status_code in (403, 404)
        theirs = outsider_api.request("GET", f"/users/me/teams/{team['id']}/channels").json()
        assert private["id"] not in [c["id"] for c in theirs]
    finally:
        api.archive_channel(private["id"])


@pytest.mark.tc("MMQA-T40")
def test_channel_admin_rights_do_not_extend_to_other_channels(api, team, message_channel, new_user):
    _, channel_admin_id, channel_admin_api = new_user()
    _, plain_id, plain_api = new_user()
    other = api.create_channel(team["id"], f"other-{_uid()}", "Other channel")
    try:
        for channel in (message_channel, other):
            for user_id in (channel_admin_id, plain_id):
                api.add_to_channel(channel["id"], user_id)
        api.set_channel_admin(message_channel["id"], channel_admin_id, True)

        control_post = api.create_post(message_channel["id"], "post for the control user")
        own_post = api.create_post(message_channel["id"], "post in the administered channel")
        other_post = api.create_post(other["id"], "post in the other channel")

        # control: a plain Member cannot delete someone else's post
        assert plain_api.request("DELETE", f"/posts/{control_post['id']}").status_code == 403
        # the Channel Admin can, in the channel they administer
        assert channel_admin_api.request("DELETE", f"/posts/{own_post['id']}").status_code == 200
        # but not in a channel where they are only a Member
        assert channel_admin_api.request("DELETE", f"/posts/{other_post['id']}").status_code == 403
    finally:
        api.archive_channel(other["id"])