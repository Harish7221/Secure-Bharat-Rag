# 🇮🇳 Secure Bharat Doc – Multilingual AI RAG Assistant

## 🎥 Live Demo

[![Watch Demo]](https://youtu.be/JZJwPSGBLFA)

---

Secure Bharat Doc is a multilingual AI-powered document intelligence system designed to securely process and understand Indian government documents in multiple languages.

Built for AI for Bharat Hackathon 🚀

---

## 🔥 Features

- 📄 Upload PDF documents (any Indian language)
- 🌍 Automatic translation to English (Sarvam AI)
- 🧠 RAG-based question answering (FAISS + Gemini)
- 🗂 Thread-based conversations
- 🧩 Structured memory extraction
- 🔐 User-specific document isolation
- 🗃 Persistent conversation storage
- 🌐 Streamlit chat interface
- ⚡ FastAPI backend

---

## 🏗 Architecture

Frontend:
- Streamlit

Backend:
- FastAPI

AI Models:
- Google Gemini (LLM)
- Sarvam AI (Translation + Speech-to-text)
- Sentence Transformer (Embeddings)

Vector Database:
- FAISS (per-user isolated storage)

Database:
- SQLite (thread & memory storage)

---

## 🔄 How It Works

1. User uploads a document
2. Document text is extracted
3. If not English → translated using Sarvam AI
4. Text is chunked
5. Embeddings are generated
6. Stored in FAISS vector store
7. User asks question
8. Relevant chunks retrieved
9. Gemini generates contextual answer
10. Conversation summary + memory stored

---

## 📂 Project Structure

```
Secure-Bharat-Doc/
│
├── app/
│   ├── main.py
│   ├── gemini_utils.py
│   ├── sarvam_utils.py
│   ├── embedding_utils.py
│   ├── vector_store.py
│   ├── thread_store.py
│   ├── pdf_utils.py
│   └── chunking.py
│
├── frontend.py
├── README.md
├── .gitignore
```

---

## 🚀 Running Locally

### 1️⃣ Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd Secure-Bharat-Doc
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Create .env file

```
GEMINI_API_KEY=your_key_here
SARVAM_API_KEY=your_key_here
```

### 5️⃣ Run Backend

```bash
uvicorn app.main:app --reload
```

### 6️⃣ Run Frontend

```bash
streamlit run frontend.py
```

---

## 🔐 Security

- API keys stored securely in `.env`
- User-isolated vector storage
- No document mixing between threads
- Sensitive files excluded via `.gitignore`

---

## 🎯 Use Case

Designed for:
- Citizens uploading land documents
- Government document simplification
- Multilingual document understanding
- AI for Bharat applications

---

## 📌 Future Improvements

- AWS deployment
- Amazon Bedrock integration
- DynamoDB thread storage
- Voice input integration
- Multi-user authentication
- Scalable vector DB

---

## 👨‍💻 Built By

Harish D  
B.Tech CSE – AI/ML  
AI for Bharat Hackathon Submission 🚀
