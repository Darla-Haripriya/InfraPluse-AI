"""
Data models for InfraPulse AI SRE Agent.
Defines schemas for incidents, server contexts, Hindsight memory records, and diagnosis outputs.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class ServerContext(BaseModel):
    server_id: str
    customer_id: str
    customer_name: str
    region: str
    infra_stack: str
    lead_sre: str
    constraints: str
    sla_target: str = "99.99%"

class IncidentTicket(BaseModel):
    ticket_id: str
    customer_id: str
    customer_name: str
    server_id: str
    severity: str
    title: str
    alert_source: str
    error_logs: str
    current_metrics: Dict[str, Any]
    default_runbook_action: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MemoryRecord(BaseModel):
    id: str
    timestamp: str
    customer_id: str
    customer_name: str
    incident_id: str
    service: str
    symptom: str
    naive_attempt: str
    outcome_of_naive_attempt: str
    verified_remediation: str
    rule_learned: str
    memory_type: str = "FAILED_COMMAND_LESSON"
    confidence: float = 0.95

class RecallQuery(BaseModel):
    query: str
    customer_id: Optional[str] = None
    service: Optional[str] = None
    top_k: int = 4

class RecallResponse(BaseModel):
    query: str
    memories: List[MemoryRecord]
    retrieved_count: int
    memory_bank_id: str

class RetainPayload(BaseModel):
    customer_id: str
    customer_name: str
    incident_id: str
    service: str
    symptom: str
    naive_attempt: Optional[str] = ""
    outcome_of_naive_attempt: Optional[str] = ""
    verified_remediation: str
    rule_learned: str
    memory_type: str = "INCIDENT_RESOLUTION"
    confidence: float = 0.95

class ReflectionRequest(BaseModel):
    memory_bank_id: Optional[str] = None
    topic: Optional[str] = None
    customer_id: Optional[str] = None

class ReflectionResult(BaseModel):
    topic: str
    reflected_at: str
    pattern_summary: str
    systemic_vulnerability: str
    proactive_policy_rule: str
    supporting_incidents: List[str]
    confidence_score: float

class DiagnosisRequest(BaseModel):
    ticket: IncidentTicket
    use_hindsight_memory: bool = True
    simulate_scenario_step: Optional[int] = None

class DiagnosisResult(BaseModel):
    ticket_id: str
    mode: str # "WITHOUT_MEMORY" or "WITH_HINDSIGHT"
    recalled_memories_count: int
    recalled_memories: List[MemoryRecord]
    dangerous_actions_blocked: List[str]
    diagnosis: str
    verified_safe_runbook: str
    explanation_of_reasoning: str
    learning_delta: str
    confidence: float
