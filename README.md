# 🏥 MediBot Pro v2.0
> **Industry-Level Medical RAG Assistant**
> A production-ready, highly secure Retrieval-Augmented Generation (RAG) chatbot designed specifically for healthcare knowledge retrieval. 

![MediBot Pro UI Screenshot](https://via.placeholder.com/800x400?text=MediBot+Pro+v2.0+UI)

## 🌟 Overview
MediBot Pro is a full-stack, AI-powered medical assistant. Unlike basic generic wrappers around ChatGPT, MediBot Pro is engineered with **Zero-Hallucination** in mind. It uses a custom Hybrid Search RAG pipeline drawing exclusively from verified medical literature (The Gale Encyclopedia of Medicine) and implements rigorous **Clinical Safety Guardrails** to prevent unauthorized diagnosing or prescribing.

## 🏗️ Architecture

- **Backend Framework:** FastAPI (Asynchronous, High-Performance)
- **Frontend Framework:** React 18 + Vite (TailwindCSS Styling)
- **Vector Database:** Pinecone v8 (Serverless Indexing)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2` (Sentence Transformers)
- **Language Model:** Cohere Command-R Plus (`langchain-cohere`)
- **Streaming Logic:** LangChain Expression Language (LCEL) with Server-Sent Events (SSE)

## 🛡️ Industry-Level Features

1. **Medical Liability Safety Filters:** Custom regex and keyword interception layers explicitly prevent the AI from generating unauthorized medical prescriptions or providing definitive automated diagnoses.
2. **Emergency Protocol Routing:** Instantly detects high-risk keywords (e.g., "heart attack", "stroke") and bypasses the AI entirely to instruct the user to contact emergency services (112/911).
3. **Hybrid Ensemble Retrieval:** Utilizes a custom `EnsembleRetrieverSimple` linking dense semantic search (Pinecone) and sparse keyword matching (BM25) to accurately surface complex medical jargon.
4. **Streamed Token Generation:** Real-time token parsing directly to the React frontend prevents UI locking and provides a seamless user experience.
5. **DDoS & Rate Limiting Protection:** Implements `slowapi` to enforce strict IP-based rate limiting on the chat endpoint protecting against API-exhaustion attacks.

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js v18+
- API Keys for Pinecone and Cohere.

### 1. Clone & Setup Backend
```bash
git clone https://github.com/daksh77arora/cura-medical-chatbot.git
cd cura-medical-chatbot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory:
```env
PINECONE_API_KEY=your_pinecone_key
COHERE_API_KEY=your_cohere_key
```

### 3. Data Ingestion
To populate your Pinecone database with the medical text, place your `Medical_book.pdf` in the `data/` folder and run:
```bash
python store_index.py
```

### 4. Run the Application
**Start the FastAPI Backend (Port 8080):**
```bash
python run_backend.py
```

**Start the React Frontend (Port 5173):**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Deployment

### Frontend (Vercel)
The React frontend is optimized for deployment on Vercel. 
1. Push your code to GitHub.
2. Sign in to [Vercel](https://vercel.com) and create a new project from your GitHub repository.
3. Set the Root Directory to `frontend`.
4. The Framework Preset should automatically be detected as `Vite`.
5. In Environment Variables, add your backend API URL (e.g., `VITE_API_URL=https://your-backend.com`).
6. Deploy!

### Backend (Render / Railway / AWS)
Due to the size of the ML dependencies and long-running requests for Retrieval, deploy the FastAPI backend on a dedicated server or container service like Render, Railway, or AWS EC2:
1. Connect your repository to the hosting platform.
2. Set the Environment Variables (`PINECONE_API_KEY`, `COHERE_API_KEY`).
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `python run_backend.py` (or `uvicorn app.main:app --host 0.0.0.0 --port 8080`).

## 📝 Disclaimer
*This project is built for educational and portfolio purposes only. It is not intended to replace professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified health provider with any questions you may have regarding a medical condition.*
