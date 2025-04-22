import os
import pickle
import fitz  # PyMuPDF
import faiss
import numpy as np
from docx import Document
from typing import List
import tiktoken
from openai import OpenAI
from dotenv import load_dotenv
# OpenAI client (new SDK v1.0+ style)
# ✅ 先加载 .env 文件
load_dotenv()

# ✅ 再获取 API Key
api_key = os.getenv("OPENAI_API_KEY")

# ✅ 最后初始化客户端
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file!")

client = OpenAI(api_key=api_key)
embedding_model = "text-embedding-ada-002"

def split_text(text, max_tokens=500):
    enc = tiktoken.get_encoding("cl100k_base")
    paragraphs = text.split("\n")
    chunks, current_chunk = [], ""
    for p in paragraphs:
        if not p.strip():
            continue
        candidate = current_chunk + "\n" + p if current_chunk else p
        if len(enc.encode(candidate)) > max_tokens:
            chunks.append(current_chunk.strip())
            current_chunk = p
        else:
            current_chunk = candidate
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def extract_text_from_files(paths: List[str]):
    documents = []
    for path in paths:
        if path.endswith(".pdf"):
            with fitz.open(path) as pdf:
                text = "\n".join(page.get_text() for page in pdf)
                documents.append((os.path.basename(path), text))
        elif path.endswith(".docx"):
            doc = Document(path)
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
            documents.append((os.path.basename(path), text))
    return documents

def embed_texts(texts: List[str]) -> List[List[float]]:
    results = []
    for i in range(0, len(texts), 20):
        batch = texts[i:i+20]
        resp = client.embeddings.create(input=batch, model=embedding_model)
        results.extend([d.embedding for d in resp.data])
    return results

def build_faiss_index(doc_paths: List[str], index_path="pdf_index.faiss", chunk_path="pdf_chunks.pkl"):
    docs = extract_text_from_files(doc_paths)
    all_chunks, metadata = [], []

    for source, full_text in docs:
        chunks = split_text(full_text)
        all_chunks.extend(chunks)
        metadata.extend([source] * len(chunks))

    embeddings = embed_texts(all_chunks)
    dim = len(embeddings[0])
    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))

    with open(chunk_path, "wb") as f:
        pickle.dump((all_chunks, metadata), f)
    faiss.write_index(index, index_path)

def get_rag_answer(query, index_path="pdf_index.faiss", chunk_path="pdf_chunks.pkl", top_k=5):
    index = faiss.read_index(index_path)
    with open(chunk_path, "rb") as f:
        chunks, metadata = pickle.load(f)

    query_embedding = client.embeddings.create(input=[query], model=embedding_model).data[0].embedding
    D, I = index.search(np.array([query_embedding]).astype("float32"), top_k)

    retrieved = [f"From {metadata[i]}:\n{chunks[i]}" for i in I[0]]
    context = "\n\n".join(retrieved)

    messages = [
        {"role": "system", "content": "You are a helpful assistant who answers based on course documents."},
        {"role": "user", "content": f"Answer the question using the following context:\n{context}\n\nQuestion: {query}"}
    ]
    response = client.chat.completions.create(model="gpt-3.5-turbo", messages=messages)
    return response.choices[0].message.content
