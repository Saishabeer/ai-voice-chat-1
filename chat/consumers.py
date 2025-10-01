import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai
from google.genai import types


client = genai.Client(api_key="AIzaSyCoXPhi3IP7zfYg2_k49P-UjKiFqnv6y7E")


class VoiceChatConsumer(AsyncWebsocketConsumer):
    """
    This consumer handles a WebSocket connection to a client and manages a
    real-time, bidirectional audio stream with the Gemini Live API.
    """

    async def connect(self):
        self.session = None
        self.session_context = None
        await self.accept()

    async def disconnect(self, close_code):
        # Clean up the Gemini session when the client disconnects.
        if self.session and self.session_context:
            try:
                await self.session_context.__aexit__(None, None, None)
            except:
                pass
            self.session = None
            self.session_context = None

    async def receive(self, text_data=None, bytes_data=None):
        # This consumer now primarily handles raw audio bytes.
        if bytes_data:
            if not self.session:
                # On the first audio chunk, establish the connection to Gemini Live API.
                await self.start_gemini_session()

            # Forward the audio chunk to Gemini.
            if self.session:
                await self.session.send_realtime_input(
                    audio=types.Blob(data=bytes_data, mime_type="audio/pcm;rate=16000")
                )

    async def start_gemini_session(self):
        """Initializes a new live session with the Gemini API."""
        # Use a model that supports native audio for the best performance.
        # 'gemini-1.5-flash-latest' is a good general-purpose choice.
        model = "gemini-2.0-flash-exp"
        config = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "speech_config": {
                "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
            },
            "system_instruction": "You are a helpful and friendly AI assistant. Keep responses concise and conversational for voice chat.",
        }
        self.session_context = client.aio.live.connect(model=model, config=config)
        self.session = await self.session_context.__aenter__()
        # Start a background task to listen for responses from Gemini.
        asyncio.create_task(self.listen_for_gemini_responses())

    async def listen_for_gemini_responses(self):
        """Receives audio chunks from Gemini and streams them to the client."""
        if not self.session:
            return
        async for response in self.session.receive():
            if response.data:
                # Forward the received audio chunk directly to the client.
                await self.send(bytes_data=response.data)
