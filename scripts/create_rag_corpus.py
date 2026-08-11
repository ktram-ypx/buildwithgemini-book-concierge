# Copyright 2026 Google LLC
"""Script to create a serverless Vertex AI RAG corpus and import pg49513.txt."""

from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-03-52fbb8ca3c22"
LOCATION = "us-central1"  # Serverless RAG Engine mode is us-central1 only
GCS_PATH = "gs://book-concierge-assets-qwiklabs-gcp-03-52fbb8ca3c22/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, remedies, and herbal descriptions from this text. "
    "Ignore and omit all Gutenberg metadata, license text, boilerplate, and image captions. "
    "Output clean, self-contained prose."
)


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Set serverless mode on the region's RAG engine config
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    try:
        rag.update_rag_engine_config(
            rag_engine_config=rag.RagEngineConfig(
                name=cfg,
                rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
            )
        )
        print("Set RAG engine config to serverless mode.")
    except Exception as e:
        print("RAG engine config note:", e)

    # 2. Create the RAG corpus
    print("Creating serverless RAG corpus...")
    corpus = rag.create_corpus(
        display_name="complete-herbal-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    corpus_name = corpus.name
    print(f"Corpus created successfully: {corpus_name}")

    # 3. Import and index the document
    print(f"Importing {GCS_PATH} into corpus...")
    resp = rag.import_files(
        corpus_name=corpus_name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-2.5-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print("Import complete! Response:", resp)


if __name__ == "__main__":
    main()
