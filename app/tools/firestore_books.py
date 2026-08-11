# Copyright 2026 Google LLC
"""Firestore function tools for reading and writing the books collection."""

from typing import Any, Optional
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-52fbb8ca3c22"
COLLECTION_NAME = "books"


def _get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    return firestore.Client(project=PROJECT_ID)


def list_books(genre: Optional[str] = None, status: Optional[str] = None) -> list[dict[str, Any]]:
    """Lists books from the Firestore database, optionally filtering by genre or status.

    Args:
        genre: Optional genre filter (e.g. 'Cyberpunk', 'Sci-Fi').
        status: Optional status filter ('unread', 'reading', 'finished').

    Returns:
        A list of book dictionaries containing title, author, genre, status, and rating.
    """
    db = _get_firestore_client()
    query = db.collection(COLLECTION_NAME)

    if status:
        query = query.where("status", "==", status.lower())

    docs = query.stream()
    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if genre and genre.lower() not in data.get("genre", "").lower():
            continue
        results.append(data)

    return results


def get_book_details(book_id: str) -> dict[str, Any]:
    """Gets details for a specific book by its ID from Firestore.

    Args:
        book_id: The ID of the book (e.g., 'book-1').

    Returns:
        A dictionary with book details or an error message.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(book_id)
    doc = doc_ref.get()

    if doc.exists:
        data = doc.to_dict()
        data["id"] = doc.id
        return data
    return {"error": f"Book with ID '{book_id}' not found."}


def add_book_to_catalog(
    title: str,
    author: str,
    genre: str,
    status: str = "unread",
    page_count: int = 0,
    rating: Optional[float] = None,
) -> str:
    """Adds a new book document to the Firestore books collection.

    Args:
        title: Title of the book.
        author: Author of the book.
        genre: Genre or topic.
        status: Reading status ('unread', 'reading', 'finished'). Defaults to 'unread'.
        page_count: Total page count.
        rating: Optional user rating (0.0 to 5.0).

    Returns:
        A confirmation message with the assigned book ID.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document()
    book_id = doc_ref.id

    book_data = {
        "id": book_id,
        "title": title,
        "author": author,
        "genre": genre,
        "status": status.lower(),
        "page_count": page_count,
        "rating": rating,
    }
    doc_ref.set(book_data)
    return f"Successfully added '{title}' by {author} to Firestore catalog with ID '{book_id}'."


def update_book_status(
    book_id: str,
    status: str,
    rating: Optional[float] = None,
) -> str:
    """Updates the reading status and optional rating of a book in Firestore.

    Args:
        book_id: The ID of the book to update (e.g. 'book-1').
        status: New status ('unread', 'reading', 'finished').
        rating: Optional updated rating (0.0 to 5.0).

    Returns:
        A confirmation message.
    """
    db = _get_firestore_client()
    doc_ref = db.collection(COLLECTION_NAME).document(book_id)
    doc = doc_ref.get()

    if not doc.exists:
        return f"Error: Book with ID '{book_id}' not found in Firestore."

    updates: dict[str, Any] = {"status": status.lower()}
    if rating is not None:
        updates["rating"] = rating

    doc_ref.update(updates)
    return f"Successfully updated book '{book_id}' status to '{status}'" + (
        f" with rating {rating}" if rating is not None else ""
    ) + "."
