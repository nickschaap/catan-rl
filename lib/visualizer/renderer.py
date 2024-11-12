from typing import TYPE_CHECKING
from fastapi import FastAPI, WebSocket
import uvicorn
from pydantic import BaseModel
import threading

if TYPE_CHECKING:
    from lib.gameplay.game import Game, GameEvent


class Message(BaseModel):
    type: str
    content: str


class Renderer:
    def __init__(self, game: "Game") -> None:
        self.game = game
        self.game.listen(self.onGameEvent)
        self.app = FastAPI()

        self.app.add_api_websocket_route("/ws", self.websocket_endpoint)
        # Start Uvicorn in a separate thread
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

        print("Listening on 8000")

    def run_server(self):
        uvicorn.run(self.app, host="127.0.0.1", port=8000)

    async def websocket_endpoint(self, websocket: WebSocket):
        await websocket.accept()
        while True:
            data = await websocket.receive_json()
            message = Message(**data)
            print(f"Received {message.type}: {message.content}")
            await websocket.send_json(
                {"type": "response", "content": f"Echo: {message.content}"}
            )

    def onGameEvent(self, event: "GameEvent") -> None:
        self.render()

    def render(self) -> None:
        pass
