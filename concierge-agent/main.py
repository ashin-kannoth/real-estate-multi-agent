import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional
from dotenv import load_dotenv
import httpx, uuid, logging, traceback

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Concierge Agent")

# ------------------- Agent URLs -------------------
AGENTS = {
    "customer": "http://localhost:8001",
    "deal":     "http://localhost:8002",
    "marketing":"http://localhost:8003"
}

# ------------------- Discover Agents -------------------
def discover_agents():
    registry = {}
    for name, url in AGENTS.items():
        try:
            card = httpx.get(f"{url}/.well-known/agent.json", timeout=3).json()
            registry[name] = {"url": url, "card": card}
            logging.info(f"✅ Discovered: {card['name']}")
        except:
            logging.warning(f"⚠️ Could not reach {name} agent")
    return registry

registry = {}

# ------------------- State -------------------
class State(TypedDict):
    user_input:     dict
    intent:         str
    customer_id:    Optional[str]
    property_id:    Optional[str]
    rag_results:    Optional[list]
    final_response: Optional[str]

# ------------------- Intent Detection -------------------
def detect_intent(state: State) -> State:
    data = state["user_input"]

    if "name" in data and "email" in data:
        state["intent"] = "onboard_customer"
    elif "title" in data and "price" in data:
        state["intent"] = "onboard_property"
    else:
        state["intent"] = "query_insights"

    logging.info(f"🎯 Intent: {state['intent']}")
    return state

# ------------------- Call Agent -------------------
def call_agent(agent_name: str, skill_id: str, data: dict) -> dict:
    url = registry.get(agent_name, {}).get("url")

    if not url:
        return {"status": "failed", "output": {"error": f"{agent_name} not available"}}

    try:
        response = httpx.post(
            f"{url}/tasks/send",
            json={
                "task_id":  str(uuid.uuid4()),
                "skill_id": skill_id,
                "input":    data
            },
            timeout=30
        )
        return response.json()
    except Exception as e:
        logging.error(f"Agent call failed: {e}")
        return {"status": "failed", "output": {"error": str(e)}}

# ------------------- Route to Agents -------------------
def route_to_agent(state: State) -> State:
    intent = state["intent"]
    data   = state["user_input"]

    if intent == "onboard_customer":
        result = call_agent("customer", "onboard_customer", data)
        state["customer_id"] = result.get("output", {}).get("customer_id")
        logging.info(f"Customer result: {result}")

    elif intent == "onboard_property":
        result = call_agent("deal", "onboard_property", data)
        state["property_id"] = result.get("output", {}).get("property_id")
        logging.info(f"Property result: {result}")

    elif intent == "query_insights":
        result = call_agent("marketing", "query_insights", data)
        state["rag_results"] = result.get("output", {}).get("results", [])
        logging.info(f"RAG result: {result}")

    return state

# ------------------- Generate Response (FINAL FIX) -------------------
def generate_response(state: State) -> State:
    intent = state["intent"]
    rag_results = state.get("rag_results", [])

    # Customer response
    if intent == "onboard_customer":
        state["final_response"] = f"Customer created successfully with ID {state.get('customer_id')}"

    # Property response
    elif intent == "onboard_property":
        state["final_response"] = f"Property onboarded successfully with ID {state.get('property_id')}. Market insights generated."

    # RAG response
    elif intent == "query_insights":
        if rag_results:
            # ✅ remove duplicates while preserving order
            unique_insights = list(dict.fromkeys(rag_results))
            insights = "\n".join(unique_insights)

            state["final_response"] = f"Here are the insights:\n{insights}"
        else:
            state["final_response"] = "No insights found. Please onboard a property first."

    else:
        state["final_response"] = "Unknown request."

    return state

# ------------------- Build Graph -------------------
def build_graph():
    graph = StateGraph(State)

    graph.add_node("detect_intent",     detect_intent)
    graph.add_node("route_to_agent",    route_to_agent)
    graph.add_node("generate_response", generate_response)

    graph.set_entry_point("detect_intent")

    graph.add_edge("detect_intent", "route_to_agent")
    graph.add_edge("route_to_agent", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()

workflow = build_graph()

# ------------------- Startup -------------------
@app.on_event("startup")
def startup():
    global registry
    registry = discover_agents()

# ------------------- Agent Card -------------------
@app.get("/.well-known/agent.json")
def agent_card():
    return {
        "name": "Concierge Agent",
        "description": "Central orchestrator for the real estate platform",
        "url": "http://localhost:8000",
        "version": "1.0.0",
        "skills": [{"id": "orchestrate", "name": "Orchestrate All Tasks"}]
    }

# ------------------- Chat Endpoint -------------------
@app.post("/chat")
def chat(request: dict):
    try:
        logging.info(f"📨 Request: {request}")

        result = workflow.invoke({
            "user_input":     request,
            "intent":         "",
            "customer_id":    None,
            "property_id":    None,
            "rag_results":    None,
            "final_response": None
        })

        return {"response": result["final_response"]}

    except Exception as e:
        logging.error(f"❌ Chat error: {str(e)}")
        traceback.print_exc()
        return {"error": str(e), "traceback": traceback.format_exc()}

# ------------------- Utilities -------------------
@app.get("/agents")
def list_agents():
    return {"registered_agents": list(registry.keys())}

@app.get("/health")
def health():
    return {"status": "ok", "agent": "concierge"}