"""
Every setting for the project lives here.

Why this file exists: in the original notebook the model name was typed into
three separate cells and the character limits were buried inside functions.
When a value is written in more than one place, sooner or later you change one
and forget the others. Here there is exactly one copy of each.
"""

import os

from dotenv import load_dotenv

# override=True means the .env file wins over any variable already set in your
# shell. That is usually what you want while developing.
load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# --- Models -----------------------------------------------------------------
# Two different jobs, two different models. Picking links out of a list is
# mechanical work that a cheap model does just as well as an expensive one.
# Writing the brochure is the part a human actually reads, so it gets the
# better model. See the cost section of the README for what this saves.

LINK_SELECTION_MODEL = "gpt-4.1-nano"
BROCHURE_MODEL = "gpt-4.1-mini"
SUMMARY_MODEL = "gpt-4.1-mini"


# --- Limits -----------------------------------------------------------------
# These caps exist to control cost and latency. Raise them if you want richer
# brochures and are happy to pay a little more per run.

MAX_CHARS_PER_PAGE = 2_000   # how much text we keep from any single page
MAX_CHARS_TOTAL = 5_000      # how much text we send to the brochure model
MAX_LINKED_PAGES = 5         # how many extra pages we will fetch per company


# --- HTTP -------------------------------------------------------------------

REQUEST_TIMEOUT = 10  # seconds before we give up on a slow site

# Some sites reject requests that do not look like a browser.
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    )
}


class MissingAPIKeyError(RuntimeError):
    """Raised when the OpenAI key is not set up."""


def require_api_key() -> str:
    """
    Return the API key, or explain clearly how to fix it if it is missing.

    Failing early with a useful message beats failing later with a confusing
    one from deep inside the OpenAI library.
    """
    if not OPENAI_API_KEY:
        raise MissingAPIKeyError(
            "No OPENAI_API_KEY found.\n"
            "Fix: copy .env.example to .env and paste your key into it.\n"
            "You can create a key at https://platform.openai.com/api-keys"
        )
    if OPENAI_API_KEY != OPENAI_API_KEY.strip():
        raise MissingAPIKeyError(
            "Your OPENAI_API_KEY has a space or tab at the start or end. "
            "Remove it and try again."
        )
    return OPENAI_API_KEY
