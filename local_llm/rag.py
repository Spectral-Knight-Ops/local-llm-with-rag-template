"""
rag.py
- Persistent Chroma indexing + retrieval helper with optional Ollama or Sentence-Transformers embeddings.
- Exposes:
    initialize_index(docs_folder="docs", reindex=False, chunk_size_chars=2000)
    rag_query(query, n_results=3, model="llava-llama3:latest")
"""

import os
import glob
import traceback
from typing import List

# Try to import Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
except Exception:
    OLLAMA_AVAILABLE = False

# ChromaDB (new-style client)
try:
    import chromadb
except Exception as e:
    raise RuntimeError("Please install chromadb (`python -m pip install chromadb`)") from e

# Sentence-transformers fallback
try:
    from sentence_transformers import SentenceTransformer
    S2_AVAILABLE = True
except Exception:
    S2_AVAILABLE = False

# Config
COLLECTION_NAME = "llm_docs"

# Compute a stable absolute path for the persistent Chroma DB (project root / chroma_db)
# __file__ is local_llm/rag.py -> go up one level to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PERSIST_DIR = os.path.join(PROJECT_ROOT, "chroma_db")

# Make sure the folder exists (client will create it if necessary, but this makes path explicit)
os.makedirs(PERSIST_DIR, exist_ok=True)

# Create a persistent client (new Chroma API) using absolute path
try:
    client = chromadb.PersistentClient(path=PERSIST_DIR)
except Exception as e:
    raise RuntimeError(f"Failed to create Chroma PersistentClient at {PERSIST_DIR}: {e}") from e


def get_ollama_embedding(text: str) -> List[float]:
    """Return embedding vector using Ollama 'nomic-embed-text' (if available)."""
    if not OLLAMA_AVAILABLE:
        raise RuntimeError("Ollama python client not available.")
    resp = ollama.embeddings(model="nomic-embed-text", prompt=text)
    # Ollama client returns {"embedding": [...]}
    return resp["embedding"]


def get_sentence_transformer_embedding(embedder, text: str) -> List[float]:
    vec = embedder.encode([text])[0]
    return vec.tolist() if hasattr(vec, "tolist") else list(vec)


def chunk_text(text: str, chunk_size_chars: int = 2000, overlap_chars: int = 200) -> List[str]:
    """
    Simple chunker that splits text into chunks of ~chunk_size_chars with overlap.
    Splits preferentially on paragraph/newline boundaries where possible.
    """
    if len(text) <= chunk_size_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if not current:
            current = p
            continue
        # if adding paragraph stays within size, append
        if len(current) + 2 + len(p) <= chunk_size_chars:
            current = current + "\n\n" + p
        else:
            # flush current chunk
            chunks.append(current)
            # start new with some overlap from end of current
            if overlap_chars > 0:
                overlap = current[-overlap_chars:]
                current = overlap + "\n\n" + p
            else:
                current = p
    if current:
        chunks.append(current)

    # As fallback, if any chunk > chunk_size_chars, perform hard-split
    final_chunks = []
    for c in chunks:
        if len(c) <= chunk_size_chars:
            final_chunks.append(c)
        else:
            # hard split by characters
            start = 0
            L = len(c)
            while start < L:
                part = c[start:start + chunk_size_chars]
                final_chunks.append(part)
                start += chunk_size_chars - overlap_chars
    return final_chunks


