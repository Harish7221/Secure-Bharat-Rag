from fastapi import FastAPI, UploadFile, File
import shutil
import os

from dotenv import load_dotenv
load_dotenv(
    
)

from app.thread_store import init_db, load_thread, save_thread, load_all_memory, save_memory
from app.pdf_utils import extract_text_from_pdf
from app.vector_store import add_embeddings, search
from app.embedding_utils import generate_embedding
from app.gemini_utils import generate_answer, summarize_conversation, extract_structured_memory
from app.chunking import chunk_text
from app.sarvam_utils import sarvam_speech_to_text, sarvam_translate_to_english, translate_document_to_english
# In-memory conversation store
# ===== Conversational Memory Store =====

conversations = {}

MAX_RECENT_TURNS = 6           # keep last 6 exchanges
SUMMARY_TRIGGER_TURNS = 12     # summarize when history exceeds this

app = FastAPI()
init_db()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.post("/upload")
async def upload_pdf(
    user_id: str,
    thread_id: str,
    file: UploadFile = File(...)
):

    import uuid
    

    doc_id = str(uuid.uuid4())

    # ===============================
    # 1️⃣ Save file
    # ===============================
    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # ===============================
    # 2️⃣ Extract text
    # ===============================
    raw_text = extract_text_from_pdf(file_path)

    if not raw_text.strip():
        return {"error": "No text found in PDF"}

    # ===============================
    # 3️⃣ Detect language (optional optimization)
    # ===============================
    try:
        from langdetect import detect
        language = detect(raw_text[:2000])  # detect using first 2000 chars
    except:
        language = "unknown"

    # ===============================
    # 4️⃣ Translate FULL document if needed
    # ===============================
    if language != "en":
        print(f"Translating document from {language} to English...")

        english_text = translate_document_to_english(raw_text)

    else:
        english_text = raw_text

    # ===============================
    # 5️⃣ Chunk translated text
    # ===============================
    chunks = chunk_text(english_text)

    # ===============================
    # 6️⃣ Generate embeddings
    # ===============================
    embeddings = [generate_embedding(chunk) for chunk in chunks]

    # ===============================
    # 7️⃣ Store in FAISS (thread-bound)
    # ===============================
    add_embeddings(
        user_id=user_id,
        thread_id=thread_id,
        doc_id=doc_id,
        embeddings=embeddings,
        chunks=chunks,
        filename=file.filename
    )

    return {
        "user_id": user_id,
        "thread_id": thread_id,
        "doc_id": doc_id,
        "filename": file.filename,
        "detected_language": language,
        "translated": language != "en",
        "chunks_added": len(chunks)
    }

@app.post("/search")
async def search_query(
    user_id: str,
    thread_id: str,   # 🔥 REQUIRED NOW
    query: str,
    doc_id: str = None,
    top_k: int = 5
):

    query_embedding = generate_embedding(query)

    results = search(
        user_id=user_id,
        thread_id=thread_id,   # 🔥 pass thread_id
        query_embedding=query_embedding,
        doc_id=doc_id,
        top_k=top_k
    )

    return {
        "user_id": user_id,
        "thread_id": thread_id,
        "doc_id_filter": doc_id,
        "top_k": top_k,
        "results": results
    }
