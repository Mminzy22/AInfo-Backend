import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .utils import get_chatbot_response


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        user_message = data["message"]

        llm_response = await self.llm_response(user_message)

        await self.send(
            text_data=json.dumps(
                {"response": llm_response},
                ensure_ascii=False,
            )
        )

    async def llm_response(self, user_message):
        llm_response = get_chatbot_response(user_message)
        response = llm_response.get("response")
        return response
