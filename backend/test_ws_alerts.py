import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/api/ws/alerts"
    try:
        async with websockets.connect(uri) as websocket:
            print("7. WebSocket /api/ws/alerts")
            print("Connection: SUCCESS")
            
            # Send a trigger message to get a demo alert
            trigger_msg = {"action": "trigger_demo_alert", "alert_type": "sar_alert"}
            await websocket.send(json.dumps(trigger_msg))
            
            # Receive response
            response = await websocket.recv()
            data = json.loads(response)
            
            print("Alert received:", data.get("type"))
            print("Alert data:", data.get("data"))
            print("Source: demo/simulated")
            
    except Exception as e:
        print(f"WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
