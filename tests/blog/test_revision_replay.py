import hashlib
from pathlib import Path

from apps.blog.post_revision_writer import PostRevisionWriter
from apps.blog.storage import create_post, read_post_content, _replay_post_content


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_content(chunks: list[str]) -> str:
    return "\n\n".join(chunks)


def _write_snapshots(
    posts_root: Path,
    post_id: str,
    revision_id: int,
    chunks: list[str],
) -> None:
    revisions_dir = posts_root / post_id / "revisions"
    revisions_dir.mkdir(parents=True, exist_ok=True)
    for index, text in enumerate(chunks):
        snapshot_path = revisions_dir / f"{revision_id}_{index}.md"
        snapshot_path.write_text(text)


def test_replay_matches_current_content(tmp_path: Path) -> None:
    posts_root = tmp_path / "posts"
    initial_chunks = ["Alpha", "Beta"]
    initial_content = _build_content(initial_chunks)
    post_id, _ = create_post(
        title=None,
        author="test",
        intent={},
        content=initial_content,
        posts_root=str(posts_root),
    )
    writer = PostRevisionWriter(posts_root=str(posts_root))

    chunks_v1 = ["Alpha v1", "Beta v1"]
    content_v1 = _build_content(chunks_v1)
    revision_id_1 = writer.apply_delta(
        post_id,
        actor={"type": "human", "id": "tester"},
        delta_type="content_chunks_modified",
        delta_payload={
            "changed_chunks": list(range(len(chunks_v1))),
            "before_hash": _hash_text(initial_content),
            "after_hash": _hash_text(content_v1),
        },
    )
    _write_snapshots(posts_root, post_id, revision_id_1, chunks_v1)
    (posts_root / post_id / "content.md").write_text(content_v1)

    chunks_v2 = ["Alpha v2", "Beta v2", "Gamma v2"]
    content_v2 = _build_content(chunks_v2)
    revision_id_2 = writer.apply_delta(
        post_id,
        actor={"type": "human", "id": "tester"},
        delta_type="content_chunks_modified",
        delta_payload={
            "changed_chunks": list(range(len(chunks_v2))),
            "before_hash": _hash_text(content_v1),
            "after_hash": _hash_text(content_v2),
        },
    )
    _write_snapshots(posts_root, post_id, revision_id_2, chunks_v2)
    (posts_root / post_id / "content.md").write_text(content_v2)

    replayed = _replay_post_content(post_id, str(posts_root))
    current = (posts_root / post_id / "content.md").read_text()
    assert replayed == current
    assert replayed == content_v2


def test_rejected_delta_does_not_affect_replay(tmp_path: Path) -> None:
    posts_root = tmp_path / "posts"
    initial_chunks = ["One", "Two"]
    initial_content = _build_content(initial_chunks)
    post_id, _ = create_post(
        title=None,
        author="test",
        intent={},
        content=initial_content,
        posts_root=str(posts_root),
    )
    writer = PostRevisionWriter(posts_root=str(posts_root))

    applied_chunks = ["One applied", "Two applied"]
    applied_content = _build_content(applied_chunks)
    applied_revision_id = writer.apply_delta(
        post_id,
        actor={"type": "human", "id": "tester"},
        delta_type="content_chunks_modified",
        delta_payload={
            "changed_chunks": list(range(len(applied_chunks))),
            "before_hash": _hash_text(initial_content),
            "after_hash": _hash_text(applied_content),
        },
    )
    _write_snapshots(posts_root, post_id, applied_revision_id, applied_chunks)
    (posts_root / post_id / "content.md").write_text(applied_content)

    rejected_chunks = ["One rejected", "Two rejected"]
    rejected_content = _build_content(rejected_chunks)
    writer.apply_delta(
        post_id,
        actor={"type": "human", "id": "tester"},
        delta_type="content_chunks_modified",
        delta_payload={
            "changed_chunks": list(range(len(rejected_chunks))),
            "before_hash": _hash_text(applied_content),
            "after_hash": _hash_text(rejected_content),
        },
        status="rejected",
        reason="rejected",
    )

    replayed = _replay_post_content(post_id, str(posts_root))
    assert replayed == applied_content
    assert replayed != rejected_content


def test_read_post_content_replays_and_writes_cache(tmp_path: Path) -> None:
    posts_root = tmp_path / "posts"
    initial_chunks = ["Start"]
    initial_content = _build_content(initial_chunks)
    post_id, _ = create_post(
        title=None,
        author="test",
        intent={},
        content=initial_content,
        posts_root=str(posts_root),
    )
    writer = PostRevisionWriter(posts_root=str(posts_root))

    chunks_v1 = ["First", "Second"]
    content_v1 = _build_content(chunks_v1)
    revision_id = writer.apply_delta(
        post_id,
        actor={"type": "human", "id": "tester"},
        delta_type="content_chunks_modified",
        delta_payload={
            "changed_chunks": list(range(len(chunks_v1))),
            "before_hash": _hash_text(initial_content),
            "after_hash": _hash_text(content_v1),
        },
    )
    _write_snapshots(posts_root, post_id, revision_id, chunks_v1)

    content_path = posts_root / post_id / "content.md"
    content_path.unlink()

    replayed = read_post_content(post_id, str(posts_root))
    assert content_path.exists()
    assert replayed == content_v1
    assert _hash_text(replayed) == _hash_text(content_v1)
