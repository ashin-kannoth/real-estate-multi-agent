import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from shared_utils.database import Session, PropertyDB
import uuid, logging, httpx

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Deal Onboarding Agent")

@app.get("/.well-known/agent.json")
def agent_card():
    return {
        "name": "Deal Onboarding Agent",
        "description": "Handles property data collection and triggers marketing",
        "url": "http://localhost:8002",
        "version": "1.0.0",
        "skills": [{
            "id": "onboard_property",
            "name": "Onboard Property",
            "description": "Validates and stores property data"
        }]
    }

@app.post("/tasks/send")
def handle_task(task: dict):
    skill = task.get("skill_id")
    data  = task.get("input", {})
    if skill == "onboard_property":
        return onboard_property(data)
    return {"status": "failed", "output": {"error": "Unknown skill"}}

def onboard_property(data: dict):
    required = ["title", "location", "price", "area", "bedrooms", "property_type"]
    missing  = [f for f in required if f not in data or not str(data[f])]
    if missing:
        logging.warning(f"Missing fields: {missing}")
        return {"status": "failed", "output": {"error": f"Missing fields: {missing}"}}

    session     = Session()
    property_id = str(uuid.uuid4())
    prop        = PropertyDB(
        id       = property_id,
        title    = data["title"],
        location = data["location"],
        price    = float(data["price"]),
        details  = data
    )
    session.add(prop)
    session.commit()
    session.close()

    logging.info(f"✅ Property onboarded: {property_id} - {data['title']}")
    trigger_marketing(property_id, data)

    return {
        "status": "completed",
        "output": {
            "property_id": property_id,
            "message": f"Property '{data['title']}' onboarded and marketing triggered"
        }
    }

def trigger_marketing(property_id: str, data: dict):
    try:
        httpx.post(
            "http://localhost:8003/tasks/send",
            json={
                "task_id":  str(uuid.uuid4()),
                "skill_id": "generate_insights",
                "input":    {"property_id": property_id, **data}
            },
            timeout=10.0
        )
        logging.info(f"📊 Marketing agent triggered for: {property_id}")
    except Exception as e:
        logging.warning(f"⚠️ Could not trigger marketing agent: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "agent": "deal-onboarding"}