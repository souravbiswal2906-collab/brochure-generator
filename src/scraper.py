"""
Fetching and reading web pages.

Three things changed from the original notebook version:

1. The original had two functions, each doing its own HTTP request to the same
   URL. Every page was downloaded twice. Here one Website object downloads and
   parses once, then hands out both the text and the links.

2. The original returned raw href values, so a link written as "/careers" was
   handed straight to requests and failed. Here every link is turned into a
   full URL.

3. The original had no error handling, so one dead link crashed the whole run.
   Here a failed fetch returns None and the caller decides what to do.
"""

from __future__ import annotations

from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from . import config

# Tags that carry no readable content. Removing them before extracting text
# keeps navigation noise and CSS out of the prompt, which saves tokens.
NOISE_TAGS = ["script", "style", "img", "input", "noscript", "svg"]

# Link prefixes that are never a page we want to read.
SKIP_PREFIXES = ("mailto:", "tel:", "javascript:", "#")


class Website:
    """One web page: its title, its readable text, and the links on it."""

    def __init__(self, url: str, html: bytes | str):
        self.url = url
        soup = BeautifulSoup(html, "html.parser")

        self.title = soup.title.string.strip() if soup.title and soup.title.string else "No title found"
        self.text = self._extract_text(soup)
        self.links = self._extract_links(soup, url)

    @staticmethod
    def _extract_text(soup: BeautifulSoup) -> str:
        if not soup.body:
            return ""
        for tag in soup.body(NOISE_TAGS):
            tag.decompose()
        return soup.body.get_text(separator="\n", strip=True)

    @staticmethod
    def _extract_links(soup: BeautifulSoup, base_url: str) -> list[str]:
        links: list[str] = []
        seen: set[str] = set()

        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            if not href:
                continue
            href = href.strip()
            if href.lower().startswith(SKIP_PREFIXES):
                continue

            # urljoin turns "/careers" into "https://example.com/careers" and
            # leaves already-absolute URLs alone.
            absolute = urljoin(base_url, href)
            if urlparse(absolute).scheme not in ("http", "https"):
                continue

            # Drop the #fragment so /about and /about#team count as one page.
            absolute = absolute.split("#")[0].rstrip("/")
            if absolute and absolute not in seen:
                seen.add(absolute)
                links.append(absolute)

        return links

    def summary_text(self, max_chars: int = config.MAX_CHARS_PER_PAGE) -> str:
        """Title plus body text, trimmed to a length worth paying for."""
        return f"{self.title}\n\n{self.text}"[:max_chars]

    def __repr__(self) -> str:
        return f"<Website {self.url!r} title={self.title!r} links={len(self.links)}>"


def fetch(url: str) -> Website | None:
    """
    Download a page and return a Website, or None if it could not be fetched.

    Returning None rather than raising is a deliberate choice: when we are
    walking half a dozen links from a company site, one broken page should not
    end the run.
    """
    try:
        response = requests.get(
            url,
            headers=config.HTTP_HEADERS,
            timeout=config.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"  ! could not fetch {url} ({error.__class__.__name__})")
        return None

    return Website(url, response.content)
