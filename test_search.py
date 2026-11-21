
from app.services.search_service import (
    search_service,
    SearchServiceError,
)


def main():

    query = (
        "Electric vehicle market growth India "
        "government report"
    )

    try:
        sources = search_service.search_and_extract(
            query=query,
            task_id=1,
        )

        print("\n========== SEARCH RESULTS ==========\n")

        for source in sources:

            print(f"ID: {source.source_id}")
            print(f"TITLE: {source.title}")
            print(f"URL: {source.url}")
            print(f"CONTENT SOURCE: {source.content_source}")
            print(f"CONTENT: {source.content[:500]}")

            print("-" * 60)

        print(f"\nTOTAL SOURCES: {len(sources)}")

    except SearchServiceError as exc:
        print(f"SEARCH FAILED: {exc}")


if __name__ == "__main__":
    main()
