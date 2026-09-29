"""
FastAPI Server for InfraPulse AI SRE Agent.
Provides RESTful APIs for incident triage, side-by-side memory comparisons,
and direct Hindsight Cloud memory operations (retain, recall, reflect).
"""

import json
import os
import logging
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models import (
    IncidentTicket, DiagnosisRequest, DiagnosisResult,
    RetainPayload, RecallQuery, ReflectionRequest, ReflectionResult, MemoryRecord
)
from .hindsight_memory import hindsight_bank
from .agent import sre_agent

logger = logging.getLogger("infrapulse.api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="InfraPulse AI - Hindsight SRE Agent API",
    description="Enterprise IT Infrastructure Support Agent learning from incident history, failed fixes, and postmortems.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DEMO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "demo")

def _load_json_file(filepath: str) -> List[Dict[str, Any]]:
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

@app.get("/")
def root():
    return {
        "agent": "InfraPulse AI SRE Agent",
        "memory_layer": "Hindsight Cloud by Vectorize",
        "memory_bank_id": settings.hindsight_memory_bank_id,
        "status": "ONLINE"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "memory_bank": settings.hindsight_memory_bank_id}

@app.get("/api/customers")
def get_customers():
    """Returns realistic enterprise infrastructure customers."""
    path = os.path.join(DATA_DIR, "customers.json")
    return _load_json_file(path)

@app.get("/api/tickets")
def get_tickets():
    """Returns active and recent incident tickets."""
    path = os.path.join(DATA_DIR, "tickets.json")
    return _load_json_file(path)

@app.post("/api/tickets/resolve")
def resolve_ticket(req: Dict[str, Any]):
    """
    Marks an incident ticket as RESOLVED and calls Hindsight retain()
    to store the verified resolution as permanent institutional memory.
    """
    try:
        ticket_id = req.get("ticket_id")
        verified_runbook = req.get("verified_runbook", "Safe canary drain protocol executed successfully.")
        
        # Load and update tickets.json
        tickets_path = os.path.join(DATA_DIR, "tickets.json")
        tickets = _load_json_file(tickets_path)
        
        target_ticket = None
        for t in tickets:
            if t.get("ticket_id") == ticket_id:
                t["status"] = "RESOLVED"
                t["resolved_at"] = datetime.utcnow().isoformat() + "Z"
                target_ticket = t
                break
                
        if tickets:
            with open(tickets_path, "w", encoding="utf-8") as f:
                json.dump(tickets, f, indent=2)
                
        # Trigger Hindsight retain()
        payload = RetainPayload(
            customer_id=target_ticket.get("customer_id", "CUST-001") if target_ticket else "CUST-001",
            customer_name=target_ticket.get("customer_name", "Enterprise Account") if target_ticket else "Enterprise Account",
            incident_id=f"INC-{ticket_id.replace('TICK-', '')}",
            service=target_ticket.get("server_id", "infra-service") if target_ticket else "infra-service",
            symptom=target_ticket.get("title", "Incident resolved") if target_ticket else "Incident resolved",
            naive_attempt=target_ticket.get("default_runbook_action", "Default restart") if target_ticket else "Default restart",
            outcome_of_naive_attempt="PREVENTED: Hindsight blocked destructive reboot command; canary protocol executed.",
            verified_remediation=verified_runbook,
            rule_learned="Enforced safe canary drain and worker throttling; 100% database uptime preserved.",
            memory_type="VERIFIED_RESOLUTION_SUCCESS",
            confidence=0.99
        )
        retained_memory = hindsight_bank.retain(payload)
        
        return {
            "success": True,
            "ticket": target_ticket,
            "memory": retained_memory,
            "message": f"Ticket {ticket_id} marked as RESOLVED and retained into Hindsight Memory Bank."
        }
    except Exception as e:
        logger.error(f"Failed to resolve ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scenarios")
def get_scenarios():
    """Returns the 1 -> 3 -> 5 -> 10 continuous learning progression scenarios."""
    path = os.path.join(DEMO_DIR, "demo_scenarios.json")
    return _load_json_file(path)

@app.post("/api/diagnose", response_model=DiagnosisResult)
def diagnose_incident(req: DiagnosisRequest):
    """
    Performs incident diagnosis.
    Toggles between WITHOUT_MEMORY (generic) and WITH_HINDSIGHT (experienced).
    """
    try:
        result = sre_agent.diagnose_incident(
            ticket=req.ticket,
            use_memory=req.use_hindsight_memory
        )
        return result
    except Exception as e:
        logger.error(f"Diagnosis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hindsight/retain", response_model=MemoryRecord)
def retain_memory(payload: RetainPayload):
    """Explicitly stores an incident resolution or failed attempt in Hindsight."""
    try:
        return hindsight_bank.retain(payload)
    except Exception as e:
        logger.error(f"Retain failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hindsight/recall")
def recall_memories(query: RecallQuery):
    """Retrieves relevant historical memories matching query and context."""
    try:
        memories = hindsight_bank.recall(query)
        return {
            "query": query.query,
            "memory_bank_id": hindsight_bank.memory_bank_id,
            "retrieved_count": len(memories),
            "memories": memories
        }
    except Exception as e:
        logger.error(f"Recall failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/hindsight/reflect", response_model=ReflectionResult)
def reflect_patterns(req: ReflectionRequest):
    """
    Triggers the Hindsight Reflection Engine to discover systemic failure patterns
    across multiple incidents.
    """
    try:
        return hindsight_bank.reflect(topic=req.topic, customer_id=req.customer_id)
    except Exception as e:
        logger.error(f"Reflection failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/hindsight/memories")
def get_all_memories():
    """Lists all stored records in the Hindsight Memory Bank."""
    return hindsight_bank.get_all_memories()

@app.get("/api/hindsight/stats")
def get_memory_stats():
    """Provides overview of the active Hindsight Memory Bank."""
    return hindsight_bank.get_memory_bank_stats()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.backend_host, port=settings.backend_port)
