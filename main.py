import os
import logging
from fastapi import FastAPI, Request, Response
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from app.agents.langgraph_agent import SlackLangGraphAgent
from app.rag import ingest_document
from app.memory import get_user_memory, update_user_memory
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.llms import OpenAI

# --- Config ---
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = os.getenv("SLACK_SIGNING_SECRET")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI & Slack Bolt ---
app = FastAPI()
slack_app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = AsyncSlackRequestHandler(slack_app)
agent = SlackLangGraphAgent()

# --- Prompt Template ---
router_prompt = PromptTemplate(
    input_variables=["input"],
    template="""
You are a router for a Slack AI assistant. Given a user message, decide which tool to use:
- doc_qa: For questions about uploaded documents
- math: For math problems
- email: For email-related tasks
- general_qa: For general knowledge or factual questions
- fallback: For anything else

User message: {input}
Tool: (doc_qa/math/email/general_qa/fallback)
"""
)

# --- Slack Event: Message (App Mention) ---
@slack_app.event("app_mention")
async def handle_app_mention(body, say, event, logger):
    user_id = event["user"]
    text = event.get("text", "")
    logger.info(f"@mention from {user_id}: {text}")
    response = agent.run(user_id, text)
    await say(response)

# --- Slack Event: File Shared ---
@slack_app.event("file_shared")
async def handle_file_shared(body, event, client, logger):
    file_id = event["file_id"]
    user_id = event.get("user_id") or event.get("user")
    logger.info(f"File shared by {user_id}: {file_id}")
    file_info = await client.files_info(file=file_id)
    file_url = file_info["file"]["url_private_download"]
    file_name = file_info["file"]["name"]
    if not file_name.lower().endswith(".pdf"):
        await client.chat_postMessage(channel=file_info["file"]["user"], text="Only PDF files are supported.")
        return
    file_bytes = await download_file(file_url, SLACK_BOT_TOKEN)
    text = extract_text_from_file(file_bytes, file_name)
    ingest_document(user_id, text)
    await client.chat_postMessage(channel=file_info["file"]["user"], text=f"File '{file_name}' ingested for RAG.")

# --- Slash Commands ---
@slack_app.command("/mydocs")
async def mydocs(ack, body, respond):
    await ack()
    user_id = body["user_id"]
    # List files (stub: list vector files)
    from os import listdir
    from os.path import isfile, join
    vector_dir = os.getenv("VECTOR_DIR", "./vectors")
    files = [f for f in listdir(vector_dir) if isfile(join(vector_dir, f)) and f.startswith(f"{user_id}")]
    if files:
        msg = "Your uploaded files:\n" + "\n".join(files)
    else:
        msg = "You have no uploaded files."
    await respond(msg)

@slack_app.command("/deletefile")
async def deletefile(ack, body, respond):
    await ack()
    user_id = body["user_id"]
    text = body.get("text", "").strip()
    if not text:
        await respond("Usage: /deletefile <filename>")
        return
    vector_dir = os.getenv("VECTOR_DIR", "./vectors")
    file_path = os.path.join(vector_dir, text)
    if os.path.exists(file_path) and text.startswith(f"{user_id}"):
        os.remove(file_path)
        await respond(f"Deleted file: {text}")
    else:
        await respond("File not found or not owned by you.")

@slack_app.command("/clearhistory")
async def clearhistory(ack, body, respond):
    await ack()
    user_id = body["user_id"]
    from redis import from_url
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    r = from_url(redis_url)
    r.delete(f"user:{user_id}:history")
    await respond("Your chat history has been cleared.")

@slack_app.command("/agenthelp")
async def agenthelp(ack, respond):
    await ack()
    # Block Kit UI (simple)
    blocks = [
        {"type": "section", "text": {"type": "mrkdwn", "text": "*Available Agent:*\n• Document QA (PDF RAG)"}}
    ]
    await respond(blocks=blocks)

# --- FastAPI route for Slack events ---
@app.post("/slack/events")
async def endpoint(req: Request):
    return await handler.handle(req)

# --- Helpers (stubs, to be implemented) ---
async def download_file(url, token):
    import aiohttp
    headers = {"Authorization": f"Bearer {token}"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            return await resp.read()

def extract_text_from_file(file_bytes, file_name):
    # Simple: handle .txt, .pdf, .docx (stub)
    if file_name.endswith(".txt"):
        return file_bytes.decode("utf-8")
    elif file_name.endswith(".pdf"):
        from io import BytesIO
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(file_bytes))
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif file_name.endswith(".docx"):
        from io import BytesIO
        import docx
        doc = docx.Document(BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
    else:
        return "Unsupported file type. Only .txt, .pdf, .docx supported."

@slack_app.event("message")
async def handle_message_events(body, say, event, logger):
    logger.info(f"handle_message_events:{body}")
    user_id = event.get("user")
    text = event.get("text", "")
    channel_type = event.get("channel_type")
    # Ignore messages from bots (including itself)
    if event.get("subtype") == "bot_message" or user_id is None:
        return
    # Respond in DMs or if bot is mentioned in a channel
    if channel_type == "im" or f"<@{body['authorizations'][0]['user_id']}>" in text:
        response = agent.run(user_id, text)
        await say(response) 