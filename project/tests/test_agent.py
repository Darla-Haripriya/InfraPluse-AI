"""
Test suite for InfraPulse AI SRE Agent and Hindsight Memory Bank.
Verifies memory retention, semantic recall, reflection, and agent decision loops.
"""

import sys
import os
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.hindsight_memory import HindsightMemoryBank
from backend.models import IncidentTicket, RetainPayload, RecallQuery
from backend.agent import SREAgent

@pytest.fixture
def memory_bank():
    return HindsightMemoryBank(memory_bank_id="test_memory_bank_01")

@pytest.fixture
def sample_ticket():
    return IncidentTicket(
        ticket_id="TICK-TEST-01",
        customer_id="CUST-001",
        customer_name="RazorPay Financial Networks",
        server_id="prod-mumbai-redis-cache-03",
        severity="P1 - Critical",
        title="High 504 Gateway Timeout on /v2/checkout with Redis connection pool exhaustion",
        alert_source="Prometheus AlertManager",
        error_logs="ConnectionPoolTimeoutException: pool exhausted",
        current_metrics={"cpu": "95%", "connections": 256, "max": 256},
        default_runbook_action="kubectl rollout restart deployment redis-orders-cache"
    )

def test_hindsight_retain_operation(memory_bank):
    """Verifies that retain() properly stores a new incident memory."""
    payload = RetainPayload(
        customer_id="CUST-TEST",
        customer_name="Test Enterprise",
        incident_id="INC-999",
        service="test-service-cache",
        symptom="High memory spike",
        naive_attempt="kill -9 all processes",
        outcome_of_naive_attempt="Catastrophic data loss",
        verified_remediation="Drain cache gracefully",
        rule_learned="Never kill -9 on production cache"
    )
    record = memory_bank.retain(payload)
    assert record.id.startswith("MEM-")
    assert record.service == "test-service-cache"
    assert "kill -9" in record.naive_attempt

def test_hindsight_recall_operation(memory_bank):
    """Verifies that recall() retrieves relevant historical memories."""
    query = RecallQuery(
        query="redis orders cache timeout razorpay",
        customer_id="CUST-001",
        service="redis-orders-cache",
        top_k=2
    )
    memories = memory_bank.recall(query)
    assert len(memories) > 0
    # Must retrieve the RazorPay INC-402 lesson
    found_inc_402 = any("INC-402" in m.incident_id or "redis" in m.service.lower() for m in memories)
    assert found_inc_402

def test_hindsight_reflect_operation(memory_bank):
    """Verifies that reflect() generates meta-level architectural patterns."""
    reflection = memory_bank.reflect(topic="Connection pool saturation", customer_id="CUST-001")
    assert reflection.topic == "Connection pool saturation"
    assert len(reflection.pattern_summary) > 20
    assert "vulnerability" in reflection.systemic_vulnerability.lower() or "backpressure" in reflection.systemic_vulnerability.lower()
    assert reflection.confidence_score >= 0.9

def test_agent_without_memory_vs_with_memory(sample_ticket):
    """
    CRITICAL TEST:
    Demonstrates that without memory, the agent recommends the dangerous action,
    while with Hindsight memory, it halts the engineer and cites the past postmortem.
    """
    agent = SREAgent()
    
    # 1. Test WITHOUT memory
    without_mem = agent.diagnose_incident(sample_ticket, use_memory=False)
    assert without_mem.mode == "WITHOUT_MEMORY"
    assert without_mem.recalled_memories_count == 0
    assert len(without_mem.dangerous_actions_blocked) == 0

    # 2. Test WITH Hindsight memory
    with_mem = agent.diagnose_incident(sample_ticket, use_memory=True)
    assert with_mem.mode == "WITH_HINDSIGHT"
    assert with_mem.recalled_memories_count > 0
    assert len(with_mem.dangerous_actions_blocked) > 0
    assert "PREVENTED CATASTROPHIC ACTION" in with_mem.diagnosis
    assert "canary" in with_mem.verified_safe_runbook.lower() or "throttle" in with_mem.verified_safe_runbook.lower()
