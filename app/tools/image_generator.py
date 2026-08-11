# Copyright 2026 Google LLC
"""Cover art generation tool using gemini-3.1-flash-lite-image in global location."""

import time
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

BUCKET_NAME = "book-concierge-assets-qwiklabs-gcp-03-52fbb8ca3c22"
PROJECT_ID = "qwiklabs-gcp-03-52fbb8ca3c22"


def generate_book_cover_art(
    prompt: str,
    title: str = "Book Cover",
    tool_context: ToolContext = None,
) -> str:
    """Generates a custom book cover illustration using the gemini-3.1-flash-lite-image model,
    saves it as an ADK artifact, uploads it to a public GCS bucket, and returns its public URL.

    Args:
        prompt: Description of the visual cover art concept or scene.
        title: Title of the book (used for naming the asset).
        tool_context: Automatically injected ADK ToolContext for saving artifacts.

    Returns:
        Public HTTPS URL of the uploaded generated cover image in Cloud Storage.
    """
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    full_prompt = f"A professional book cover art illustration for '{title}'. Concept: {prompt}"

    try:
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite-image",
            contents=full_prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
            ),
        )

        image_bytes = None
        for candidate in getattr(response, "candidates", []):
            for part in getattr(candidate.content, "parts", []):
                if getattr(part, "inline_data", None):
                    image_bytes = part.inline_data.data
                    break
            if image_bytes:
                break

        if not image_bytes:
            return "Error: Model response did not contain image bytes."

        # Unique object filename
        slug = "".join(c if c.isalnum() else "_" for c in title.lower())[:20]
        object_name = f"covers/{slug}_{int(time.time())}_{str(uuid.uuid4())[:6]}.jpg"

        # 1. Save artifact in ToolContext for Playground
        if tool_context and hasattr(tool_context, "save_artifact"):
            try:
                artifact_part = types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpeg",
                )
                tool_context.save_artifact(
                    filename=f"{slug}_cover.jpg",
                    artifact=artifact_part,
                )
            except Exception as e:
                print("Note: save_artifact failed:", e)

        # 2. Upload image bytes directly to GCS bucket
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(object_name)
        blob.upload_from_string(image_bytes, content_type="image/jpeg")

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"
        return public_url

    except Exception as e:
        return f"Error generating image: {e}"
