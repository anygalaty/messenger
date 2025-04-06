from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(chat_id, []).append(websocket)

    async def disconnect(self, chat_id: str, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)

    async def broadcast(self, chat_id: str, message: dict, exclude: WebSocket | None = None):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                if connection != exclude:
                    try:
                        await connection.send_json(message)
                    except:
                        await self.disconnect(chat_id, connection)

    async def send_to_user(self, user_id: str, message: dict):
        connections = self.active_connections.get(user_id, [])
        to_remove = []
        for conn in connections:
            try:
                await conn.send_json(message)
            except Exception:
                to_remove.append(conn)
        for conn in to_remove:
            await self.disconnect(user_id, conn)
