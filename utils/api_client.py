import requests

class MattermostAPI:
    def __init__(self, base_url: str, username: str, password: str):
        self.base = base_url.rstrip("/") + "/api/v4"
        self.session = requests.Session()
        r = self.session.post(
            f"{self.base}/users/login",
            json={"login_id": username, "password": password},
        )
        r.raise_for_status()
        self.session.headers["Authorization"] = f"Bearer {r.headers['Token']}"
        self.me = r.json()

    def get_team(self, name: str) -> dict:
        r = self.session.get(f"{self.base}/teams/name/{name}")
        r.raise_for_status()
        return r.json()

    def get_user(self, username: str) -> dict:
        r = self.session.get(f"{self.base}/users/username/{username}")
        r.raise_for_status()
        return r.json()

    def create_channel(self, team_id: str, name: str, display_name: str, private: bool = False) -> dict:
        r = self.session.post(
            f"{self.base}/channels",
            json={
                "team_id": team_id,
                "name": name,
                "display_name": display_name,
                "type": "P" if private else "O",
            },
        )
        r.raise_for_status()
        return r.json()

    def add_to_channel(self, channel_id: str, user_id: str) -> dict:
        r = self.session.post(
            f"{self.base}/channels/{channel_id}/members",
            json={"user_id": user_id},
        )
        r.raise_for_status()
        return r.json()

    def archive_channel(self, channel_id: str) -> None:
        r = self.session.delete(f"{self.base}/channels/{channel_id}")
        r.raise_for_status()

    def get_channel_by_name(self, team_id: str, name: str) -> dict:
        r = self.session.get(f"{self.base}/teams/{team_id}/channels/name/{name}")
        r.raise_for_status()
        return r.json()

    def get_channel_member(self, channel_id: str, user_id: str) -> dict:
        r = self.session.get(f"{self.base}/channels/{channel_id}/members/{user_id}")
        r.raise_for_status()
        return r.json()