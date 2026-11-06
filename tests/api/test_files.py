import hashlib
import struct
import uuid
import zlib

import pytest
import requests


def _uid() -> str:
    return uuid.uuid4().hex[:8]


def make_png(width: int = 8, height: int = 8) -> bytes:
    """A small valid red PNG, built in code so no binary file is needed in the repo."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        body = struct.pack(">I", len(data)) + tag + data
        return body + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + b"\xff\x00\x00" * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


@pytest.mark.tc("MMQA-T68")
@pytest.mark.parametrize(
    "filename, content, mime, is_image",
    [
        pytest.param("red-square.png", make_png(), "image/png", True, id="image"),
        pytest.param("notes.txt", b"QA plain text document\nline two\n", "text/plain", False, id="document"),
    ],
)
def test_upload_preserves_name_type_and_content(api, message_channel, filename, content, mime, is_image):
    info = api.upload_file(message_channel["id"], filename, content, mime)
    assert info["name"] == filename
    assert info["extension"] == filename.rsplit(".", 1)[1]
    assert info["size"] == len(content)
    assert info.get("has_preview_image", False) is is_image

    post = api.create_post(message_channel["id"], "file attached", file_ids=[info["id"]])
    assert post["file_ids"] == [info["id"]]

    downloaded = api.request("GET", f"/files/{info['id']}")
    assert downloaded.status_code == 200
    assert hashlib.sha256(downloaded.content).hexdigest() == hashlib.sha256(content).hexdigest()


@pytest.fixture
def private_file(api, team):
    channel = api.create_channel(team["id"], f"files-{_uid()}", "Private files", private=True)
    content = f"secret report {_uid()}".encode()
    info = api.upload_file(channel["id"], "secret.txt", content, "text/plain")
    api.create_post(channel["id"], "see attached file", file_ids=[info["id"]])
    yield {"channel": channel, "file_id": info["id"], "content": content}
    try:
        api.archive_channel(channel["id"])
    except requests.HTTPError:
        pass


@pytest.mark.tc("MMQA-T70")
def test_removed_member_loses_file_access(api, private_file, new_user):
    _, member_id, member_api = new_user()
    api.add_to_channel(private_file["channel"]["id"], member_id)
    url = f"/files/{private_file['file_id']}"

    # control: while still a member, the direct file URL works
    allowed = member_api.request("GET", url)
    assert allowed.status_code == 200
    assert allowed.content == private_file["content"]

    api.remove_from_channel(private_file["channel"]["id"], member_id)

    denied = member_api.request("GET", url)
    assert denied.status_code == 403
    assert private_file["content"] not in denied.content


@pytest.mark.tc("MMQA-T71")
def test_never_a_member_cannot_access_file(api, private_file, new_user):
    _, member_id, member_api = new_user()
    _, _, outsider_api = new_user()
    api.add_to_channel(private_file["channel"]["id"], member_id)
    url = f"/files/{private_file['file_id']}"

    # control: a real member can open the same URL
    assert member_api.request("GET", url).status_code == 200

    denied = outsider_api.request("GET", url)
    assert denied.status_code == 403
    assert private_file["content"] not in denied.content