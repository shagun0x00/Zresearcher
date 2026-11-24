
# app/services/search_service.py

import time
from datetime import datetime, timezone
from urllib.parse import urlparse

from ddgs import DDGS

from app.schemas.research import ResearchSource


class SearchServiceError(Exception):
    """Raised when web search fails."""


class SearchService:

    def __init__(self):
        self.max_results = 4
        self.max_content_chars = 5000
        self.max_attempts = 3

    def is_valid_url(self, url: str) -> bool:
        if not url:
            return False

        try:
            parsed = urlparse(url)

            return (
                parsed.scheme in ("http", "https")
                and bool(parsed.netloc)
                and not parsed.username
                and not parsed.password
            )

        except Exception:
            return False

    def _build_fallback_query(self, query: str) -> str:
        """Shorten a long search query for a fallback attempt."""

        words = query.split()

        if len(words) > 8:
            return " ".join(words[:8])

        return query

    def _extract_source_content(self, search_client, url: str) -> tuple[str, str]:
        """Extract webpage text; fall back to an empty string on failure."""

        try:
            extracted = search_client.extract(
                url,
                fmt="text_plain",
            )

            if isinstance(extracted, dict):
                content = extracted.get("content", "")
            else:
                content = ""

            if content and content.strip():
                return (
                    content.strip()[:self.max_content_chars],
                    "webpage",
                )

        except Exception:
            pass

        return "", "search_snippet"

    def search_and_extract(
        self,
        query: str,
        task_id: int,
    ) -> list[ResearchSource]:

        if not query or not query.strip():
            raise SearchServiceError("Search query cannot be empty.")

        fallback_query = self._build_fallback_query(query.strip())
        queries = [query.strip()]

        if fallback_query.lower() != query.strip().lower():
            queries.append(fallback_query)

        last_error = None
        results = []

        for search_query in queries:
            for attempt in range(1, self.max_attempts + 1):
                try:
                    with DDGS(timeout=20) as search_client:
                        search_results = search_client.text(
                            query=search_query,
                            region="in-en",
                            safesearch="moderate",
                            max_results=self.max_results,
                        )

                        results = list(search_results or [])

                        if results:
                            sources = []
                            seen_urls = set()

                            for index, result in enumerate(results, start=1):
                                url = result.get("href", "")
                                title = result.get("title") or "Untitled source"
                                snippet = result.get("body") or ""

                                if not self.is_valid_url(url):
                                    continue

                                normalized_url = url.rstrip("/").lower()

                                if normalized_url in seen_urls:
                                    continue

                                seen_urls.add(normalized_url)

                                content, content_source = (
                                    self._extract_source_content(
                                        search_client,
                                        url,
                                    )
                                )

                                if not content:
                                    content = snippet[:self.max_content_chars]

                                if not content.strip():
                                    continue

                                source = ResearchSource(
                                    source_id=f"T{task_id}-S{len(sources) + 1}",
                                    title=title,
                                    url=url,
                                    snippet=snippet,
                                    content=content,
                                    content_source=content_source,
                                    published_date=result.get("date"),
                                    retrieved_at=datetime.now(
                                        timezone.utc
                                    ).isoformat(),
                                )

                                sources.append(source)

                            if sources:
                                return sources

                    # Search returned no usable sources. Try again.
                    last_error = "Search returned no usable results."

                except Exception as exc:
                    last_error = exc

                if attempt < self.max_attempts:
                    time.sleep(attempt * 2)

        # No results is not necessarily a provider exception.
        if not results and last_error:
            return []

        if last_error:
            raise SearchServiceError(
                f"Web search failed after retries: {last_error}"
            ) from (
                last_error if isinstance(last_error, Exception) else None
            )

        return []


# Shared service instance
search_service = SearchService()
