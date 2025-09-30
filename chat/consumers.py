import json
import os, uuid
from channels.generic.websocket import AsyncWebsocketConsumer
import google.generativeai as genai
from gtts import gTTS
from django.conf import settings


genai.configure(api_key="AIzaSyCoXPhi3IP7zfYg2_k49P-UjKiFqnv6y7E")


class VoiceChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        user_text = data.get("message")
        if not user_text:
            return

        # 1️⃣ Gemini text reply
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(user_text)
        reply_text = response.text

        # 2️⃣ Ensure media folder exists
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        # 3️⃣ Convert text → speech
        filename = f"reply_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        tts = gTTS(reply_text)
        tts.save(filepath)

        # 4️⃣ Send back text + audio URL
        await self.send(text_data=json.dumps({
            "user_text": user_text,
            "reply_text": reply_text,
            "reply_audio": settings.MEDIA_URL + filename
        }))
