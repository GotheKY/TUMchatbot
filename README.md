# AI Guide Chatbot (Student Assistant)

## 🛠 How to Run

1. Install Python 3.8+ and pip
2. Set your OpenAI API key in the terminal:
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
   On Windows CMD:
   ```
   set OPENAI_API_KEY=your_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the server:
   ```
   python app.py
   ```
5. Open in browser:
   ```
   http://127.0.0.1:5000
   ```

## ✨ Features
- Answers course questions based on pre-defined FAQ
- Falls back to GPT response if no match found
