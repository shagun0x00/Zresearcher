
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

    def is_valid_url(self, url: str) -> bool:
        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
            and not parsed.username
            and not parsed.password
        )

    def search_and_extract(
        self,
        query: str,
        task_id: int,
    ) -> list[ResearchSource]:

        try:
            search_client = DDGS(timeout=15)

            results = search_client.text(
                query=query,
                region="in-en",
                safesearch="moderate",
                max_results=self.max_results,
            )

            sources = []

            for index, result in enumerate(results, start=1):

                url = result.get("href", "")
                title = result.get("title", "Untitled source")
                snippet = result.get("body", "")

                if not self.is_valid_url(url):
                    continue

                content = ""
                content_source = "search_snippet"

                try:
                    extracted = search_client.extract(
                        url,
                        fmt="text_plain",
                    )

                    content = extracted.get("content", "")

                    if content and content.strip():
                        content = content.strip()[
                            :self.max_content_chars
                        ]
                        content_source = "webpage"

                except Exception:
                    # Continue with the search snippet if extraction fails.
                    content = ""

                if not content:
                    content = snippet

                source = ResearchSource(
                    source_id=f"T{task_id}-S{index}",
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

            return sources

        except Exception as exc:
            raise SearchServiceError(
                f"Web search failed: {exc}"
            ) from exc


search_service = SearchService()
 