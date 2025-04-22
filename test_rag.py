from rag_utils import build_faiss_index, get_rag_answer

# Step 1: 构建向量索引（第一次运行）
document_paths = [
    "kursablauf.pdf",
    "lernhilfe.pdf",
    "course_summary.docx"
]
build_faiss_index(document_paths)

# Step 2: 用户问问题
question = "Wann ist die Klausur?"
answer = get_rag_answer(question)

print("Bot Antwort:")
print(answer)
