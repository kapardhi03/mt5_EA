"""
Real-time notification service using Server-Sent Events (SSE)
Handles real-time updates for admin dashboards, user status changes, and group updates
"""

import asyncio
import json
from typing import Dict, Set, Any
from datetime import datetime
from fastapi import Request
from fastapi.responses import StreamingResponse
import logging

logger = logging.getLogger(__name__)

class RealtimeService:
    def __init__(self):
        # Store active connections by user type and user ID
        self.admin_connections: Dict[str, Set[Any]] = {}
        self.user_connections: Dict[str, Set[Any]] = {}
        self.master_connections: Dict[str, Set[Any]] = {}

    async def add_connection(self, user_id: str, user_role: str, queue: asyncio.Queue):
        """Add a new SSE connection"""
        if user_role == "admin":
            if user_id not in self.admin_connections:
                self.admin_connections[user_id] = set()
            self.admin_connections[user_id].add(queue)
        elif user_role == "master":
            if user_id not in self.master_connections:
                self.master_connections[user_id] = set()
            self.master_connections[user_id].add(queue)
        else:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(queue)

        logger.info(f"Added connection for {user_role} user {user_id}")

    async def remove_connection(self, user_id: str, user_role: str, queue: asyncio.Queue):
        """Remove an SSE connection"""
        try:
            if user_role == "admin" and user_id in self.admin_connections:
                self.admin_connections[user_id].discard(queue)
                if not self.admin_connections[user_id]:
                    del self.admin_connections[user_id]
            elif user_role == "master" and user_id in self.master_connections:
                self.master_connections[user_id].discard(queue)
                if not self.master_connections[user_id]:
                    del self.master_connections[user_id]
            elif user_id in self.user_connections:
                self.user_connections[user_id].discard(queue)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
        except Exception as e:
            logger.error(f"Error removing connection: {e}")

    async def notify_admins(self, event_type: str, data: Dict[str, Any]):
        """Send notification to all admin connections"""
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        for admin_id, queues in self.admin_connections.items():
            for queue in queues.copy():  # Use copy to avoid modification during iteration
                try:
                    await queue.put(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to admin {admin_id}: {e}")
                    # Remove broken connection
                    queues.discard(queue)

    async def notify_user(self, user_id: str, event_type: str, data: Dict[str, Any]):
        """Send notification to a specific user"""
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        if user_id in self.user_connections:
            for queue in self.user_connections[user_id].copy():
                try:
                    await queue.put(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    self.user_connections[user_id].discard(queue)

    async def notify_masters(self, event_type: str, data: Dict[str, Any]):
        """Send notification to all master connections"""
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        for master_id, queues in self.master_connections.items():
            for queue in queues.copy():
                try:
                    await queue.put(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to master {master_id}: {e}")
                    queues.discard(queue)

    async def notify_group_members(self, group_id: str, event_type: str, data: Dict[str, Any]):
        """Send notification to all members of a specific group"""
        # This would require group membership data - simplified for now
        message = {
            "event": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }

        # In a real implementation, we'd query the database for group members
        # For now, send to all user connections
        for user_id, queues in self.user_connections.items():
            for queue in queues.copy():
                try:
                    await queue.put(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
                    queues.discard(queue)

# Global instance
realtime_service = RealtimeService()

async def sse_endpoint(request: Request, user_id: str, user_role: str):
    """SSE endpoint for real-time updates"""
    async def event_stream():
        queue = asyncio.Queue()
        await realtime_service.add_connection(user_id, user_role, queue)

        try:
            while True:
                try:
                    # Wait for message with timeout to send keep-alive
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"data: {message}\n\n"
                except asyncio.TimeoutError:
                    # Send keep-alive message
                    yield f"data: {json.dumps({'event': 'keep-alive', 'timestamp': datetime.now().isoformat()})}\n\n"
                except asyncio.CancelledError:
                    break
        except Exception as e:
            logger.error(f"SSE connection error: {e}")
        finally:
            await realtime_service.remove_connection(user_id, user_role, queue)

    return StreamingResponse(
        event_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )