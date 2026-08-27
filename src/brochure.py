"""
The pipeline: a URL goes in, a brochure comes out.

Four steps:
    1. Fetch the landing page and collect its links.
    2. Ask a cheap model which of those links are worth reading.
    3. Fetch those pages and stitch the text together.
    4. Ask a better model to write the brochure.

Nothing here knows whether it is being run from a terminal, a web app, or a
test. It returns text and lets the caller decide how to show it.
"""

from __future__ import annotations

from typing import Iterator

from . import config, llm, prompts, scraper


def select_relevant_links(site: scraper.Website) -> list[dict[str, str]]:
    """Step 2: let the model filter the link list down to what matters."""
    if not site.links:
        return []

    result = llm.complete_json(
        model=config.LINK_SELECTION_MODEL,
        system=prompts.LINK_SELECTION_SYSTEM,
        user=prompts.link_selection_user(site.url, site.links),
    )

    links = result.get("links", [])
    # Trust nothing that came back from a model: check the shape before use.
    valid = [
        link for link in links
        if isinstance(link, dict) and link.get("url")
    ]
    return valid[: config.MAX_LINKED_PAGES]


def gather_content(url: str) -> str:
    """Steps 1 to 3: everything up to, but not including, the writing."""
    landing = scraper.fetch(url)
    if landing is None:
        raise RuntimeError(f"Could not load {url}. Check the address and your connection.")

    print(f"Reading {landing.title}")
    parts = [f"## Landing page\n\n{landing.summary_text()}"]

    print(f"Choosing which of {len(landing.links)} links are worth reading...")
    for link in select_relevant_links(landing):
        page = scraper.fetch(link["url"])
        if page is None:
            continue
        label = link.get("type", "page")
        print(f"  + {label}: {link['url']}")
        parts.append(f"## {label}\n\n{page.summary_text()}")

    combined = "\n\n".join(parts)
    return combined[: config.MAX_CHARS_TOTAL]


def generate(company_name: str, url: str, humorous: bool = False) -> str:
    """Step 4: the whole thing, returned as one finished string."""
    content = gather_content(url)
    system = prompts.BROCHURE_SYSTEM_HUMOROUS if humorous else prompts.BROCHURE_SYSTEM
    return llm.complete(
        model=config.BROCHURE_MODEL,
        system=system,
        user=prompts.brochure_user(company_name, content),
    )


def generate_stream(company_name: str, url: str, humorous: bool = False) -> Iterator[str]:
    """Step 4, streamed: same result, arriving piece by piece."""
    content = gather_content(url)
    system = prompts.BROCHURE_SYSTEM_HUMOROUS if humorous else prompts.BROCHURE_SYSTEM
    yield from llm.stream(
        model=config.BROCHURE_MODEL,
        system=system,
        user=prompts.brochure_user(company_name, content),
    )


def summarize(url: str) -> str:
    """The simpler sibling: one page in, a short summary out."""
    site = scraper.fetch(url)
    if site is None:
        raise RuntimeError(f"Could not load {url}. Check the address and your connection.")
    return llm.complete(
        model=config.SUMMARY_MODEL,
        system=prompts.SUMMARY_SYSTEM,
        user=prompts.summary_user(site.summary_text()),
    )
