# EduAssist-AI: Coaching Chatbot

EduAssist-AI is a high-performance, decoupled AI chatbot built specifically for educational institutes and coaching centers. It leverages **Retrieval-Augmented Generation (RAG)** to provide highly accurate, hallucination-free answers about institute policies, admissions, and fees, while also serving as a capable academic tutor for allowed subjects.

## 🚀 Key Features

- **Decoupled Architecture**: Pure RESTful Python Flask API backend communicating securely with a static HTML/JS frontend via configured CORS.
- **Retrieval-Augmented Generation (RAG)**: The AI dynamically searches a local Knowledge Base and injects context into its system prompt to answer administrative questions with 100% accuracy.
- **SaaS Admin Dashboard**: A beautifully designed, secure portal for institute administrators to manage the Knowledge Base, view real-time Student Chat Logs, and control allowed tutoring subjects.
- **High Concurrency SQLite**: Optimized database using Write-Ahead Logging (WAL) and SQLAlchemy engine configurations to handle dozens of simultaneous student chats without database locks.
- **Intelligent Routing System**: Automatically classifies student queries (Admin vs. Academic) and routes them to specialized LLM prompts for optimized token usage and speed.
- **Persistent Memory**: Session-based memory allows the AI to remember the last 4 exchanges to answer conversational follow-up questions seamlessly.

## 🛠️ Tech Stack

- **Backend:** Python 3.10, Flask, Flask-CORS, SQLite
- **Frontend:** HTML5, CSS3, Vanilla JS, DOMPurify, Marked.js, KaTeX (for mathematical rendering)
- **Database:** SQLite
- **AI Integration:** Groq AI (using ultra-fast Qwen 3.8-27b models)

## 📦 Deployment & Architecture

This project is designed for a split-deployment model:
1. **Frontend:** Hosted globally on **GitHub Pages** for ultra-fast static delivery.
2. **Backend API & Admin:** Hosted on **PythonAnywhere**, serving REST endpoints.

## ⚙️ Local Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/EduAssist-AI.git
   cd EduAssist-AI
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Set up the database and create the admin account:
   ```bash
   python seed.py
   ```
4. Create a `.env` file with your API keys:
   ```text
   GROQ_API_KEY=your_groq_api_key
   SECRET_KEY=dev-secret-key
   ```
5. Run the API server:
   ```bash
   python app.py
   ```
6. Open `index.html` in your browser to test the frontend!

7. Default Password-
usrname- username
password- ChangeMe123!
---
*Built with ❤️ to student support.*
