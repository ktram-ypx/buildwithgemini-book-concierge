# Copyright 2026 Google LLC
"""Retrieval function tool grounded on Culpeper's Complete Herbal RAG corpus."""

import vertexai
from vertexai.preview import rag

PROJECT_ID = "qwiklabs-gcp-03-52fbb8ca3c22"
LOCATION = "us-central1"
CORPUS_NAME = "projects/706640678435/locations/us-central1/ragCorpora/5125703306366156800"


def consult_complete_herbal_corpus(query: str) -> str:
    """Searches Culpeper's Complete Herbal book corpus for historical herbal remedies, plants, and ailments.

    Args:
        query: What to look up in the book (a plant, ailment, remedy, or virtue).

    Returns:
        Relevant passages extracted from the Complete Herbal book text, or a message if none found.
    """
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        resp = rag.retrieval_query(
            text=query,
            rag_resources=[rag.RagResource(rag_corpus=CORPUS_NAME)],
            rag_retrieval_config=rag.RagRetrievalConfig(top_k=5),
        )
        contexts = getattr(resp.contexts, "contexts", [])
        passages = [c.text.strip() for c in contexts if getattr(c, "text", "").strip()]
        if passages:
            return "\n\n---\n\n".join(passages)
        return "No relevant passages found in the Complete Herbal corpus."
    except Exception as e:
        return f"Retrieval failed: {e}"
