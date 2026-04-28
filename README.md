# AI Chef Assistant -> Nutrition AI Agent

Agentic Generative AI project built through Advanced GenAI labs.

Started as an AI Chef Assistant (Day 1) and evolved into a Nutrition AI Agent with tools, memory, context engineering, and fullstack UI (Day 2).

---

# Features

## Day 1 — AI Chef Assistant
- Ingredient analysis from text/image
- Guided meal workflow:
  1. Analyze ingredients  
  2. Suggest meals  
  3. User selects  
  4. Confirm meal  
  5. Return recipe  

- Conversation memory using thread_id  
- Structured outputs with Pydantic  
- OpenAI + Ollama support  
- CLI + React UI

---

## Day 2 — Nutrition AI Agent Upgrade
Added:

- Nutrition analysis (calories, protein, carbs, fat)
- Tool Calling Agent
- Healthy restaurant / grocery search tool
- CSV nutrition storage tool
- Context engineering
- Message trimming + summarization memory
- Multi-modal food analysis

Example:

```text
2 eggs, avocado toast, orange juice
```

Returns nutrition summary + recommendations.

---

# Tech Stack

## Backend
- Python
- LangChain
- LangGraph
- FastAPI
- Pydantic
- OpenAI / Ollama

## Frontend
- React
- Vite
- Tailwind

---

# Architecture

```text
User
↓
React / CLI
↓
FastAPI
↓
AI Agent
├─ Memory
├─ Tool Calling
├─ Context Optimization
└─ Structured Outputs
```

---

# Project Structure

```bash
app.py
chef_agent.py
schemas.py
config.py
utils.py
tools.py
middleware.py
backend_api/
frontend/
```

---

# Concepts Implemented

## Day 1
- Prompt Engineering
- Structured Outputs
- Memory
- Multimodal Inputs

## Day 2
- Agents
- Tools
- ReAct-style Tool Calling
- Context Engineering
- Middleware
- Summarization Memory

---

# Run Project

## Install

```bash
pip install -r requirements.txt
```

Create:

```env
OPENAI_API_KEY=your_key_here
```

---

## Run CLI

```bash
python app.py
```

---

## Run Backend

```bash
uvicorn backend_api.main:app --reload
```

Endpoints:

```http
POST /nutrition/analyze
POST /nutrition/search
POST /nutrition/store
GET /history/{thread_id}
```

---

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on:

```text
http://127.0.0.1:5173
```

---

# Example Flow

```text
User enters meal
↓
Agent analyzes nutrition
↓
User asks healthy nearby food
↓
Agent calls search tool
↓
User stores nutrition summary
```

---

# Safety
- No medical diagnosis
- No strict diet plans

Disclaimer:

```text
This is not medical advice.
Consult a qualified professional.
```

---

# Git Workflow

```bash
main
feature/backend-cli
feature/day2-nutrition-agent
```

---

# Future Roadmap
Planned:
- RAG
- Vector databases
- Long-term memory
- Multi-agent systems

Repository will continue evolving through the course.

---

Built as part of Advanced Generative AI labs.
