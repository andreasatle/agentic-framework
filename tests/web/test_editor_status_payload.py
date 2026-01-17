import os
from pathlib import Path

from fastapi.testclient import TestClient

from apps.blog import storage
from apps.blog.storage import create_post


def test_editor_entry_payload_includes_status(tmp_path: Path, monkeypatch) -> None:
    os.environ["ADMIN_PASSWORD"] = "test-password"
    os.environ["ADMIN_USERNAME"] = "admin"
    import web.api
    from web.api import app

    monkeypatch.setattr(web.api, "require_admin", lambda *_: None)

    posts_root = tmp_path / "posts"
    posts_root.mkdir()
    monkeypatch.setattr(storage, "POSTS_ROOT", posts_root)

    post_id, _ = create_post(
        title="Draft post",
        author="tester",
        intent={},
        content="Hello",
    )

    client = TestClient(app)
    resp = client.get(
        f"/blog/editor/{post_id}",
        auth=("admin", "test-password"),
        headers={"accept": "text/html"},
    )
    assert resp.status_code == 200
    body = resp.text
    assert "Draft post" in body
    assert "Status:" in body
    assert "draft" in body
