"""FreshRSS Google Reader API client."""

from datetime import UTC, datetime
from types import TracebackType
from typing import Any
from urllib.parse import quote, urlencode

import httpx
from pydantic import BaseModel, Field, computed_field


# =============================================================================
# Exceptions
# =============================================================================


class FreshRSSError(Exception):
    """Base exception for FreshRSS client."""


class AuthenticationError(FreshRSSError):
    """Failed to authenticate with FreshRSS API."""


class APIError(FreshRSSError):
    """FreshRSS API returned an error."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


# =============================================================================
# Models
# =============================================================================


class Category(BaseModel):
    """Feed category/folder."""

    id: str
    label: str


class Subscription(BaseModel):
    """RSS feed subscription."""

    id: str
    title: str
    url: str
    html_url: str = Field(alias="htmlUrl")
    icon_url: str | None = Field(default=None, alias="iconUrl")
    categories: list[Category] = Field(default_factory=list)


class SubscriptionList(BaseModel):
    """List of subscriptions response."""

    subscriptions: list[Subscription]


class ArticleOrigin(BaseModel):
    """Article source feed info."""

    stream_id: str = Field(alias="streamId")
    title: str
    html_url: str = Field(alias="htmlUrl")


class ArticleSummary(BaseModel):
    """Article summary/content."""

    content: str


class Article(BaseModel):
    """RSS article/item."""

    id: str
    title: str
    published: int  # Unix timestamp
    updated: int | None = None
    canonical: list[dict[str, Any]] = Field(default_factory=list)
    alternate: list[dict[str, Any]] = Field(default_factory=list)
    summary: ArticleSummary | None = None
    origin: ArticleOrigin | None = None

    @computed_field
    @property
    def link(self) -> str | None:
        """Get article URL from canonical or alternate links."""
        if self.canonical:
            return self.canonical[0].get("href")
        if self.alternate:
            return self.alternate[0].get("href")
        return None

    @computed_field
    @property
    def published_at(self) -> datetime:
        """Get published timestamp as datetime."""
        return datetime.fromtimestamp(self.published, tz=UTC)


class StreamContents(BaseModel):
    """Response from stream/contents endpoint."""

    id: str
    title: str | None = None
    updated: int | None = None
    items: list[Article] = Field(default_factory=list)
    continuation: str | None = None


class UnreadCount(BaseModel):
    """Unread count for a feed/category."""

    id: str
    count: int
    newest_item_timestamp_usec: str = Field(alias="newestItemTimestampUsec")


class UnreadCountResponse(BaseModel):
    """Response from unread-count endpoint."""

    max: int
    unreadcounts: list[UnreadCount]


# =============================================================================
# Google Reader API state tags
# =============================================================================

STATE_READ = "user/-/state/com.google/read"
STATE_STARRED = "user/-/state/com.google/starred"
STATE_READING_LIST = "user/-/state/com.google/reading-list"


# =============================================================================
# Client
# =============================================================================


class FreshRSSClient:
    """Async client for FreshRSS Google Reader API."""

    def __init__(
        self,
        api_url: str,
        username: str,
        password: str,
        timeout: int = 30,
    ) -> None:
        """Initialize the FreshRSS client.

        Args:
            api_url: Base URL of FreshRSS API (e.g., https://example.com/api/greader.php)
            username: FreshRSS username
            password: FreshRSS API password
            timeout: Request timeout in seconds
        """
        self.api_url = api_url.rstrip("/")
        self.username = username
        self.password = password
        self.timeout = timeout
        self._auth_token: str | None = None
        self._action_token: str | None = None
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "FreshRSSClient":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get HTTP client, creating if needed."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    # =========================================================================
    # Authentication
    # =========================================================================

    async def authenticate(self) -> str:
        """Authenticate with FreshRSS and get auth token.

        Returns:
            Auth token string.

        Raises:
            AuthenticationError: If authentication fails.
        """
        client = self._get_client()
        url = f"{self.api_url}/accounts/ClientLogin"

        try:
            response = await client.post(
                url,
                data={
                    "Email": self.username,
                    "Passwd": self.password,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise AuthenticationError(f"Authentication failed: {e.response.status_code}") from e
        except httpx.RequestError as e:
            raise AuthenticationError(f"Authentication request failed: {e}") from e

        # Parse response: SID=xxx\nLSID=xxx\nAuth=xxx
        auth_data: dict[str, str] = {}
        for line in response.text.strip().split("\n"):
            if "=" in line:
                key, value = line.split("=", 1)
                auth_data[key] = value

        if "Auth" not in auth_data:
            raise AuthenticationError("Auth token not found in response")

        self._auth_token = auth_data["Auth"]
        return self._auth_token

    async def _ensure_authenticated(self) -> None:
        """Ensure client is authenticated, authenticating if needed."""
        if self._auth_token is None:
            await self.authenticate()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self._auth_token:
            headers["Authorization"] = f"GoogleLogin auth={self._auth_token}"
        return headers

    async def get_token(self) -> str:
        """Get action token for POST operations.

        Returns:
            Action token string.

        Raises:
            APIError: If token request fails.
        """
        await self._ensure_authenticated()
        client = self._get_client()
        url = f"{self.api_url}/reader/api/0/token"

        try:
            response = await client.get(url, headers=self._get_headers())
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to get token: {e.response.status_code}", e.response.status_code
            ) from e

        self._action_token = response.text.strip()
        return self._action_token

    async def _ensure_action_token(self) -> str:
        """Ensure action token is available and fresh."""
        await self.get_token()
        return self._action_token  # type: ignore[return-value]

    # =========================================================================
    # Subscriptions
    # =========================================================================

    async def get_subscriptions(self) -> list[Subscription]:
        """Get list of RSS feed subscriptions.

        Returns:
            List of Subscription objects.

        Raises:
            APIError: If request fails.
        """
        await self._ensure_authenticated()
        client = self._get_client()
        url = f"{self.api_url}/reader/api/0/subscription/list"

        try:
            response = await client.get(
                url,
                params={"output": "json"},
                headers=self._get_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to get subscriptions: {e.response.status_code}",
                e.response.status_code,
            ) from e

        data = response.json()
        subscription_list = SubscriptionList.model_validate(data)
        return subscription_list.subscriptions

    async def get_unread_counts(self) -> dict[str, int]:
        """Get unread article counts per feed.

        Returns:
            Dict mapping feed ID to unread count.

        Raises:
            APIError: If request fails.
        """
        await self._ensure_authenticated()
        client = self._get_client()
        url = f"{self.api_url}/reader/api/0/unread-count"

        try:
            response = await client.get(
                url,
                params={"output": "json"},
                headers=self._get_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to get unread counts: {e.response.status_code}",
                e.response.status_code,
            ) from e

        data = response.json()
        unread_response = UnreadCountResponse.model_validate(data)
        return {item.id: item.count for item in unread_response.unreadcounts}

    # =========================================================================
    # Articles
    # =========================================================================

    async def get_stream_contents(
        self,
        stream_id: str,
        count: int = 100,
        continuation: str | None = None,
        exclude_target: str | None = None,
    ) -> StreamContents:
        """Get contents of a stream (feed, category, or state).

        Args:
            stream_id: Stream identifier (feed ID, category, or state tag)
            count: Maximum number of items to return
            continuation: Continuation token for pagination
            exclude_target: State tag to exclude (e.g., read articles)

        Returns:
            StreamContents with articles.

        Raises:
            APIError: If request fails.
        """
        await self._ensure_authenticated()
        client = self._get_client()

        encoded_stream_id = quote(stream_id, safe="")
        url = f"{self.api_url}/reader/api/0/stream/contents/{encoded_stream_id}"

        params: dict[str, str | int] = {
            "output": "json",
            "n": count,
        }
        if continuation:
            params["c"] = continuation
        if exclude_target:
            params["xt"] = exclude_target

        try:
            response = await client.get(
                url,
                params=params,
                headers=self._get_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to get stream contents: {e.response.status_code}",
                e.response.status_code,
            ) from e

        data = response.json()
        return StreamContents.model_validate(data)

    async def get_unread_articles(
        self,
        limit: int = 100,
        feed_id: str | None = None,
    ) -> list[Article]:
        """Get unread articles.

        Args:
            limit: Maximum number of articles to return
            feed_id: Optional feed ID to filter by

        Returns:
            List of unread Article objects.

        Raises:
            APIError: If request fails.
        """
        stream_id = feed_id if feed_id else STATE_READING_LIST
        exclude = STATE_READ

        articles: list[Article] = []
        continuation: str | None = None

        while len(articles) < limit:
            remaining = limit - len(articles)
            batch_size = min(remaining, 100)

            stream = await self.get_stream_contents(
                stream_id=stream_id,
                count=batch_size,
                continuation=continuation,
                exclude_target=exclude,
            )

            articles.extend(stream.items)

            if not stream.continuation or len(stream.items) < batch_size:
                break

            continuation = stream.continuation

        return articles[:limit]

    async def get_article_by_id(self, article_id: str) -> Article | None:
        """Get a single article by ID.

        Args:
            article_id: The article ID

        Returns:
            Article object or None if not found.
        """
        await self._ensure_authenticated()
        client = self._get_client()
        url = f"{self.api_url}/reader/api/0/stream/items/contents"

        try:
            response = await client.post(
                url,
                data={"i": article_id, "output": "json"},
                headers=self._get_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError:
            return None

        data = response.json()
        items = data.get("items", [])
        if items:
            return Article.model_validate(items[0])
        return None

    # =========================================================================
    # State Management
    # =========================================================================

    async def mark_as_read(self, article_ids: list[str]) -> bool:
        """Mark articles as read.

        Args:
            article_ids: List of article IDs to mark as read

        Returns:
            True if successful.

        Raises:
            APIError: If request fails.
        """
        return await self._edit_tag(article_ids, add_tag=STATE_READ)

    async def mark_as_starred(self, article_ids: list[str]) -> bool:
        """Mark articles as starred.

        Args:
            article_ids: List of article IDs to star

        Returns:
            True if successful.

        Raises:
            APIError: If request fails.
        """
        return await self._edit_tag(article_ids, add_tag=STATE_STARRED)

    async def _edit_tag(
        self,
        article_ids: list[str],
        add_tag: str | None = None,
        remove_tag: str | None = None,
    ) -> bool:
        """Edit tags on articles.

        Args:
            article_ids: List of article IDs
            add_tag: Tag to add
            remove_tag: Tag to remove

        Returns:
            True if successful.

        Raises:
            APIError: If request fails.
        """
        if not article_ids:
            return True

        await self._ensure_authenticated()
        token = await self._ensure_action_token()
        client = self._get_client()
        url = f"{self.api_url}/reader/api/0/edit-tag"

        form_data: list[tuple[str, str]] = [("T", token)]
        for article_id in article_ids:
            form_data.append(("i", article_id))
        if add_tag:
            form_data.append(("a", add_tag))
        if remove_tag:
            form_data.append(("r", remove_tag))

        encoded_data = urlencode(form_data)

        try:
            response = await client.post(
                url,
                content=encoded_data,
                headers=self._get_headers(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to edit tags: {e.response.status_code}",
                e.response.status_code,
            ) from e

        return response.text.strip() == "OK"
