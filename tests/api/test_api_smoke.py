import uuid

def test_api_login_returns_admin(api):
    assert api.me["username"] == "qa_admin"

def test_create_and_archive_channel(api, team):
    suffix = uuid.uuid4().hex[:8]
    channel = api.create_channel(team["id"], f"auto-{suffix}", f"Auto {suffix}")
    assert channel["team_id"] == team["id"]
    api.archive_channel(channel["id"])