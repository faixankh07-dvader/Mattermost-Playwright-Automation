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

    def list_public_channels(self, team_id: str) -> list:
        r = self.session.get(
            f"{self.base}/teams/{team_id}/channels",
            params={"per_page": 200},
        )
        r.raise_for_status()
        return r.json()

    def create_user(self, username: str, password: str) -> dict:
        r = self.session.post(
            f"{self.base}/users",
            json={"email": f"{username}@test.local", "username": username, "password": password},
        )
        r.raise_for_status()
        return r.json()

    def add_to_team(self, team_id: str, user_id: str) -> dict:
        r = self.session.post(
            f"{self.base}/teams/{team_id}/members",
            json={"team_id": team_id, "user_id": user_id},
        )
        r.raise_for_status()
        return r.json()

    def set_team_admin(self, team_id: str, user_id: str, is_admin: bool) -> None:
        r = self.session.put(
            f"{self.base}/teams/{team_id}/members/{user_id}/schemeRoles",
            json={"scheme_user": True, "scheme_admin": is_admin},
        )
        r.raise_for_status()

    def deactivate_user(self, user_id: str) -> None:
        r = self.session.delete(f"{self.base}/users/{user_id}")
        r.raise_for_status()

    def get_team_member(self, team_id: str, user_id: str) -> dict:
        r = self.session.get(f"{self.base}/teams/{team_id}/members/{user_id}")
        r.raise_for_status()
        return r.json()

    def create_post(self, channel_id: str, message: str) -> dict:
        r = self.session.post(
            f"{self.base}/posts",
            json={"channel_id": channel_id, "message": message},
        )
        r.raise_for_status()
        return r.json()

    def get_post(self, post_id: str) -> dict:
        r = self.session.get(f"{self.base}/posts/{post_id}")
        r.raise_for_status()
        return r.json()

    def get_channel_posts(self, channel_id: str) -> list:
        r = self.session.get(
            f"{self.base}/channels/{channel_id}/posts",
            params={"per_page": 200},
        )
        r.raise_for_status()
        data = r.json()
        return [data["posts"][post_id] for post_id in data["order"]]

    def get_user_by_id(self, user_id: str) -> dict:
        r = self.session.get(f"{self.base}/users/{user_id}")
        r.raise_for_status()
        return r.json()

    def set_channel_admin(self, channel_id: str, user_id: str, is_admin: bool) -> None:
        r = self.session.put(
            f"{self.base}/channels/{channel_id}/members/{user_id}/schemeRoles",
            json={"scheme_user": True, "scheme_admin": is_admin},
        )
        r.raise_for_status()

    def search_posts(self, team_id: str, terms: str) -> list:
        r = self.session.post(
            f"{self.base}/teams/{team_id}/posts/search",
            json={"terms": terms, "is_or_search": False},
        )
        r.raise_for_status()
        data = r.json()
        order = data.get("order") or []
        posts = data.get("posts") or {}
        return [posts[post_id] for post_id in order]

    def edit_post(self, post_id: str, message: str) -> dict:
        r = self.session.put(f"{self.base}/posts/{post_id}/patch", json={"message": message})
        r.raise_for_status()
        return r.json()

    def delete_post(self, post_id: str) -> None:
        r = self.session.delete(f"{self.base}/posts/{post_id}")
        r.raise_for_status()