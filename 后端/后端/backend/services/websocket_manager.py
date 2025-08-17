import logging
import json
from typing import Dict, List, Any
from fastapi import WebSocket
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    WebSocket connection manager for handling real-time data streaming.
    Manages active connections and provides methods for sending data to clients.
    """
    
    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
        logger.info("WebSocket connection manager initialized")
    
    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.
        
        Args:
            websocket (WebSocket): The WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection established. Total active: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Remove a disconnected WebSocket connection.
        
        Args:
            websocket (WebSocket): The WebSocket connection to remove
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for topic, connections in self.subscriptions.items():
            if websocket in connections:
                connections.remove(websocket)
        
        logger.info(f"WebSocket connection closed. Total active: {len(self.active_connections)}")
    
    async def subscribe(self, websocket: WebSocket, topic: str):
        """
        Subscribe a client to a specific topic.
        
        Args:
            websocket (WebSocket): The WebSocket connection to subscribe
            topic (str): The topic to subscribe to
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
            logger.info(f"Client subscribed to topic: {topic}")
    
    async def unsubscribe(self, websocket: WebSocket, topic: str):
        """
        Unsubscribe a client from a specific topic.
        
        Args:
            websocket (WebSocket): The WebSocket connection to unsubscribe
            topic (str): The topic to unsubscribe from
        """
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
            logger.info(f"Client unsubscribed from topic: {topic}")
    
    async def send_personal_message(self, message: Any, websocket: WebSocket):
        """
        Send a message to a specific client.
        
        Args:
            message (Any): The message to send
            websocket (WebSocket): The WebSocket connection to send to
        """
        try:
            if isinstance(message, dict):
                await websocket.send_json(message)
            else:
                await websocket.send_text(str(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
    
    async def broadcast(self, message: Any):
        """
        Broadcast a message to all connected clients.
        
        Args:
            message (Any): The message to broadcast
        """
        disconnected = []
        
        for connection in self.active_connections:
            try:
                if isinstance(message, dict):
                    await connection.send_json(message)
                else:
                    await connection.send_text(str(message))
            except Exception as e:
                logger.error(f"Error during broadcast: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def publish(self, topic: str, message: Any):
        """
        Publish a message to all clients subscribed to a specific topic.
        
        Args:
            topic (str): The topic to publish to
            message (Any): The message to publish
        """
        if topic not in self.subscriptions:
            return
        
        disconnected = []
        
        for connection in self.subscriptions[topic]:
            try:
                if isinstance(message, dict):
                    await connection.send_json(message)
                else:
                    await connection.send_text(str(message))
            except Exception as e:
                logger.error(f"Error publishing to topic {topic}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)
    
    async def send_heartbeat(self):
        """Send a heartbeat message to all connected clients to keep connections alive."""
        heartbeat = {"type": "heartbeat", "timestamp": str(datetime.now())}
        await self.broadcast(heartbeat) 
