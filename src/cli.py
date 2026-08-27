"""
The command line interface.

This file is the only one that knows a human is watching. It reads arguments,
calls the pipeline, and prints. Because all the logic lives elsewhere, adding
a web interface later means writing a new file next to this one and changing
nothing else.

Usage:
    python -m src.cli brochure "HuggingFace" https://huggingface.co
    python -m src.cli brochure "HuggingFace" https://huggingface.co --funny -o hf.md
    python -m src.cli summarize https://anthropic.com
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import brochure
from .config import MissingAPIKeyError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="brochure-generator",
        description="Turn a company website into a brochure, using an LLM.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    make = subcommands.add_parser("brochure", help="write a brochure for a company")
    make.add_argument("company", help='the company name, e.g. "HuggingFace"')
    make.add_argument("url", help="the company website, e.g. https://huggingface.co")
    make.add_argument("--funny", action="store_true", help="use the humorous tone")
    make.add_argument("--no-stream", action="store_true", help="wait for the full reply")
    make.add_argument("-o", "--output", help="also save the result to this file")

    summary = subcommands.add_parser("summarize", help="summarise a single page")
    summary.add_argument("url", help="the page to summarise")
    summary.add_argument("-o", "--output", help="also save the result to this file")

    return parser


def save(text: str, path: str) -> None:
    Path(path).write_text(text, encoding="utf-8")
    print(f"\nSaved to {path}")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        if args.command == "brochure":
            if args.no_stream or args.output:
                result = brochure.generate(args.company, args.url, humorous=args.funny)
                print("\n" + result)
            else:
                result = ""
                print()
                for piece in brochure.generate_stream(args.company, args.url, humorous=args.funny):
                    print(piece, end="", flush=True)
                    result += piece
                print()

        else:  # summarize
            result = brochure.summarize(args.url)
            print("\n" + result)

        if args.output:
            save(result, args.output)

    except MissingAPIKeyError as error:
        print(f"\n{error}", file=sys.stderr)
        return 1
    except RuntimeError as error:
        print(f"\n{error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
        return 130

    return 0


if __name__ == "__main__":
    sys.exit(main())
