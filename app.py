from flask import Flask, render_template, request, jsonify
import pandas as pd
from openai_helper import ask_gpt
from rapidfuzz import fuzz
from rag_utils import get_rag_answer

app = Flask(__name__)

# Load FAQ data
faq_df = pd.read_csv("faq_data_enhanced.csv")

# Track conversation state for multi-turn logic
conversation_state = {
    "pending_question": None,
    "follow_up": None,
}

def get_best_matching_question(user_input):
    best_score = 0
    best_row = None
    for _, row in faq_df.iterrows():
        score = fuzz.token_sort_ratio(user_input.lower(), str(row["Question"]).lower())
        if score > best_score and score >= 85:
            best_score = score
            best_row = row
    return best_row

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("message").strip()
    global conversation_state

    # Step 1: Follow-up logic
    if conversation_state["pending_question"]:
        base_q = conversation_state["pending_question"]
        user_answer = user_input.lower()

        for _, row in faq_df.iterrows():
            if row["Question"].lower().strip() == base_q and str(row["Expected_Answer"]).lower().strip() == user_answer:
                conversation_state = {"pending_question": None, "follow_up": None}
                return jsonify({"reply": row["Bot_Reply"]})

        conversation_state = {"pending_question": None, "follow_up": None}
        # fallback to RAG
        rag_answer = get_rag_answer(user_input)
        return jsonify({"reply": rag_answer})

    # Step 2: FAQ matching
    row = get_best_matching_question(user_input)
    if row is not None:
        if pd.notna(row["Follow_Up"]):
            conversation_state["pending_question"] = row["Question"].lower().strip()
            conversation_state["follow_up"] = row["Follow_Up"]
            return jsonify({"reply": row["Follow_Up"]})
        else:
            return jsonify({"reply": row["Bot_Reply"]})

    # Step 3: Try RAG before GPT
    rag_answer = get_rag_answer(user_input)
    if rag_answer and len(rag_answer.strip()) > 20:
        return jsonify({"reply": rag_answer})

    return jsonify({"reply": ask_gpt(user_input)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Render 会传入 PORT 环境变量
    app.run(host="0.0.0.0", port=port, debug=True)
