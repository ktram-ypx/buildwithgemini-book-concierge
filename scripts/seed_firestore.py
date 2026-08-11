#!/usr/bin/env python3
# Copyright 2026 Google LLC
"""Script to seed the Firestore database with initial books data."""

from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-03-52fbb8ca3c22"
COLLECTION_NAME = "books"

INITIAL_BOOKS = [
    {
        "id": "book-1",
        "title": "Neuromancer",
        "author": "William Gibson",
        "genre": "Sci-Fi / Cyberpunk",
        "status": "unread",
        "page_count": 271,
        "rating": 4.8,
    },
    {
        "id": "book-2",
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Sci-Fi / Epic Space Opera",
        "status": "reading",
        "page_count": 412,
        "rating": 4.9,
    },
    {
        "id": "book-3",
        "title": "Snow Crash",
        "author": "Neal Stephenson",
        "genre": "Sci-Fi / Cyberpunk",
        "status": "unread",
        "page_count": 480,
        "rating": 4.7,
    },
    {
        "id": "book-4",
        "title": "Kindred",
        "author": "Octavia E. Butler",
        "genre": "Sci-Fi / Time Travel",
        "status": "finished",
        "page_count": 287,
        "rating": 4.9,
    },
]


def seed_firestore():
    db = firestore.Client(project=PROJECT_ID)
    print(f"Seeding '{COLLECTION_NAME}' collection in Firestore project '{PROJECT_ID}'...")
    collection_ref = db.collection(COLLECTION_NAME)

    for book in INITIAL_BOOKS:
        doc_ref = collection_ref.document(book["id"])
        doc_ref.set(book)
        print(f"  Added/Updated book: {book['id']} - '{book['title']}' by {book['author']}")

    print("Firestore seeding completed successfully!")


if __name__ == "__main__":
    seed_firestore()
