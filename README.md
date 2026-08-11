# 📚 Book Concierge AI Agent

An intelligent, multi-modal AI book concierge built on the **Google Agent Development Kit (ADK)** and deployed on **Google Cloud Agent Platform**. 

Book Concierge helps users discover literature, manage personal reading catalogs, search live online book metadata, generate custom AI cover art, ground recommendations with RAG knowledge, and remember user preferences across sessions.

Generated for this [lab](https://storage.googleapis.com/bwg3/index.html).

---

## 🌟 Key Features

- **📖 Interactive Book & Catalog Management**: Search Google Books, list personal collections, add new titles, and update reading statuses backed by **Google Cloud Firestore**.
- **🎨 AI Cover Art Generation**: Generate custom book cover art on demand using the `gemini-3.1-flash-lite-image` model, auto-saved to **Google Cloud Storage** and presented via public URLs.
- **🧠 Cross-Session Long-Term Memory**: Remembers user reading preferences, favorite authors, and past recommendations across conversations via **Vertex AI Memory Bank**.
- **🌿 Grounded RAG Knowledge**: Grounded retrieval against Culpeper's Complete Herbal corpus using **Vertex AI RAG Engine**.
- **🐍 Safe Sandbox Code Execution**: Securely executes Python code snippets in an isolated cloud environment with **Agent Engine Sandbox Code Executor**.
- **🎛️ Rich A2UI Card UI**: Emits rich display cards, tables, and images directly into the chat using **A2UI Schema 0.8**.
- **💬 Sleek Web Chat Interface**: Includes a FastAPI A2A proxy server and a modern web chat UI with quick-action suggestion chips, responsive styling, and animated thinking indicators.

---

## ☁️ Google Cloud Services & Technologies Used

| Service / Tool | Purpose in Project |
| :--- | :--- |
| **Vertex AI Agent Engine** | Hosts and orchestrates the deployed agent runtime via A2A protocol |
| **Vertex AI Memory Bank** | Long-term memory extraction callback and `PreloadMemoryTool` |
| **Vertex AI RAG Engine** | Vector search and document retrieval over specialized corpora |
| **Vertex AI Gemini (`gemini-3.1-flash-lite-image`)** | Generates high-quality book cover images |
| **Google Cloud Storage (GCS)** | Stores and serves generated image artifacts publicly |
| **Google Cloud Firestore** | NoSQL database storing user book catalogs and reading lists |
| **Google Cloud Run** | Containerized hosting for the FastAPI proxy & web frontend |
| **Agent Engine Sandbox** | Isolated Python execution sandbox |
| **Google ADK & A2A SDK** | Framework for agent creation, tool definitions, and A2A streaming |

---

## 📁 Repository Structure

```
book-concierge/
├── app/
│   ├── agent.py                 # Core agent definition, callbacks, and sandbox setup
│   ├── a2ui_utils.py            # A2UI event wrapper and callback
│   └── tools/
│       ├── firestore_books.py   # Firestore book catalog CRUD tools
│       ├── google_books.py      # Google Books API search tool
│       ├── image_generator.py  # Gemini cover art tool + GCS upload
│       └── herbal_rag.py        # Vertex AI RAG retrieval tool
├── frontend/
│   ├── main.py                  # FastAPI proxy talking A2A protocol
│   ├── requirements.txt         # Frontend dependencies
│   └── static/
│       └── index.html           # Chat UI with suggestion chips & A2UI card renderer
├── agents-cli-manifest.yaml    # Deployment manifest
├── deployment_metadata.json     # Agent Engine resource mapping
└── pyproject.toml               # Python dependencies
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- `uv` package manager installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- `google-agents-cli` installed (`uv tool install google-agents-cli`)
- Google Cloud SDK authenticated with Application Default Credentials (`gcloud auth application-default login`)

### 2. Run the Agent Locally
Launch the agent in the ADK dev environment:
```bash
agents-cli playground
```

### 3. Run the Web Frontend Locally
In a separate terminal, start the FastAPI chat proxy frontend:
```bash
cd frontend
AGENT_ENGINE_RESOURCE_NAME="<your-agent-engine-resource-name>" \
AGENT_DIRECTORY="app" \
PORT=8080 uv run python main.py
```
Open **`http://localhost:8080`** in your browser to interact with the Book Concierge!

---

## ☁️ Deployment

### Deploy Agent to Agent Platform
```bash
agents-cli deploy
```

### Deploy Frontend to Cloud Run
```bash
gcloud run deploy book-concierge-frontend \
  --source ./frontend \
  --region us-east1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<your-resource-name>",AGENT_DIRECTORY="app" \
  --project <your-gcp-project-id>
```

---

## 📝 License

Licensed under the Apache License, Version 2.0.
