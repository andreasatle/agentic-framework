"""What search engines and link previews read: the sitemap, robots.txt, a post's description, and the head tags of
the static AgentSwarm pages.

The static pages are served as they were written (the swarm's output is never edited); the tags are added to their
<head> when they are served, from their entry in tutorials.json or essays.json.
"""

import html
import re
from datetime import date

import markdown

from web.tutorials import Tutorial

SITE = "https://atle.dev"
DESCRIPTION_LIMIT = 160

# Pages only the editor uses: kept out of search results.
PRIVATE_PREFIXES = ("/blog/editor", "/blog/edit/", "/blog/revisions", "/blog/writer")


def excerpt(text: str, limit: int = DESCRIPTION_LIMIT) -> str:
    """The first paragraph of a markdown text as plain text, cut at a word near `limit` characters."""
    rendered = markdown.markdown(text)
    for paragraph in re.findall(r"<p>(.*?)</p>", rendered, flags=re.DOTALL):
        plain = " ".join(html.unescape(re.sub(r"<[^>]+>", "", paragraph)).split())
        if plain:
            if len(plain) <= limit:
                return plain
            return plain[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:") + "…"
    return ""


def head_tags(path: str, entry: Tutorial | None) -> str:
    """Canonical URL, description and link-preview tags for a static page, from its listing entry."""
    url = SITE + path
    tags = [f'<link rel="canonical" href="{html.escape(url)}">']
    if entry is not None:
        title = html.escape(entry.title)
        description = html.escape(excerpt(entry.summary))
        tags += [
            f'<meta name="description" content="{description}">',
            '<meta property="og:type" content="article">',
            '<meta property="og:site_name" content="atle.dev">',
            f'<meta property="og:title" content="{title}">',
            f'<meta property="og:description" content="{description}">',
            f'<meta property="og:url" content="{html.escape(url)}">',
            f'<meta property="article:published_time" content="{entry.date}">',
            '<meta name="twitter:card" content="summary">',
        ]
    return "".join(tags)


def with_head_tags(page: str, path: str, entry: Tutorial | None) -> str:
    """The page with its head tags added before </head>, unless it already has a description."""
    if 'name="description"' in page or "</head>" not in page:
        return page
    return page.replace("</head>", head_tags(path, entry) + "</head>", 1)


def robots() -> str:
    lines = ["User-agent: *"]
    lines += [f"Disallow: {prefix}" for prefix in PRIVATE_PREFIXES]
    lines += ["", f"Sitemap: {SITE}/sitemap.xml", ""]
    return "\n".join(lines)


def sitemap(pages: list[tuple[str, str | None]]) -> str:
    """A sitemap of (path, last modified YYYY-MM-DD or None) pairs."""
    entries = []
    for path, modified in pages:
        entry = f"  <url><loc>{html.escape(SITE + path)}</loc>"
        if modified:
            entry += f"<lastmod>{modified}</lastmod>"
        entries.append(entry + "</url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "\n".join(entries) + "\n</urlset>\n"
    )


def day(value: object) -> str | None:
    """YYYY-MM-DD from a date, a datetime or an ISO string."""
    text = value.isoformat() if isinstance(value, date) else str(value)
    return text[:10] if re.match(r"\d{4}-\d{2}-\d{2}", text) else None
