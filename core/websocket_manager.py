from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, chat_id: str, websocket: WebSocket):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []

        self.active_connections[chat_id].append(websocket)

    async def disconnect(self, chat_id: str, websocket: WebSocket):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)

    async def broadcast(self, chat_id: str, message: dict, exclude: WebSocket | None = None):
        if chat_id in self.active_connections:
            to_remove = []
            for connection in self.active_connections[chat_id]:
                if connection == exclude:
                    continue
                try:
                    await connection.send_json(message)
                except Exception:
                    to_remove.append(connection)
            for connection in to_remove:
                await self.disconnect(chat_id, connection)
