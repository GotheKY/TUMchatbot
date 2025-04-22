from openai import OpenAI
from dotenv import load_dotenv
import os

# ✅ 先加载 .env 文件
load_dotenv()

# ✅ 再获取 API Key
api_key = os.getenv("OPENAI_API_KEY")

# ✅ 最后初始化客户端
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file!")

client = OpenAI(api_key=api_key)

def ask_gpt(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # 可换为 "gpt-4" 或 "gpt-4o"
            messages=[
                {"role": "system", "content": "You are a helpful assistant for answering course-related questions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return "Sorry, I couldn't retrieve an answer at the moment."
