"""Authoritative single-writer interface for post revision state."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps.blog.storage import next_revision_id


class PostRevisionWriter:
    """Single-writer authority for loading and revising blog posts.

    This module centralizes revision recording and content updates under a
    single-writer authority.
    """

    def __init__(self, posts_root: str = "posts") -> None:
        self._posts_root = posts_root

    def load_post(self, post_id: str) -> Any:
        """Load a post into the writer's authority context for revision."""
        raise NotImplementedError

    def apply_delta(
        self,
        post_id: str,
        *,
        actor: Any,
        delta_type: str,
        delta_payload: dict,
        reason: str | None = None,
    ) -> Any:
        """Apply a delta under single-writer authority and record intent."""
        revision_id = next_revision_id(post_id, self._posts_root)
        status = delta_payload.get("status", "applied")

        record_payload = dict(delta_payload)
        content = record_payload.pop("_content", None)
        snapshot_chunks = record_payload.pop("_snapshot_chunks", None)

        revision_entry: dict[str, Any] = {
            "revision_id": revision_id,
            "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "delta_type": delta_type,
            "delta_payload": record_payload,
            "actor": actor,
            "status": status,
        }
        if reason is not None:
            revision_entry["reason"] = reason

        post_dir = Path(self._posts_root) / post_id
        meta_path = post_dir / "meta.yaml"
        if meta_path.exists():
            meta_payload = yaml.safe_load(meta_path.read_text()) or {}
            if not isinstance(meta_payload, dict):
                raise ValueError(f"Invalid meta.yaml for post {post_id}")
        else:
            meta_payload = {}

        revisions = meta_payload.get("revisions")
        if revisions is None:
            revisions = []
        elif not isinstance(revisions, list):
            raise ValueError(f"Invalid revisions for post {post_id}")

        revisions.append(revision_entry)
        meta_payload["revisions"] = revisions
        meta_path.write_text(yaml.safe_dump(meta_payload, sort_keys=False, default_flow_style=False))

        if status != "rejected" and content is not None:
            content_path = post_dir / "content.md"
            content_path.write_text(content)

        if status != "rejected" and snapshot_chunks:
            revisions_dir = post_dir / "revisions"
            revisions_dir.mkdir(exist_ok=True)
            for snapshot in snapshot_chunks:
                index = snapshot.get("index")
                text = snapshot.get("text")
                if not isinstance(index, int) or not isinstance(text, str):
                    raise ValueError("Invalid snapshot chunk payload")
                snapshot_path = revisions_dir / f"{revision_id}_{index}.md"
                snapshot_path.write_text(text)

        return revision_id

    def get_current_state(self, post_id: str) -> Any:
        """Return the current authoritative state for a post."""
        raise NotImplementedError

    def get_revision_log(self, post_id: str) -> Any:
        """Return the authoritative revision log for a post."""
        raise NotImplementedError
