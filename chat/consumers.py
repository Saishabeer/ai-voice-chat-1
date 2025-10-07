import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai
from google.genai import types
import os
from . import constants
from dotenv import load_dotenv

load_dotenv()


client = genai.Client(
    api_key=os.getenv("API_KEY"),
    http_options={"api_version": "v1alpha"}
)


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
        config = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "speech_config": {
                "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
            },
            "input_audio_transcription": {},  # Enable input transcription
            "output_audio_transcription": {},  # Enable output transcription
            "system_instruction": constants.RISHI_SYSTEM_INSTRUCTION,
        }
        self.session_context = client.aio.live.connect(model=constants.GEMINI_MODEL_NAME, config=config)
        self.session = await self.session_context.__aenter__()
        # Start a background task to listen for responses from Gemini.
        asyncio.create_task(self.listen_for_gemini_responses())

    async def listen_for_gemini_responses(self):
        """Receives audio chunks from Gemini and streams them to the client."""
        if not self.session:
            return
        try:
            while True:
                # Continuously listen for new turns/responses
                turn = self.session.receive()
                async for response in turn:
                    # Handle transcriptions from server_content
                    if hasattr(response, 'server_content') and response.server_content:
                        server_content = response.server_content
                        
                        # Handle input transcription (user speech)
                        if hasattr(server_content, 'input_transcription') and server_content.input_transcription:
                            if hasattr(server_content.input_transcription, 'text') and server_content.input_transcription.text:
                                await self.send(text_data=json.dumps({
                                    'type': 'user_transcript',
                                    'text': server_content.input_transcription.text
                                }))
                        
                        # Handle output transcription (Rishi's speech)
                        if hasattr(server_content, 'output_transcription') and server_content.output_transcription:
                            if hasattr(server_content.output_transcription, 'text') and server_content.output_transcription.text:
                                await self.send(text_data=json.dumps({
                                    'type': 'ai_transcript',
                                    'text': server_content.output_transcription.text
                                }))
                    
                    # Handle audio data from Gemini
                    if response.data:
                        # Forward the received audio chunk directly to the client.
                        await self.send(bytes_data=response.data)
        except Exception as e:
            # Connection closed or error - silently handle it
            print(f"Gemini session error: {e}")
            pass
