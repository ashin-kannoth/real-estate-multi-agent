# 🏠 Real Estate Multi-Agent AI System

## 🚀 Overview
This project implements a **federated multi-agent system** for a real estate platform using the **A2A (Agent-to-Agent) protocol**.

It demonstrates:
- Agent orchestration
- Microservices communication
- RAG (Retrieval-Augmented Generation)
- Real-world AI system design

---

## 🧠 Architecture

### Agents

1. **Concierge Agent**
   - Central orchestrator
   - Detects intent
   - Routes requests
   - Aggregates responses

2. **Customer Onboarding Agent**
   - Collects user data
   - Generates Customer ID

3. **Deal (Property) Agent**
   - Stores property data
   - Generates Property ID
   - Triggers marketing agent

4. **Marketing Intelligence Agent**
   - Generates insights
   - Stores in vector DB (ChromaDB)
   - Supports RAG queries

---

## 🔁 Workflow

User → Concierge  
→ Detect intent  
→ Route to agent  

Property Flow:
User → Deal Agent → Marketing Agent → Store in Vector DB  

Query Flow:
User → Concierge → Marketing Agent (RAG) → Return insights  

---

## ⚙️ Tech Stack

- FastAPI  
- LangGraph  
- LangChain  
- ChromaDB  
- Python  

---

## 🧪 Features

- Multi-agent architecture  
- A2A communication  
- RAG pipeline  
- Microservices design  
- API-based system  

---

## ▶️ Run the Project

Open 4 terminals:

### Terminal 1
```bash
cd customer-onboarding-agent
uvicorn main:app --port 8001 --reload
