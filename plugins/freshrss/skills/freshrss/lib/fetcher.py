"""Full article fetcher with fallback to dynamic rendering."""

from typing import Any

import httpx
import trafilatura


# Lazy-loaded browser instance (singleton)
_playwright = None
_browser = None


async def _get_browser():
    """Get or create browser instance (singleton pattern)."""
    global _playwright, _browser

    if _browser is None:
        from playwright.async_api import async_playwright

        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(headless=True)

    return _browser


async def close_browser() -> None:
    """Close browser and cleanup resources."""
    global _playwright, _browser

    if _browser:
        await _browser.close()
        _browser = None

    if _playwright:
        await _playwright.stop()
        _playwright = None


async def _fetch_rendered_html(url: str, timeout: int = 30) -> str:
    """Fetch page HTML after JavaScript rendering.

    Uses Playwright to load the page and wait for network idle.

    Args:
        url: The URL to fetch
        timeout: Maximum wait time in seconds

    Returns:
        Rendered HTML content as string
    """
    browser = await _get_browser()
    page = await browser.new_page()

    try:
        await page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
        html = await page.content()
        return html
    finally:
        await page.close()


async def _fetch_static(url: str, timeout: int) -> str:
    """Fetch HTML using httpx (static, no JS execution).

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds

    Returns:
        HTML content as string
    """
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        response = await client.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; FreshRSS-Skill/1.0)",
                "Accept": "text/html,application/xhtml+xml,*/*",
            },
        )
        response.raise_for_status()
        return response.text


def _extract_content(html: str) -> dict[str, Any] | None:
    """Extract article content using trafilatura.

    Args:
        html: Raw HTML content

    Returns:
        Extracted content dict with content, title, author, date,
        or None if extraction fails
    """
    extracted = trafilatura.extract(
        html,
        include_links=True,
        include_images=False,
        include_tables=True,
        output_format="txt",
    )

    if not extracted:
        # Retry with lenient settings
        extracted = trafilatura.extract(
            html,
            include_links=True,
            include_images=False,
            include_tables=True,
            output_format="txt",
            favor_recall=True,
        )

    if not extracted:
        return None

    metadata = trafilatura.extract_metadata(html)

    result: dict[str, Any] = {"content": extracted}
    if metadata:
        if metadata.title:
            result["title"] = metadata.title
        if metadata.author:
            result["author"] = metadata.author
        if metadata.date:
            result["date"] = metadata.date

    return result


async def fetch_full_article(
    url: str,
    force_dynamic: bool = False,
    timeout: int = 30,
) -> dict[str, Any]:
    """Fetch full article content from original URL.

    By default, uses fast static fetching (trafilatura).
    If the returned content seems incomplete or contains only
    JavaScript placeholders, call again with force_dynamic=True.

    Args:
        url: The original article URL to fetch
        force_dynamic: Force browser rendering for JS-heavy sites
        timeout: Request timeout in seconds (default: 30)

    Returns:
        Extracted article with content, title, author, date, url, and method.
        The 'method' field indicates 'static' or 'dynamic' fetch was used.
    """
    if not url:
        return {"error": True, "message": "URL is required", "code": "INVALID_INPUT"}

    # ========== Dynamic fetch (Playwright) ==========
    if force_dynamic:
        try:
            html = await _fetch_rendered_html(url, timeout=timeout)
            result = _extract_content(html)

            if result:
                result["url"] = url
                result["method"] = "dynamic"
                return result

            return {
                "error": True,
                "message": "Could not extract content after dynamic rendering",
                "code": "EXTRACTION_FAILED",
            }

        except ImportError:
            return {
                "error": True,
                "message": "Playwright not installed. Run: playwright install chromium",
                "code": "PLAYWRIGHT_NOT_INSTALLED",
            }
        except Exception as e:
            return {
                "error": True,
                "message": f"Dynamic fetch failed: {e}",
                "code": "DYNAMIC_FETCH_FAILED",
            }

    # ========== Static fetch (trafilatura) ==========
    try:
        html = await _fetch_static(url, timeout)
        result = _extract_content(html)

        if result:
            result["url"] = url
            result["method"] = "static"
            return result

        return {
            "error": True,
            "message": "Could not extract content from page",
            "code": "EXTRACTION_FAILED",
            "hint": "Try calling with --dynamic flag for JS-rendered pages",
        }

    except httpx.TimeoutException:
        return {"error": True, "message": f"Timeout fetching URL: {url}", "code": "TIMEOUT"}
    except httpx.HTTPStatusError as e:
        return {
            "error": True,
            "message": f"HTTP error {e.response.status_code}",
            "code": "HTTP_ERROR",
        }
    except httpx.RequestError as e:
        return {"error": True, "message": f"Request failed: {e}", "code": "REQUEST_ERROR"}
