from google import genai
import os

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found")

client = genai.Client(api_key=GOOGLE_API_KEY)

CHAT_MODEL = "models/gemini-2.5-flash"

def generate_answer(context: str, question: str):

    prompt = f"""
    You are a helpful assistant.
    Explain the following document content in simple language.
    Provide a detailed and complete answer using all relevant information from the document context.
    Do not shorten the response.

    Context:
    {context}

    Question:
    {question}
    """

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt,
        config={
            "temperature": 0.2,
            "top_p": 0.9,
            "max_output_tokens": 8000
        }
    )

    return response.text

def summarize_conversation(summary: str, messages: list):

    conversation_text = ""

    for msg in messages:
        conversation_text += f"{msg['role'].upper()}: {msg['content']}\n"

    prompt = f"""
You are a conversation summarizer.

Previous summary:
{summary}

New conversation:
{conversation_text}

Create an updated concise summary preserving important context.
"""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt
    )

    return response.text

import json
from google import genai

client = genai.Client(api_key=GOOGLE_API_KEY)

CHAT_MODEL = "models/gemini-2.5-flash"


def extract_structured_memory(message: str):
    prompt = f"""
You are a memory extraction engine.

Extract permanent user facts from the message.

Rules:
- Only extract factual, long-term information.
- Ignore temporary statements.
- Return ONLY valid JSON.
- If nothing important, return empty JSON {{}}.

Possible fields:
- name
- preferred_language
- profession
- interests
- goals
- location

Message:
{message}
"""

    response = client.models.generate_content(
        model=CHAT_MODEL,
        contents=prompt
    )

    try:
        return json.loads(response.text.strip())
    except:
        return {}