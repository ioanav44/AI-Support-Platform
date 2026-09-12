"""
WebSocket API endpoint for real-time dashboard updates.
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.websocket_manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.

    Events pushed to clients:
    - TICKET_INGESTED: New ticket processed
    - EMERGING_ISSUE_DETECTED: New anomaly detected
    - SIMULATION_PROGRESS: Simulation tick update
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, optionally handle client messages
            data = await websocket.receive_text()
            # Could handle client-side pings or commands here
            if data == "ping":
                await manager.send_personal(websocket, {"event": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
