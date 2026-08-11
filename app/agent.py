# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors.agent_engine_sandbox_code_executor import (
    AgentEngineSandboxCodeExecutor,
)
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools.firestore_books import (
    add_book_to_catalog,
    get_book_details,
    list_books,
    update_book_status,
)
from app.tools.google_books import search_google_books
from app.tools.herbal_rag import consult_complete_herbal_corpus
from app.tools.image_generator import generate_book_cover_art


MODEL = "gemini-3.6-flash"
AGENT_ENGINE_RESOURCE = "projects/706640678435/locations/us-east1/reasoningEngines/4801769588637302784"


async def generate_memories_callback(callback_context: CallbackContext):
    """Sends the completed turn/session to Memory Bank for long-term memory extraction."""
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        query: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=AGENT_ENGINE_RESOURCE,
)

schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

a2ui_instruction = schema_manager.generate_system_prompt(
    role_description=(
        "A helpful AI Book Concierge with live online book search, cover art generation, "
        "Firestore database capabilities, sandbox Python code execution, and grounding on Culpeper's Complete Herbal RAG corpus."
    ),
    workflow_description=(
        "Analyze the user's request and use available tools (Firestore catalog, online Google Books search, RAG corpus, image generator, Python sandbox) "
        "to retrieve data, calculate stats, or create cover art, then return structured A2UI display cards."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects.\n\n"
        "DATABASE, CODE EXECUTION, IMAGE & RAG TOOL INSTRUCTIONS:\n"
        "- Use `generate_book_cover_art` to generate custom visual book cover illustrations for recommendations or user prompts.\n"
        "- Use `consult_complete_herbal_corpus` to answer questions or look up remedies, plants, and herbs from Culpeper's Complete Herbal.\n"
        "- Use `search_google_books` to look up real-world published books, authors, release dates, and descriptions online.\n"
        "- Use `list_books` to query books in the user's personal Firestore catalog (filter by genre or status).\n"
        "- Use `get_book_details` to retrieve specific book details from the catalog.\n"
        "- Use `add_book_to_catalog` when the user adds a new book to their reading list or catalog.\n"
        "- Use `update_book_status` when the user changes a book's reading status ('unread', 'reading', 'finished') or rating.\n"
        "- You can execute Python code inside a secure Agent Engine sandbox for math calculations, data analysis, "
        "reading time estimations, or data formatting.\n\n"
        "MEMORY INSTRUCTIONS:\n"
        "1. You remember the user's name, stated reading preferences, favorite genres, favorite authors, "
        "and ALL previously recommended book titles across sessions.\n"
        "2. Whenever you recommend a book, clearly state the title, author, and genre so it is recorded as a durable memory.\n"
        "3. Always check preloaded memories, the Complete Herbal RAG corpus, and the catalog before answering."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=a2ui_instruction,
    tools=[
        PreloadMemoryTool(),
        generate_book_cover_art,
        consult_complete_herbal_corpus,
        search_google_books,
        list_books,
        get_book_details,
        add_book_to_catalog,
        update_book_status,
        get_weather,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
