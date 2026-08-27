"""
Every word we send to the model lives in this file, and nothing else does.

Prompts are the part of an LLM project you change most often. Keeping them
away from the logic means you can rewrite the tone of a brochure without
reading a single line of scraping or API code.
"""

LINK_SELECTION_SYSTEM = """
You are given a list of links found on a company's website.
Decide which are worth reading to write a brochure about the company:
pages like About, Company, Team, Careers, Jobs, Customers, or Products.

Ignore Terms of Service, Privacy Policy, login pages, social media profiles,
and email links.

Respond only in JSON, in exactly this shape:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page", "url": "https://another.full.url/careers"}
    ]
}
""".strip()


def link_selection_user(url: str, links: list[str]) -> str:
    """Ask the model to pick the useful links out of the ones we found."""
    joined = "\n".join(links)
    return (
        f"Here are the links found on {url}.\n"
        f"Choose the ones relevant to a brochure and reply with full URLs in JSON.\n\n"
        f"{joined}"
    )


BROCHURE_SYSTEM = """
You analyse the contents of several pages from a company website and write a
short brochure about that company for prospective customers, investors, and
recruits.

Cover what the company does, its culture, its customers, and its open roles,
but only where the source pages actually give you that information. Do not
invent facts.

Respond in markdown. Do not wrap the markdown in a code block.
""".strip()


BROCHURE_SYSTEM_HUMOROUS = """
You analyse the contents of several pages from a company website and write a
short, funny, slightly irreverent brochure about that company for prospective
customers, investors, and recruits.

Keep it entertaining but never mean, and never invent facts about the company.

Respond in markdown. Do not wrap the markdown in a code block.
""".strip()


def brochure_user(company_name: str, content: str) -> str:
    """Hand the model everything we scraped and ask for the brochure."""
    return (
        f"You are looking at a company called: {company_name}\n\n"
        f"Here are the contents of its landing page and other relevant pages. "
        f"Use this information to write a short brochure in markdown.\n\n"
        f"{content}"
    )


SUMMARY_SYSTEM = """
You analyse the contents of a website and give a short, clear summary,
ignoring navigation text. If the page includes news or announcements,
summarise those too.

Respond in markdown. Do not wrap the markdown in a code block.
""".strip()


def summary_user(content: str) -> str:
    return f"Here are the contents of a website. Summarise it.\n\n{content}"
