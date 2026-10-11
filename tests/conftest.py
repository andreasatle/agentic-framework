"""Shared test setup: the same environment the app gets at startup.

The app loads `.env` in src/web/bootstrap.py before anything else; several modules (e.g. apps.blog.paths) read
settings such as AGENTIC_BLOG_POSTS_ROOT when they are imported, so the tests load it first too. Variables
already set in the shell win, so CI or a one-off run can point elsewhere.
"""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
