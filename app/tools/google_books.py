# Copyright 2026 Google LLC
"""External book metadata search tool using public online APIs (Google Books / Open Library)."""

import json
import urllib.parse
import urllib.request
from typing import Any, Optional


def search_google_books(query: str, max_results: int = 3) -> list[dict[str, Any]]:
    """Searches external public book databases (Google Books / Open Library) for real-world book metadata.

    Args:
        query: Book title, author name, or topic to search for.
        max_results: Maximum number of search results to return (default 3, max 5).

    Returns:
        A list of dictionaries containing title, authors, first_publish_year, subjects, and ISBN/cover details.
    """
    safe_query = urllib.parse.quote(query)
    headers = {"User-Agent": "BookConciergeApp/1.0 (https://cloud.google.com)"}

    # 1. Try Google Books API
    gb_url = f"https://www.googleapis.com/books/v1/volumes?q={safe_query}&maxResults={min(max_results, 5)}"
    req = urllib.request.Request(gb_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            items = data.get("items", [])
            if items:
                results = []
                for item in items:
                    vol = item.get("volumeInfo", {})
                    results.append({
                        "title": vol.get("title", "Unknown Title"),
                        "authors": vol.get("authors", ["Unknown Author"]),
                        "publishedDate": vol.get("publishedDate", "N/A"),
                        "description": vol.get("description", "No description available.")[:250] + "...",
                        "pageCount": vol.get("pageCount", 0),
                        "categories": vol.get("categories", []),
                        "source": "Google Books",
                    })
                return results
    except Exception:
        pass  # Fallback to Open Library on rate limit or error

    # 2. Fallback to Open Library API
    ol_url = f"https://openlibrary.org/search.json?q={safe_query}&limit={min(max_results, 5)}"
    req = urllib.request.Request(ol_url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
            docs = data.get("docs", [])
            results = []
            for doc in docs:
                results.append({
                    "title": doc.get("title", "Unknown Title"),
                    "authors": doc.get("author_name", ["Unknown Author"]),
                    "publishedDate": str(doc.get("first_publish_year", "N/A")),
                    "description": f"First published in {doc.get('first_publish_year', 'N/A')}. Languages: {', '.join(doc.get('language', ['en'])[:3])}.",
                    "pageCount": doc.get("number_of_pages_median", 0),
                    "categories": doc.get("subject", [])[:3],
                    "source": "Open Library",
                })
            return results
    except Exception as e:
        return [{"error": f"Failed to search online book catalog: {e}"}]
