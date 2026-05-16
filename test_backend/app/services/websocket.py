# app/services/websocket.py
"""WebSocket manager for real-time communication."""

from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manage WebSocket connections and message broadcasting."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, client_id: str, room: str = "default"):
        """Accept and store WebSocket connection."""
        await websocket.accept()

        if room not in self.active_connections:
            self.active_connections[room] = set()

        self.active_connections[room].add(websocket)
        self.connection_metadata[websocket] = {
            "client_id": client_id,
            "room": room
        }

        logger.info(f"Client {client_id} connected to room {room}")

        # Отправляем приветственное сообщение
        await self.send_personal_message(websocket, {
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "room": room
        })

    async def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.connection_metadata:
            metadata = self.connection_metadata[websocket]
            room = metadata.get("room", "default")
            client_id = metadata.get("client_id", "unknown")

            if room in self.active_connections:
                self.active_connections[room].discard(websocket)
                if not self.active_connections[room]:
                    del self.active_connections[room]

            del self.connection_metadata[websocket]
            logger.info(f"Client {client_id} disconnected from room {room}")

    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to specific connection."""
        try:
            await websocket.send_json(message)
        except WebSocketDisconnect:
            await self.disconnect(websocket)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

    async def broadcast_to_room(self, room: str, message: dict, exclude: WebSocket = None):
        """Broadcast message to all connections in a room."""
        if room in self.active_connections:
            connections = self.active_connections[room].copy()
            for connection in connections:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except WebSocketDisconnect:
                        await self.disconnect(connection)
                    except Exception as e:
                        logger.error(f"Error broadcasting message: {e}")

    async def broadcast_to_all(self, message: dict, exclude: WebSocket = None):
        """Broadcast message to all connections in all rooms."""
        for room in self.active_connections:
            await self.broadcast_to_room(room, message, exclude)

    async def handle_inference_progress(self, task_id: str, progress: float, status: str):
        """Broadcast inference progress updates."""
        await self.broadcast_to_all({
            "type": "inference_progress",
            "task_id": task_id,
            "progress": progress,
            "status": status
        })

    async def send_result(self, client_id: str, result: dict):
        """Send inference result to specific client."""
        # Find websocket by client_id
        for ws, metadata in self.connection_metadata.items():
            if metadata.get("client_id") == client_id:
                await self.send_personal_message(ws, {
                    "type": "result",
                    "data": result
                })
                break


# Global instance
websocket_manager = WebSocketManager()