"""Authoritative single-writer interface for post revision state."""

from typing import Any


class PostRevisionWriter:
    """Single-writer authority for loading and revising blog posts.

    This module defines the authoritative interface only; it does not perform
    I/O or integrate with application services yet.
    """

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
        raise NotImplementedError

    def get_current_state(self, post_id: str) -> Any:
        """Return the current authoritative state for a post."""
        raise NotImplementedError

    def get_revision_log(self, post_id: str) -> Any:
        """Return the authoritative revision log for a post."""
        raise NotImplementedError
