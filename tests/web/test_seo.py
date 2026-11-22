import os
import xml.etree.ElementTree as ET

from fastapi.testclient import TestClient

from web import seo
from web.tutorials import TUTORIALS


def client() -> TestClient:
    os.environ.setdefault("ADMIN_PASSWORD", "test-password")
    os.environ.setdefault("ADMIN_USERNAME", "admin")
    from web.api import app

    return TestClient(app)


def test_robots_keeps_the_editor_out_and_names_the_sitemap() -> None:
    body = client().get("/robots.txt").text
    assert "Disallow: /blog/editor" in body
    assert "Sitemap: https://atle.dev/sitemap.xml" in body


def test_sitemap_lists_the_pages_and_every_tutorial() -> None:
    resp = client().get("/sitemap.xml")
    assert resp.headers["content-type"].startswith("application/xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [loc.text for loc in ET.fromstring(resp.text).findall("s:url/s:loc", ns)]
    assert "https://atle.dev/blog" in locs
    assert all(f"https://atle.dev{t.href}" in locs for t in TUTORIALS)


def test_a_tutorial_page_gets_its_description_and_preview_tags() -> None:
    tutorial = TUTORIALS[0]
    body = client().get(tutorial.href).text
    assert '<meta name="description"' in body
    assert f'<link rel="canonical" href="https://atle.dev{tutorial.href}">' in body
    assert body.count("</head>") == 1


def test_pages_have_their_own_description_and_canonical_url() -> None:
    body = client().get("/blog").text
    assert "Tutorials written by AgentSwarm" in body
    assert '<link rel="canonical" href="https://atle.dev/blog">' in body
    assert '<meta property="og:title" content="Writing · Andreas Atle">' in body


def test_excerpt_takes_the_first_paragraph_and_cuts_at_a_word() -> None:
    assert seo.excerpt("# Title\n\nA **short** first [para](x).\n\nSecond.") == "A short first para."
    long = seo.excerpt("word " * 100)
    assert len(long) <= seo.DESCRIPTION_LIMIT and long.endswith("word…")


def test_a_page_with_a_description_is_left_alone() -> None:
    page = '<html><head><meta name="description" content="x"></head></html>'
    assert seo.with_head_tags(page, "/p", None) == page