@app.post("/ask")
async def ask_question(
    user_id: str,
    thread_id: str,
    question: str,
    doc_id: str = None
):

    MAX_MESSAGES = 6

    # ===============================
    # 🌍 1️⃣ TRANSLATE INPUT (Typed OR Voice)
    # ===============================
    english_question = sarvam_translate_to_english(question)

    # ===============================
    # 🔐 LOAD THREAD
    # ===============================
    thread_data = load_thread(thread_id, user_id)
    summary = thread_data.get("summary", "")
    messages = thread_data.get("messages", [])

    # Store ORIGINAL user message (for UI display)
    messages.append({
        "role": "user",
        "content": question
    })

    # ===============================
    # 🧠 2️⃣ STRUCTURED MEMORY EXTRACTION
    # ===============================

    new_memory = extract_structured_memory(question)

    if isinstance(new_memory, dict):
        for key, value in new_memory.items():
            if value:
                save_memory(user_id, key, str(value))

    # ===============================
    # 🧠 3️⃣ CONVERSATION SUMMARIZATION
    # ===============================

    if len(messages) > MAX_MESSAGES:
        old_messages = messages[:-MAX_MESSAGES]
        recent_messages = messages[-MAX_MESSAGES:]

        summary = summarize_conversation(summary, old_messages)
        messages = recent_messages

    # ===============================
    # 🔎 4️⃣ DOCUMENT RETRIEVAL (THREAD + USER ISOLATED)
    # ===============================

    query_embedding = generate_embedding(english_question)

    relevant_chunks = search(
        user_id=user_id,
        thread_id=thread_id,
        query_embedding=query_embedding,
        doc_id=doc_id
    )

    document_context = "\n".join(relevant_chunks) if relevant_chunks else ""

    # ===============================
    # 🧠 5️⃣ LOAD USER MEMORY
    # ===============================

    memory_data = load_all_memory(user_id)

    memory_text = "\n".join(
        [f"{k}: {v}" for k, v in memory_data.items()]
    )

    # ===============================
    # 🧾 6️⃣ FORMAT RECENT HISTORY
    # ===============================

    history_text = "\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in messages]
    )

    # ===============================
    # 🎯 7️⃣ BUILD FINAL PROMPT
    # ===============================

    final_prompt = f"""
You are an intelligent and personalized AI assistant.

Guidelines:
- Use structured user memory if relevant.
- Use document context strictly when answering document-related questions.
- If no document context is available, rely on conversation and memory.
- Answer completely and clearly.
- Never cut responses midway.

User Memory:
{memory_text}

Conversation Summary:
{summary}

Recent Conversation:
{history_text}

Document Context:
{document_context}

Question:
{english_question}
"""

    # ===============================
    # 🤖 8️⃣ GENERATE ANSWER
    # ===============================

    answer = generate_answer(final_prompt, english_question)

    # ===============================
    # 💾 9️⃣ STORE ASSISTANT RESPONSE
    # ===============================

    messages.append({
        "role": "assistant",
        "content": answer
    })

    save_thread(thread_id, user_id, summary, messages)

    return {
        "user_id": user_id,
        "thread_id": thread_id,
        "memory_used": memory_data,
        "answer": answer
    }

@app.post("/voice-ask")
async def voice_ask(
    user_id: str,
    thread_id: str,
    audio: UploadFile = File(...)
):

    file_path = f"temp_{audio.filename}"

    with open(file_path, "wb") as f:
        f.write(await audio.read())

    raw_text = sarvam_speech_to_text(file_path)

    # ❌ REMOVE translation here
    return await ask_question(
        user_id=user_id,
        thread_id=thread_id,
        question=raw_text
    )

@app.get("/get-thread")
async def get_thread(user_id: str, thread_id: str):
    thread_data = load_thread(thread_id, user_id)

    return {
        "thread_id": thread_id,
        "summary": thread_data["summary"],
        "messages": thread_data["messages"]
    }

from fastapi import FastAPI
import sqlite3

@app.get("/list-threads")
async def list_threads(user_id: str):
    conn = sqlite3.connect("threads.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT thread_id 
        FROM threads
        WHERE user_id = ?
        ORDER BY rowid DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    threads = [row[0] for row in rows]

    return {"threads": threads}

@app.get("/list-documents")
async def list_documents(user_id: str):
    user_folder = f"uploads/{user_id}"

    if not os.path.exists(user_folder):
        return {"documents": []}

    files = [
        f for f in os.listdir(user_folder)
        if f.endswith(".pdf")
    ]

    return {"documents": files}