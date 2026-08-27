"""
Tests for the scraper.

These run offline. The Website class takes HTML as an argument rather than
fetching it itself, which is precisely what makes it testable: no network, no
API key, no waiting. Splitting "get the bytes" from "understand the bytes" is
one of the main reasons the code is arranged the way it is.

Run them with:   pytest
"""

from src.scraper import Website

SAMPLE_HTML = """
<html>
  <head><title>Acme Corp</title></head>
  <body>
    <script>console.log("this should be stripped");</script>
    <style>body { color: red; }</style>
    <h1>We make anvils</h1>
    <p>Since 1949.</p>
    <a href="/about">About</a>
    <a href="/about#team">About, again</a>
    <a href="careers">Careers</a>
    <a href="https://example.com/investors">Investors</a>
    <a href="mailto:hi@acme.com">Email us</a>
    <a href="#top">Back to top</a>
    <a>No href at all</a>
  </body>
</html>
"""


def make_site() -> Website:
    return Website("https://acme.com/", SAMPLE_HTML)


def test_title_is_read():
    assert make_site().title == "Acme Corp"


def test_script_and_style_are_removed():
    text = make_site().text
    assert "console.log" not in text
    assert "color: red" not in text


def test_body_text_is_kept():
    text = make_site().text
    assert "We make anvils" in text
    assert "Since 1949." in text


def test_relative_links_become_absolute():
    links = make_site().links
    assert "https://acme.com/about" in links
    assert "https://acme.com/careers" in links


def test_absolute_links_are_left_alone():
    assert "https://example.com/investors" in make_site().links


def test_mailto_and_fragment_links_are_dropped():
    links = make_site().links
    assert not any(link.startswith("mailto:") for link in links)
    assert "https://acme.com" not in links  # the "#top" link, stripped to nothing useful


def test_duplicate_links_appear_once():
    links = make_site().links
    # /about and /about#team are the same page
    assert links.count("https://acme.com/about") == 1


def test_summary_text_respects_the_limit():
    assert len(make_site().summary_text(max_chars=20)) == 20


def test_missing_title_does_not_crash():
    site = Website("https://acme.com/", "<html><body><p>Hi</p></body></html>")
    assert site.title == "No title found"
