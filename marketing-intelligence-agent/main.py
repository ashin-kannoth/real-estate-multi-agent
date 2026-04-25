import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi import FastAPI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import chromadb, uuid, logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Marketing Intelligence Agent")

# Vector DB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("property_insights")

processed = set()

# ------------------- Agent Card -------------------
@app.get("/.well-known/agent.json")
def agent_card():
    return {
        "name": "Marketing Intelligence Agent",
        "description": "Generates market insights and stores them in vector DB",
        "url": "http://localhost:8003",
        "version": "1.0.0",
        "skills": [
            {
                "id": "generate_insights",
                "name": "Generate Market Insights",
                "description": "Analyzes property and generates market intelligence"
            },
            {
                "id": "query_insights",
                "name": "Query Insights",
                "description": "Retrieves relevant insights from vector database"
            }
        ]
    }

# ------------------- Task Handler -------------------
@app.post("/tasks/send")
def handle_task(task: dict):
    skill = task.get("skill_id")
    data  = task.get("input", {})

    if skill == "generate_insights":
        return generate_insights(data)

    elif skill == "query_insights":
        return query_insights(data)

    return {"status": "failed", "output": {"error": "Unknown skill"}}

# ------------------- Generate Insights (MOCK) -------------------
def generate_insights(data: dict):
    property_id = data.get("property_id", str(uuid.uuid4()))

    if property_id in processed:
        logging.info(f"Already processed: {property_id}")
        return {"status": "completed", "output": {"message": "Already processed"}}

    # ✅ MOCK AI INSIGHT (no OpenAI required)
    insight_text = f"""
    {data.get('location')} is a high-demand real estate market.
    The property '{data.get('title')}' priced at {data.get('price')} shows strong investment potential.
    The area has consistent price growth and high rental yield.
    It is considered a moderate-risk, high-return investment opportunity.
    """

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(insight_text)

    # Store in ChromaDB with dummy embeddings
    for i, chunk in enumerate(chunks):
        collection.add(
            ids=[f"{property_id}_chunk_{i}"],
            embeddings=[[0.1] * 10],  # dummy vector
            documents=[chunk],
            metadatas=[{
                "property_id": property_id,
                "location": data.get("location", ""),
                "chunk_index": i
            }]
        )

    processed.add(property_id)
    logging.info(f"✅ Insights stored for: {property_id} ({len(chunks)} chunks)")

    return {
        "status": "completed",
        "output": {
            "property_id": property_id,
            "chunks_stored": len(chunks),
            "message": "Market insights generated and stored"
        }
    }

# ------------------- Query Insights (RAG) -------------------
def query_insights(data: dict):
    query = data.get("query", "real estate market insights")

    # Dummy embedding (since we removed OpenAI)
    query_embedding = [0.1] * 10

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    docs = results.get("documents", [[]])[0]
    logging.info(f"🔍 RAG query returned {len(docs)} results")

    return {
        "status": "completed",
        "output": {"results": docs}
    }

# ------------------- Health -------------------
@app.get("/health")
def health():
    return {"status": "ok", "agent": "marketing-intelligence"}