def initialize_index(docs_folder: str = "docs", reindex: bool = False, chunk_size_chars: int = 2000):
    """
    Create or load a Chroma collection and index all .txt files inside docs_folder.
    If reindex=True, the existing collection is deleted and rebuilt.
    """
    os.makedirs(docs_folder, exist_ok=True)

    # create/get collection (PersistentClient provides list_collections/get_collection/create_collection)
    try:
        existing_cols = [c.name for c in client.list_collections()]
    except Exception:
        existing_cols = []

    if reindex and COLLECTION_NAME in existing_cols:
        try:
            client.delete_collection(COLLECTION_NAME)
            existing_cols = [c.name for c in client.list_collections()]
        except Exception:
            pass

    if COLLECTION_NAME in existing_cols:
        collection = client.get_collection(name=COLLECTION_NAME)
    else:
        collection = client.create_collection(name=COLLECTION_NAME)

    # Check existing item count
    try:
        existing_count = len(collection.get()['ids'])
    except Exception:
        existing_count = 0

    if existing_count > 0 and not reindex:
        print(f"Chroma collection '{COLLECTION_NAME}' already has {existing_count} items. Skipping indexing.")
        return collection

    # Determine embedding mechanism
    use_ollama = False
    if OLLAMA_AVAILABLE:
        try:
            _ = get_ollama_embedding("test")
            use_ollama = True
            print("Using Ollama 'nomic-embed-text' for embeddings.")
        except Exception:
            print("Ollama client available but 'nomic-embed-text' not usable; falling back to sentence-transformers if available.")

    embedder = None
    if not use_ollama:
        if not S2_AVAILABLE:
            raise RuntimeError("No usable embedder found. Install sentence-transformers or set up Ollama embedding model 'nomic-embed-text'.")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        print("Using Sentence-Transformers 'all-MiniLM-L6-v2' for embeddings (download on first run).")

    # Gather text files
    txt_files = sorted(glob.glob(os.path.join(docs_folder, "*.txt")))
    if not txt_files:
        print(f"No .txt files found in {docs_folder}. Add files and run initialize_index() again.")
        return collection

    docs = []
    ids = []
    metadata = []
    embeddings = []

    doc_counter = 0
    for path in txt_files:
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            text = fh.read().strip()
        if not text:
            continue

        # chunk the document to smaller pieces for better retrieval
        chunks = chunk_text(text, chunk_size_chars=chunk_size_chars, overlap_chars=int(chunk_size_chars * 0.1))
        for i, chunk in enumerate(chunks):
            docs.append(chunk)
            ids.append(f"{os.path.basename(path)}__{i}")
            metadata.append({"source": os.path.basename(path), "chunk_index": i})
            # compute embedding
            if use_ollama:
                emb = get_ollama_embedding(chunk)
                embeddings.append(emb)
            else:
                emb = get_sentence_transformer_embedding(embedder, chunk)
                embeddings.append(emb)
            doc_counter += 1

    # (Re)create collection and add
    try:
        if COLLECTION_NAME in [c.name for c in client.list_collections()]:
            client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(name=COLLECTION_NAME)
    collection.add(documents=docs, embeddings=embeddings, ids=ids, metadatas=metadata)
    # persist (PersistentClient persists to path automatically; but call persist if available)
    try:
        client.persist()
    except Exception:
        pass

    print(f"Indexed {doc_counter} chunks from {len(txt_files)} files into Chroma collection '{COLLECTION_NAME}' (persist dir: {PERSIST_DIR}).")
    return collection

#The lines below allow you to change the model you are using. Make sure you did an ollama pull on the model so it is present
def rag_query(query: str, n_results: int = 3, model: str = "llava-llama3:latest"):
#def rag_query(query: str, n_results: int = 3, model: str = "gpt-oss:latest"):
    """
    Run a RAG query:
      - embed query
      - retrieve top n_results documents
      - build a prompt with retrieved context and call Ollama model
    Returns the model's text response.
    """
    collection = client.get_collection(name=COLLECTION_NAME)

    # embed query
    use_ollama = False
    if OLLAMA_AVAILABLE:
        try:
            q_emb = get_ollama_embedding(query)
            use_ollama = True
        except Exception:
            use_ollama = False

    if not use_ollama:
        if not S2_AVAILABLE:
            raise RuntimeError("No embedding option available for queries.")
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
        q_emb = get_sentence_transformer_embedding(embedder, query)

    # query chroma
    results = collection.query(query_embeddings=[q_emb], n_results=n_results)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    if not docs:
        context = ""
    else:
        context_pieces = []
        for d, m in zip(docs, metas):
            header = f"Source: {m.get('source','unknown')} (chunk {m.get('chunk_index','?')})\n"
            context_pieces.append(header + d)
        context = "\n\n---\n\n".join(context_pieces)

    # Build prompt. You can change the system instruction here to enforce safety / style.
    #ADJUST THIS FOR YOUR SPECIFIC USAGE
    prompt = (
        "You are a helpful red-team assistant. Use the contextual documents below to answer the question. "
        "If the documents do not contain the needed information, you may also use your general (pretrained) knowledge. "
        "Reference sources from the context when used, and include safety/authorization reminders for risky actions.\n\n"
        f"{context}\n\nQuestion: {query}\n\nAnswer concisely and reference sources if appropriate."
    )

    # Call Ollama model for generation
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return f"[RAG -> Ollama error] {e}\n{traceback.format_exc()}"


# If run directly, index docs folder and test one query. This can be run directly to ensure pipeline is good to go
if __name__ == "__main__":
    col = initialize_index("docs", reindex=False)
    print("Test query (if docs exist):")
    try:
        ans = rag_query("Hello, how are you doing today?", n_results=3)
        print(ans)
    except Exception as ex:
        print("RAG query failed:", ex)
