import json
import logging
from typing import List
from datetime import datetime
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for real-time alert notifications via WebSocket.
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    def add_connection(self, websocket: WebSocket):
        """Register a new WebSocket connection."""
        self.active_connections.append(websocket)
        logger.info(f"Connection added. Total active: {len(self.active_connections)}")
    
    def remove_connection(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Connection removed. Total active: {len(self.active_connections)}")
    
    async def broadcast_demo_alert(self, alert_type: str = "sar_alert"):
        """
        Broadcast a demo alert to all connected clients.
        """
        alert_data = {
            "type": alert_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": self._generate_demo_alert_data(alert_type)
        }
        
        message = json.dumps(alert_data)
        
        # Broadcast to all connected clients
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                logger.info(f"Alert sent: {alert_type}")
            except Exception as e:
                logger.error(f"Failed to send alert to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.remove_connection(conn)
    
    def _generate_demo_alert_data(self, alert_type: str) -> dict:
        """Generate demo alert data based on type."""
        if alert_type == "sar_alert":
            return {
                "alert_id": "sar-demo-001",
                "severity": "critical",
                "position": {
                    "lon": -42.0,
                    "lat": -67.0
                },
                "message": "DEMO: SAR operation requested at coordinates",
                "vessel_in_range": True
            }
        elif alert_type == "ice_hazard":
            return {
                "alert_id": "ice-demo-001",
                "severity": "warning",
                "position": {
                    "lon": -44.0,
                    "lat": -69.0
                },
                "message": "DEMO: Dangerous ice concentration detected",
                "ice_concentration": 0.85
            }
        elif alert_type == "route_deviation":
            return {
                "alert_id": "deviation-demo-001",
                "severity": "moderate",
                "message": "DEMO: Vessel deviating from planned route",
                "deviation_distance_nm": 2.5
            }
        else:
            return {
                "alert_id": f"{alert_type}-demo-001",
                "severity": "info",
                "message": f"DEMO: {alert_type} notification"
            }
