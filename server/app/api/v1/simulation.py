"""
Simulation API — Trigger and control demo simulation scenarios.
"""
import asyncio
import logging

from fastapi import APIRouter, HTTPException
from app.schemas.analytics import SimulationTrigger, SimulationStatus
from app.services.simulator_service import simulator, SCENARIOS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/trigger", response_model=dict, status_code=202)
async def trigger_simulation(trigger: SimulationTrigger):
    """Trigger a simulation scenario in the background."""
    if trigger.scenario not in SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {trigger.scenario}")

    current_status = simulator.get_status(trigger.scenario)
    if current_status.get("status") == "RUNNING":
        raise HTTPException(status_code=409, detail=f"Scenario '{trigger.scenario}' is already running")

    # Launch in background
    asyncio.create_task(
        simulator.run_scenario(trigger.scenario, trigger.speed, trigger.ticket_count)
    )

    return {
        "status": "STARTED",
        "scenario": trigger.scenario,
        "speed": trigger.speed,
        "ticket_count": trigger.ticket_count,
    }


@router.get("/status", response_model=dict)
async def get_simulation_status():
    """Get status of all simulation scenarios."""
    statuses = {}
    for scenario in SCENARIOS:
        statuses[scenario] = simulator.get_status(scenario)
    return {"simulations": statuses, "any_running": simulator.is_running}


@router.post("/stop/{scenario}", response_model=dict)
async def stop_simulation(scenario: str):
    """Stop a running simulation scenario."""
    if scenario not in SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown scenario: {scenario}")

    simulator.stop_scenario(scenario)
    return {"status": "STOPPING", "scenario": scenario}


@router.get("/scenarios", response_model=dict)
async def list_scenarios():
    """List available simulation scenarios."""
    scenarios = []
    for name, config in SCENARIOS.items():
        scenarios.append({
            "id": name,
            "label": name.replace("_", " ").title(),
            "category": config["category"],
            "sample_messages": config["messages"][:3],
        })
    return {"scenarios": scenarios}
