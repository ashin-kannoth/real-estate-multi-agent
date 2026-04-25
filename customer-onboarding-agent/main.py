import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from shared_utils.database import Session, CustomerDB
import uuid, logging

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Customer Onboarding Agent")

@app.get("/.well-known/agent.json")
def agent_card():
    return {
        "name": "Customer Onboarding Agent",
        "description": "Handles customer data collection and validation",
        "url": "http://localhost:8001",
        "version": "1.0.0",
        "skills": [{
            "id": "onboard_customer",
            "name": "Onboard Customer",
            "description": "Validates and stores customer data, returns customer ID"
        }]
    }

@app.post("/tasks/send")
def handle_task(task: dict):
    skill = task.get("skill_id")
    data  = task.get("input", {})
    if skill == "onboard_customer":
        return onboard_customer(data)
    return {"status": "failed", "output": {"error": "Unknown skill"}}

def onboard_customer(data: dict):
    required = ["name", "email", "phone", "budget", "preferred_location"]
    missing  = [f for f in required if f not in data or not data[f]]
    if missing:
        logging.warning(f"Missing fields: {missing}")
        return {"status": "failed", "output": {"error": f"Missing fields: {missing}"}}

    if float(data["budget"]) <= 0:
        return {"status": "failed", "output": {"error": "Budget must be greater than 0"}}

    session     = Session()
    customer_id = str(uuid.uuid4())
    customer    = CustomerDB(
        id       = customer_id,
        name     = data["name"],
        email    = data["email"],
        phone    = data["phone"],
        budget   = float(data["budget"]),
        location = data["preferred_location"]
    )
    session.add(customer)
    session.commit()
    session.close()

    logging.info(f"✅ Customer onboarded: {customer_id} - {data['name']}")
    return {
        "status": "completed",
        "output": {
            "customer_id": customer_id,
            "message": f"Customer {data['name']} onboarded successfully"
        }
    }

@app.get("/health")
def health():
    return {"status": "ok", "agent": "customer-onboarding"}