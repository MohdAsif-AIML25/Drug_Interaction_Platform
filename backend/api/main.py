from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger
import json
import asyncio
import time
import os
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

from .clients.gemini_client import stream_explanation
from .clients.ml_client import get_severity_prediction
from .clients.vector_client import query_interactions, index_data
from .db import save_event

app = FastAPI(title="Drug Interaction Platform API")

# Setup Logging
if not os.path.exists("logs"):
    os.makedirs("logs")
logger.add("logs/api.log", rotation="500 MB", serialize=True, level="INFO")

# Init Metrics
Instrumentator().instrument(app).expose(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DrugAnalyseRequest(BaseModel):
    drug_a: str
    drug_b: str

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API and indexing vector data...")
    try:
        base_dir = Path(__file__).resolve().parents[1]
        candidate_dirs = [
            base_dir / "data",
            base_dir.parent / "data",
            Path.cwd() / "data",
        ]

        data_dir = None
        for candidate in candidate_dirs:
            if (candidate / "eval copy.csv").exists() or (candidate / "test copy.csv").exists():
                data_dir = candidate
                break

        if data_dir is None:
            data_dir = base_dir.parent / "data"

        paths = [
            data_dir / "eval copy.csv",
            data_dir / "test copy.csv",
        ]

        existing_paths = [str(p) for p in paths if p.exists()]
        if existing_paths:
            logger.info(f"Found CSV files for indexing: {existing_paths}")
            index_data(existing_paths)
        else:
            logger.warning(
                "No CSV files found for indexing at startup. Checked: %s",
                [str(p) for p in paths],
            )
    except Exception as e:
        logger.error(f"Startup indexing failed: {e}")

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

@app.post("/search")
@app.post("/interactions")
async def search_interactions(request: DrugAnalyseRequest):
    """Search the indexed interaction documents for a drug pair."""
    drug_a = request.drug_a
    drug_b = request.drug_b
    logger.info(f"Searching interactions for: {drug_a} vs {drug_b}")

    results = query_interactions(drug_a, drug_b)
    return {
        "query": f"{drug_a} vs {drug_b}",
        "results": results,
        "count": len(results),
    }

@app.post("/analyse")
async def analyse(request: DrugAnalyseRequest):
    """
    Advanced Pipeline:
    1. ML Severity Prediction (Instant)
    2. RAG Search (Vector DB from your CSVs)
    3. Streaming Gemini Analysis
    """
    drug_a = request.drug_a
    drug_b = request.drug_b
    
    logger.info(f"Analysing: {drug_a} vs {drug_b}")

    # 1. ML Prediction
    severity, confidence = get_severity_prediction(drug_a, drug_b)

    # 2. RAG Retrieval (Uses your large CSV data)
    context_docs = query_interactions(drug_a, drug_b)
    context_text = "\n".join(context_docs)

    # Fetch product details for drug_a and drug_b
    from .db import SessionLocal
    from .models import Product
    db = SessionLocal()
    drug_a_info = db.query(Product).filter(Product.sub_category.ilike(f"%{drug_a}%")).first()
    drug_b_info = db.query(Product).filter(Product.sub_category.ilike(f"%{drug_b}%")).first()
    db.close()

    drug_a_data = {
        "product_name": drug_a_info.product_name if drug_a_info else "N/A",
        "sub_category": drug_a_info.sub_category if drug_a_info else drug_a,
        "side_effects": drug_a_info.side_effects if drug_a_info else "N/A"
    }

    drug_b_data = {
        "product_name": drug_b_info.product_name if drug_b_info else "N/A",
        "sub_category": drug_b_info.sub_category if drug_b_info else drug_b,
        "side_effects": drug_b_info.side_effects if drug_b_info else "N/A"
    }

    # 3. Save event info (Empty events since we removed FDA)
    try:
        save_event(drug_a, drug_b, [])
    except Exception as e:
        logger.error(f"DB Error: {e}")

    # 4. Result Stream
    async def token_stream():
        # A: Yield ML result first (So UI can show badge immediately)
        yield json.dumps({
            "type": "ml_result", 
            "data": {
                "severity": severity, 
                "confidence": round(confidence * 100, 2)
            }
        }) + "\n\n"
        
        # B: Yield drug product info
        yield json.dumps({
            "type": "drug_info",
            "data": {
                "drug_a": drug_a_data,
                "drug_b": drug_b_data
            }
        }) + "\n\n"

        # C: Yield empty events list (To maintain frontend compatibility)
        yield json.dumps({"type": "events", "data": []}) + "\n\n"
        
        # D: Stream Gemini analysis using CSV context
        prompt_enhancement = f"ML Severity Predicted: {severity}. Context from CSV data: {context_text}. "
        prompt_enhancement += "Requirement: Cover mechanism, consequences, action, and confidence."
        
        try:
            # We pass empty list for events
            async for token in stream_explanation(drug_a, drug_b, [], prompt_enhancement):
                if token:
                    yield json.dumps({"type": "token", "data": token}) + "\n\n"
        except Exception as e:
            logger.error(f"Gemini Error: {e}")
            yield json.dumps({"type": "error", "data": str(e)}) + "\n\n"

    return StreamingResponse(token_stream(), media_type="text/event-stream")