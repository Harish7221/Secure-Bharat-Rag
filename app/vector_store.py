import faiss
import numpy as np
import os
import pickle

BASE_PATH = "vector_store"
DIMENSION = 384


# ==========================================
# 📁 Path Manager (User + Thread Scoped)
# ==========================================

def get_thread_paths(user_id, thread_id):
    thread_folder = os.path.join(BASE_PATH, user_id, thread_id)
    os.makedirs(thread_folder, exist_ok=True)

    index_path = os.path.join(thread_folder, "index.faiss")
    metadata_path = os.path.join(thread_folder, "metadata.pkl")

    return index_path, metadata_path


# ==========================================
# ➕ Add Embeddings (Thread Scoped)
# ==========================================

def add_embeddings(user_id, thread_id, doc_id, embeddings, chunks, filename=None):

    index_path, metadata_path = get_thread_paths(user_id, thread_id)

    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(DIMENSION)
        metadata = []

    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)

    for chunk in chunks:
        metadata.append({
            "text": chunk,
            "doc_id": doc_id,
            "filename": filename
        })

    faiss.write_index(index, index_path)

    with open(metadata_path, "wb") as f:
        pickle.dump(metadata, f)

    return doc_id


# ==========================================
# 🔎 Search (Thread Scoped)
# ==========================================

def search(user_id, thread_id, query_embedding, doc_id=None, top_k=5):

    index_path, metadata_path = get_thread_paths(user_id, thread_id)

    if not os.path.exists(index_path):
        return []

    index = faiss.read_index(index_path)

    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    query_vector = np.array([query_embedding]).astype("float32")

    distances, indices = index.search(query_vector, top_k)

    results = []

    for idx in indices[0]:
        if idx < len(metadata):

            # If filtering by specific document
            if doc_id:
                if metadata[idx]["doc_id"] == doc_id:
                    results.append(metadata[idx]["text"])
            else:
                results.append(metadata[idx]["text"])

    return results