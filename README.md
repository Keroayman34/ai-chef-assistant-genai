# AI Chef Assistant → Nutrition AI Agent → RAG Agent

An evolving Generative AI project built across Advanced GenAI labs.

This project was developed progressively over 3 stages:

- Day 1: AI Chef Assistant (LLM + Workflow)
- Day 2: Nutrition Agent (Tools + Agentic AI)
- Day 3: RAG Agent (Multi-source retrieval + reasoning)

---

# Project Overview

This project demonstrates how a simple LLM application evolves into a full **Agentic AI system**.

It combines:
- Memory
- Tool usage
- Context engineering
- Retrieval (RAG)
- Multi-source reasoning

---

# Features

## Day 1 — AI Chef Assistant

- Accepts ingredients (text + optional image)
- Follows strict step-by-step workflow:
  1. Analyze ingredients
  2. Suggest meals
  3. Ask user preference
  4. Confirm meal
  5. Return recipe
- Human-like chef persona
- Structured output (Pydantic)
- Memory using `thread_id`
- OpenAI + Ollama support

---

## Day 2 — Nutrition AI Agent

Extended the assistant into an Agent:

- Nutrition analysis (calories, protein, carbs, fat)
- Meal recommendations
- Tool calling system
- Search tool (restaurants / groceries)
- CSV storage tool (nutrition logs)
- Context optimization (message trimming + summarization)
- Multi-modal food understanding

---

## Day 3 — RAG Multi-Source Agent

Upgraded into a Retrieval-Augmented Generation (RAG) system:

### Multi-Source Knowledge

Agent can retrieve information from:

- Local files (knowledge base)
- Database (structured data)
- Online search (external info)

---

### Intelligent Tool Selection

Agent decides dynamically:

- Use database → for structured nutrition facts  
- Use local files → for general knowledge  
- Use search → for up-to-date information  

---

### RAG Capabilities

- Local document retrieval
- Query-based search
- Context-aware responses
- Source attribution (file / db / search)

---

# Tech Stack

## Backend
- Python
- LangChain
- LangGraph (memory)
- FastAPI
- Pydantic
- python-dotenv

## Frontend
- React
- Vite
- Tailwind CSS

## Models
- OpenAI (GPT-4o-mini)
- Ollama (Mistral)

---

# Project Structure

```bash
.
├── app.py
├── chef_agent.py
├── schemas.py
├── config.py
├── utils.py
├── tools.py            # Day2 tools
├── middleware.py       # Context optimization
├── rag.py              # Day3 retrieval logic
├── db.py               # Local database
├── data/               # Local knowledge files
│
├── backend_api/
│   └── main.py
│
├── frontend/
├── requirements.txt
└── README.md
```

---

# Architecture

```text
User
↓
CLI / React UI
↓
FastAPI Backend
↓
AI Agent
├── Memory (LangGraph)
├── Tool Calling
├── RAG (Files + DB + Search)
└── Structured Output
```

---

# Setup

## 1 Install dependencies

```bash
pip install -r requirements.txt
```

---

## 2 Setup environment variables

Create `.env`:

```env
OPENAI_API_KEY=your_key_here
```

---

# Run Project

## CLI Version

```bash
python app.py
```

---

## FastAPI Backend

```bash
uvicorn backend_api.main:app --reload
```

---

## React Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on:
```
http://127.0.0.1:5173
```

---

# Example Flow

```text
User inputs meal
↓
Agent analyzes nutrition
↓
User asks for healthy options
↓
Agent decides:
   → search tool OR
   → database OR
   → local files
↓
Agent responds with best source
```

---

# Concepts Covered

## Day 1
- Prompt Engineering
- Structured Output
- Memory
- Multimodal Input

## Day 2
- Agents
- Tool Calling
- Context Engineering
- Middleware

## Day 3
- RAG (Retrieval-Augmented Generation)
- Multi-source reasoning
- Tool selection logic
- Knowledge integration

---

# Safety

- No medical diagnosis
- No strict diet plans

Disclaimer:

```
This is not medical advice.
Consult a professional for dietary decisions.
```

---

# Git Workflow

```bash
main
feature/day1-chef
feature/day2-nutrition-agent
feature/day3-rag-agent
```

---

# Future Improvements

- Vector database (FAISS / Chroma)
- RAG embeddings
- Multi-agent systems
- Personalized nutrition planning
- Dashboard analytics

---

# Summary

This project demonstrates the transition from:

```
LLM → Agent → RAG System
```

and reflects real-world GenAI application architecture.

---

Built as part of Advanced Generative AI Labs.
