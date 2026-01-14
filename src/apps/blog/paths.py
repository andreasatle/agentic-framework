"""Single canonical filesystem root for blog posts.

POSTS_ROOT is the single canonical filesystem root for all blog storage.
No other module may define, derive, or override a blog posts root.
"""

from pathlib import Path

POSTS_ROOT = Path(__file__).resolve().parent / "posts"
if not POSTS_ROOT.exists() or not POSTS_ROOT.is_dir():
    raise RuntimeError(
        f"Canonical blog posts directory missing or invalid: {POSTS_ROOT.resolve()}"
    )

__all__ = ["POSTS_ROOT"]
