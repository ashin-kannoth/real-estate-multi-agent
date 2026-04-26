# 🏠 Real Estate Multi-Agent AI System

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.136-green)
![LangGraph](https://img.shields.io/badge/LangGraph-1.1-orange)
![ChromaDB](https://img.shields.io/badge/ChromaDB-1.5-purple)

## 🚀 Overview

This project implements a **federated multi-agent system** for a real estate platform using the **A2A (Agent-to-Agent) Protocol**.

It demonstrates:
- ✅ Multi-agent architecture with independent deployable services
- ✅ Agent-to-Agent (A2A) communication via Agent Cards
- ✅ Workflow orchestration using **LangGraph StateGraph**
- ✅ RAG (Retrieval-Augmented Generation) pipeline with **ChromaDB**
- ✅ Microservices-based AI system design

---

## 🧠 Architecture

```
User Request
     │
     ▼
┌─────────────────────┐
│   Concierge Agent   │  ← Orchestrator (Port 8000)
│   (LangGraph)       │
└──────────┬──────────┘
           │
    ┌──────┴──────┐
    │  Intent Detection  │
    └──────┬──────┘
           │
    ┌──────▼──────────────────────┐
    │                             │
    ▼                             ▼
Customer Agent            Deal Agent
(Port 8001)               (Port 8002)
    │                             │
    ▼                             ▼
Store to DB              Store to DB
Return Customer ID        Trigger Marketing Agent
                                  │
                                  ▼
                         Marketing Agent
                         (Port 8003)
                                  │
                                  ▼
                         Generate AI Insights
                         Store in ChromaDB (RAG)
```

---

## 🤖 Agents

### 1. 🎯 Concierge Agent (Orchestrator) — Port 8000
- Central entry point for all user requests
- Discovers agents dynamically via Agent Cards
- Detects user intent (onboard customer / property / query)
- Routes requests to correct specialized agents
- Aggregates and returns final responses using LLM

### 2. 👤 Customer Onboarding Agent — Port 8001
- Collects and validates customer data
- Stores data in SQLite database
- Generates unique **Customer ID**
- Validates required fields and budget ranges

### 3. 🏠 Deal (Property) Onboarding Agent — Port 8002
- Collects and validates property data
- Stores structured property info in SQLite
- Generates unique **Property ID**
- **Auto-triggers** Marketing Intelligence Agent

### 4. 📊 Marketing Intelligence Agent — Port 8003
- Generates AI-powered real estate market insights
- Chunks insights and converts to embeddings
- Stores in **ChromaDB** vector database
- Supports RAG-based query responses
- Prevents duplicate property processing

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend Framework | FastAPI |
| Orchestration | LangGraph (StateGraph) |
| AI Framework | LangChain |
| LLM | OpenAI GPT-4o |
| Vector Database | ChromaDB |
| Embeddings | OpenAI Embeddings |
| Persistence | SQLite (SQLAlchemy) |
| Protocol | A2A (Agent-to-Agent) |
| Language | Python 3.11 |

---

## 📁 Project Structure

```
real-estate-multi-agent/
│
├── concierge-agent/
│   ├── main.py                    # Orchestrator with LangGraph
│   └── __init__.py
│
├── customer-onboarding-agent/
│   ├── main.py                    # Customer A2A Server
│   └── __init__.py
│
├── deal-onboarding-agent/
│   ├── main.py                    # Property A2A Server
│   └── __init__.py
│
├── marketing-intelligence-agent/
│   ├── main.py                    # RAG + Insights A2A Server
│   └── __init__.py
│
├── shared_utils/
│   ├── database.py                # SQLAlchemy models
│   ├── models.py                  # Pydantic schemas
│   └── __init__.py
│
├── .env.example                   # Environment variables template
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## ▶️ How to Run

### Step 1: Clone the repository

```bash
git clone https://github.com/ashin-kannoth/real-estate-multi-agent.git
cd real-estate-multi-agent
```

### Step 2: Create virtual environment

```bash
python -m venv venv
```

**Activate (Windows):**
```bash
venv\Scripts\activate
```

**Activate (Mac/Linux):**
```bash
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set up environment variables

Create a `.env` file in the root folder:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### Step 5: Run all agents (4 separate terminals)

**Terminal 1 — Customer Onboarding Agent:**
```bash
cd customer-onboarding-agent
python -m uvicorn main:app --port 8001 --reload
```

**Terminal 2 — Deal Onboarding Agent:**
```bash
cd deal-onboarding-agent
python -m uvicorn main:app --port 8002 --reload
```

**Terminal 3 — Marketing Intelligence Agent:**
```bash
cd marketing-intelligence-agent
python -m uvicorn main:app --port 8003 --reload
```

**Terminal 4 — Concierge Agent (start last):**
```bash
cd concierge-agent
python -m uvicorn main:app --port 8000 --reload
```

---

## 🧪 API Testing

Open Swagger UI in browser:
```
http://127.0.0.1:8000/docs
```

---

### 🔹 Test 1: Onboard a Customer

**POST** `http://127.0.0.1:8000/chat`

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "9876543210",
  "budget": 500000,
  "preferred_location": "Dubai Marina"
}
```

**Expected Response:**
```json
{
  "response": "Customer John Doe has been successfully onboarded. Customer ID: abc-123"
}
```

---

### 🔹 Test 2: Onboard a Property

**POST** `http://127.0.0.1:8000/chat`

```json
{
  "title": "Luxury Sunset Villa",
  "location": "Dubai Marina",
  "price": 450000,
  "area": 1800,
  "bedrooms": 3,
  "property_type": "villa"
}
```

**Expected Response:**
```json
{
  "response": "Property 'Luxury Sunset Villa' onboarded. Property ID: xyz-456. Market analysis triggered."
}
```

---

### 🔹 Test 3: Query Market Insights (RAG)

**POST** `http://127.0.0.1:8000/chat`

```json
{
  "query": "Is Dubai Marina a good real estate investment?"
}
```

**Expected Response:**
```json
{
  "response": "Dubai Marina is a high-demand real estate market with strong investment potential..."
}
```

---

### 🔹 Test 4: Check Registered Agents

**GET** `http://127.0.0.1:8000/agents`

```json
{
  "registered_agents": ["customer", "deal", "marketing"]
}
```

---

### 🔹 Test 5: Check Agent Card

**GET** `http://127.0.0.1:8000/.well-known/agent.json`

```json
{
  "name": "Concierge Agent",
  "description": "Central orchestrator for the real estate platform",
  "url": "http://localhost:8000",
  "version": "1.0.0"
}
```

---

## 📊 Sample Output

```
✅ Discovered: Customer Onboarding Agent
✅ Discovered: Deal Onboarding Agent
✅ Discovered: Marketing Intelligence Agent
🎯 Intent detected: onboard_property
✅ Property onboarded: xyz-456 - Luxury Sunset Villa
📊 Marketing agent triggered for property: xyz-456
✅ Insights stored for property: xyz-456 (4 chunks)
🔍 RAG query returned 3 results
```

---

## 🔁 Workflow Flow

```
Customer Flow:
User Input → Concierge → Customer Agent → SQLite DB → Customer ID

Property Flow:
User Input → Concierge → Deal Agent → SQLite DB → Property ID
                                    → Marketing Agent (auto-trigger)
                                    → Generate AI Insights
                                    → ChromaDB (embeddings)

Query Flow:
User Query → Concierge → Marketing Agent (RAG)
           → ChromaDB similarity search
           → LLM response generation
           → Final Answer
```

---

## 🌐 Agent Cards (A2A Protocol)

Each agent exposes its capabilities at `/.well-known/agent.json`:

| Agent | URL | Agent Card |
|-------|-----|------------|
| Concierge | http://localhost:8000 | `/.well-known/agent.json` |
| Customer | http://localhost:8001 | `/.well-known/agent.json` |
| Deal | http://localhost:8002 | `/.well-known/agent.json` |
| Marketing | http://localhost:8003 | `/.well-known/agent.json` |

---

## 🎯 Key Features

- 🤖 **Distributed AI system** — 4 independent microservices
- 🔗 **A2A Protocol** — Structured agent communication via Agent Cards
- 🧩 **LangGraph orchestration** — StateGraph-based workflow management
- 🔍 **RAG pipeline** — ChromaDB vector search for intelligent responses
- 💾 **Persistent storage** — SQLite database for customers and properties
- 📝 **Logging** — Full observability across all agents
- 🔄 **Auto-triggering** — Deal Agent automatically triggers Marketing Agent
- 📖 **Swagger UI** — Interactive API documentation

---

## 👨‍💻 Author

**Ashin K**

---

## 💼 Resume Line

> Built a federated multi-agent real estate AI system using FastAPI, LangGraph, and ChromaDB, implementing A2A communication protocol, RAG pipeline, and microservice orchestration for intelligent property market insights.
