#!/usr/bin/env python3
"""FreshRSS skill CLI executor.

Usage:
    python run.py setup              Configure credentials
    python run.py unread [-n NUM]    Get unread articles
    python run.py article <id>       Get single article
    python run.py fetch <url>        Fetch full content from URL
    python run.py read <id> [...]    Mark articles as read
    python run.py subs               List subscriptions
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from getpass import getpass
from typing import Any

# Add lib to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 1)[0])

from lib.credentials import get_credentials, setup_credentials, clear_credentials
from lib.client import FreshRSSClient, AuthenticationError, APIError
from lib.fetcher import fetch_full_article


def output_json(data: Any) -> None:
    """Output data as JSON."""
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


def output_error(message: str, code: str = "ERROR") -> None:
    """Output error as JSON."""
    output_json({"error": True, "message": message, "code": code})
    sys.exit(1)


# =============================================================================
# Commands
# =============================================================================


def cmd_setup(args: argparse.Namespace) -> None:
    """Configure credentials interactively."""
    if args.clear:
        if clear_credentials():
            output_json({"success": True, "message": "Credentials cleared"})
        else:
            output_error("Failed to clear credentials", "CLEAR_FAILED")
        return

    print("FreshRSS Skill Setup")
    print("=" * 40)
    print()
    print("Enter your FreshRSS API credentials.")
    print("These will be stored securely in your system keychain.")
    print()

    api_url = input("API URL (e.g., https://rss.example.com/api/greader.php): ").strip()
    if not api_url:
        output_error("API URL is required", "INVALID_INPUT")

    username = input("Username: ").strip()
    if not username:
        output_error("Username is required", "INVALID_INPUT")

    password = getpass("API Password: ").strip()
    if not password:
        output_error("Password is required", "INVALID_INPUT")

    # Test connection
    print()
    print("Testing connection...")

    async def test_connection():
        async with FreshRSSClient(api_url, username, password) as client:
            await client.authenticate()
            subs = await client.get_subscriptions()
            return len(subs)

    try:
        num_subs = asyncio.run(test_connection())
        print(f"Connected! Found {num_subs} subscriptions.")
    except AuthenticationError as e:
        output_error(f"Authentication failed: {e}", "AUTH_FAILED")
    except Exception as e:
        output_error(f"Connection failed: {e}", "CONNECTION_FAILED")

    # Save credentials
    if setup_credentials(api_url, username, password):
        output_json({
            "success": True,
            "message": "Credentials saved to keychain",
            "subscriptions": num_subs,
        })
    else:
        output_error("Failed to save credentials", "SAVE_FAILED")


async def _cmd_unread(args: argparse.Namespace) -> None:
    """Get unread articles."""
    creds = get_credentials()
    if not creds:
        output_error("Credentials not configured. Run: python run.py setup", "NO_CREDENTIALS")

    async with FreshRSSClient(creds.api_url, creds.username, creds.password) as client:
        articles = await client.get_unread_articles(limit=args.num, feed_id=args.feed)

        result = []
        for a in articles:
            result.append({
                "id": a.id,
                "title": a.title,
                "link": a.link,
                "published": a.published_at.isoformat(),
                "feed": a.origin.title if a.origin else "",
                "feed_id": a.origin.stream_id if a.origin else "",
                "summary": (a.summary.content[:500] + "..." if a.summary and len(a.summary.content) > 500 else (a.summary.content if a.summary else "")),
            })

        output_json({"count": len(result), "articles": result})


async def _cmd_unread_digest(args: argparse.Namespace) -> None:
    """Get unread articles with full content for digest generation."""
    creds = get_credentials()
    if not creds:
        output_error("Credentials not configured. Run: python run.py setup", "NO_CREDENTIALS")

    # Expand output directory
    output_dir = os.path.expanduser(args.output)

    async with FreshRSSClient(creds.api_url, creds.username, creds.password) as client:
        articles = await client.get_unread_articles(limit=args.num, feed_id=args.feed)

        if not articles:
            output_json({
                "count": 0,
                "digest_mode": True,
                "message": "No unread articles found",
                "articles": []
            })
            return

        result = []
        stats = {"total": len(articles), "success": 0, "failed": 0, "dynamic_used": 0}

        for a in articles:
            article_data = {
                "id": a.id,
                "title": a.title,
                "link": a.link,
                "published": a.published_at.isoformat(),
                "feed": a.origin.title if a.origin else "",
                "feed_id": a.origin.stream_id if a.origin else "",
            }

            # Fetch full content from original URL
            if a.link:
                try:
                    fetched = await fetch_full_article(
                        a.link,
                        force_dynamic=args.dynamic,
                        timeout=args.timeout,
                    )

                    if fetched.get("error"):
                        # Fallback to RSS content
                        rss_content = a.summary.content if a.summary else ""
                        article_data["full_content"] = rss_content
                        article_data["content_source"] = "rss"
                        article_data["fetch_error"] = fetched.get("message", "Unknown error")
                        stats["failed"] += 1
                    else:
                        article_data["full_content"] = fetched.get("content", "")
                        article_data["content_source"] = "fetched"
                        article_data["fetch_method"] = fetched.get("method", "static")
                        article_data["author"] = fetched.get("author")
                        article_data["fetch_date"] = fetched.get("date")
                        stats["success"] += 1
                        if fetched.get("method") == "dynamic":
                            stats["dynamic_used"] += 1
                except Exception as e:
                    # Fallback to RSS content on any exception
                    rss_content = a.summary.content if a.summary else ""
                    article_data["full_content"] = rss_content
                    article_data["content_source"] = "rss"
                    article_data["fetch_error"] = str(e)
                    stats["failed"] += 1
            else:
                # No link available, use RSS content
                article_data["full_content"] = a.summary.content if a.summary else ""
                article_data["content_source"] = "rss"
                article_data["fetch_error"] = "No article link available"
                stats["failed"] += 1

            # Calculate word count (character count for Chinese)
            content = article_data.get("full_content", "")
            article_data["word_count"] = len(content)

            result.append(article_data)

        # Generate suggested filename
        today = datetime.now().strftime("%Y-%m-%d")

        output_json({
            "count": len(result),
            "digest_mode": True,
            "output_dir": output_dir,
            "fetch_stats": stats,
            "articles": result,
            "instructions": {
                "task": "summarize",
                "language": "zh-CN",
                "output_format": "html",
                "suggested_filename": f"digest-{today}.html"
            }
        })


def cmd_unread(args: argparse.Namespace) -> None:
    """Get unread articles wrapper."""
    try:
        if args.digest:
            asyncio.run(_cmd_unread_digest(args))
        else:
            asyncio.run(_cmd_unread(args))
    except AuthenticationError as e:
        output_error(str(e), "AUTH_FAILED")
    except APIError as e:
        output_error(str(e), "API_ERROR")
    except Exception as e:
        output_error(str(e), "ERROR")


async def _cmd_article(args: argparse.Namespace) -> None:
    """Get single article by ID."""
    creds = get_credentials()
    if not creds:
        output_error("Credentials not configured. Run: python run.py setup", "NO_CREDENTIALS")

    async with FreshRSSClient(creds.api_url, creds.username, creds.password) as client:
        article = await client.get_article_by_id(args.article_id)

        if not article:
            output_error(f"Article not found: {args.article_id}", "NOT_FOUND")

        output_json({
            "id": article.id,
            "title": article.title,
            "link": article.link,
            "published": article.published_at.isoformat(),
            "feed": article.origin.title if article.origin else "",
            "feed_id": article.origin.stream_id if article.origin else "",
            "content": article.summary.content if article.summary else "",
        })


def cmd_article(args: argparse.Namespace) -> None:
    """Get single article wrapper."""
    try:
        asyncio.run(_cmd_article(args))
    except AuthenticationError as e:
        output_error(str(e), "AUTH_FAILED")
    except APIError as e:
        output_error(str(e), "API_ERROR")
    except Exception as e:
        output_error(str(e), "ERROR")


async def _cmd_fetch(args: argparse.Namespace) -> None:
    """Fetch full article content from URL."""
    result = await fetch_full_article(
        args.url,
        force_dynamic=args.dynamic,
        timeout=args.timeout,
    )
    output_json(result)


def cmd_fetch(args: argparse.Namespace) -> None:
    """Fetch full content wrapper."""
    try:
        asyncio.run(_cmd_fetch(args))
    except Exception as e:
        output_error(str(e), "ERROR")


async def _cmd_read(args: argparse.Namespace) -> None:
    """Mark articles as read."""
    creds = get_credentials()
    if not creds:
        output_error("Credentials not configured. Run: python run.py setup", "NO_CREDENTIALS")

    async with FreshRSSClient(creds.api_url, creds.username, creds.password) as client:
        success = await client.mark_as_read(args.article_ids)

        if success:
            output_json({
                "success": True,
                "message": f"Marked {len(args.article_ids)} article(s) as read",
                "ids": args.article_ids,
            })
        else:
            output_error("Failed to mark articles as read", "MARK_FAILED")


def cmd_read(args: argparse.Namespace) -> None:
    """Mark as read wrapper."""
    try:
        asyncio.run(_cmd_read(args))
    except AuthenticationError as e:
        output_error(str(e), "AUTH_FAILED")
    except APIError as e:
        output_error(str(e), "API_ERROR")
    except Exception as e:
        output_error(str(e), "ERROR")


async def _cmd_subs(args: argparse.Namespace) -> None:
    """List subscriptions."""
    creds = get_credentials()
    if not creds:
        output_error("Credentials not configured. Run: python run.py setup", "NO_CREDENTIALS")

    async with FreshRSSClient(creds.api_url, creds.username, creds.password) as client:
        subs = await client.get_subscriptions()
        counts = await client.get_unread_counts()

        result = []
        for s in subs:
            result.append({
                "id": s.id,
                "title": s.title,
                "url": s.url,
                "unread": counts.get(s.id, 0),
                "category": s.categories[0].label if s.categories else None,
            })

        # Sort by unread count descending
        result.sort(key=lambda x: x["unread"], reverse=True)

        total_unread = sum(r["unread"] for r in result)
        output_json({
            "count": len(result),
            "total_unread": total_unread,
            "subscriptions": result,
        })


def cmd_subs(args: argparse.Namespace) -> None:
    """List subscriptions wrapper."""
    try:
        asyncio.run(_cmd_subs(args))
    except AuthenticationError as e:
        output_error(str(e), "AUTH_FAILED")
    except APIError as e:
        output_error(str(e), "API_ERROR")
    except Exception as e:
        output_error(str(e), "ERROR")


# =============================================================================
# Main
# =============================================================================


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FreshRSS skill CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # setup
    p_setup = subparsers.add_parser("setup", help="Configure credentials")
    p_setup.add_argument("--clear", action="store_true", help="Clear stored credentials")
    p_setup.set_defaults(func=cmd_setup)

    # unread
    p_unread = subparsers.add_parser("unread", help="Get unread articles")
    p_unread.add_argument("-n", "--num", type=int, default=20, help="Number of articles (default: 20)")
    p_unread.add_argument("-f", "--feed", type=str, help="Filter by feed ID")
    p_unread.add_argument("--digest", action="store_true",
        help="Fetch full content for digest generation")
    p_unread.add_argument("--output", "-o", type=str,
        default="~/Documents/freshrss-digest/",
        help="Output directory for digest (default: ~/Documents/freshrss-digest/)")
    p_unread.add_argument("--dynamic", "-d", action="store_true",
        help="Use browser rendering for JS-heavy pages")
    p_unread.add_argument("--timeout", "-t", type=int, default=30,
        help="Timeout per article fetch in seconds (default: 30)")
    p_unread.set_defaults(func=cmd_unread)

    # article
    p_article = subparsers.add_parser("article", help="Get single article by ID")
    p_article.add_argument("article_id", help="Article ID")
    p_article.set_defaults(func=cmd_article)

    # fetch
    p_fetch = subparsers.add_parser("fetch", help="Fetch full content from URL")
    p_fetch.add_argument("url", help="Article URL")
    p_fetch.add_argument("--dynamic", "-d", action="store_true", help="Use browser rendering for JS pages")
    p_fetch.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in seconds (default: 30)")
    p_fetch.set_defaults(func=cmd_fetch)

    # read
    p_read = subparsers.add_parser("read", help="Mark articles as read")
    p_read.add_argument("article_ids", nargs="+", help="Article IDs to mark as read")
    p_read.set_defaults(func=cmd_read)

    # subs
    p_subs = subparsers.add_parser("subs", help="List subscriptions")
    p_subs.set_defaults(func=cmd_subs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
