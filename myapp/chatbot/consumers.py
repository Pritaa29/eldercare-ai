# WebSocket consumer (stub — HTTP-based chat is used instead)
from channels.generic.websocket import AsyncWebsocketConsumer
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self): await self.accept()
    async def disconnect(self, code): pass
    async def receive(self, text_data=None, bytes_data=None): pass
