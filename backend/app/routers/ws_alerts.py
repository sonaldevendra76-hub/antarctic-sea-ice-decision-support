from fastapi import APIRouter
from fastapi import WebSocket
import json
import logging

from app.services.alert_service import AlertService

logger = logging.getLogger(__name__)
alerts_router = APIRouter()
alert_service = AlertService()


@alerts_router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """
    WebSocket endpoint for real-time alert notifications.
    Supports manually triggered demo SAR alerts.
    """
    await websocket.accept()
    logger.info("WebSocket connection established for alerts")
    
    try:
        # Register this connection with the alert service
        alert_service.add_connection(websocket)
        
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle manual trigger for demo alerts
            if message.get("action") == "trigger_demo_alert":
                alert_type = message.get("type", "sar_alert")
                await alert_service.broadcast_demo_alert(alert_type)
                
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        alert_service.remove_connection(websocket)
        logger.info("WebSocket connection closed")
