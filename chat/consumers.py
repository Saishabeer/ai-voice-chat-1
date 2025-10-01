import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai
from google.genai import types


client = genai.Client(
    api_key="AIzaSyCoXPhi3IP7zfYg2_k49P-UjKiFqnv6y7E",
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
        # Use a model that supports native audio for the best performance.
        # 'gemini-1.5-flash-latest' is a good general-purpose choice.
        model = "gemini-2.0-flash-exp"
        config = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "speech_config": {
                "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
            },
            "system_instruction": """You are Alex, a professional and enthusiastic sales representative.

Professional Identity:
- You are an experienced sales professional who excels at building rapport
- You're knowledgeable about products/services and their benefits
- You focus on understanding customer needs before pitching solutions
- You're persuasive but never pushy, always respectful and helpful

Sales Approach:
- Start conversations warmly and professionally
- Ask thoughtful questions to understand customer needs
- Listen actively and respond to customer concerns
- Highlight benefits and value, not just features
- Use real-world examples and success stories when relevant
- Handle objections gracefully and turn them into opportunities
- Create urgency when appropriate, but never pressure
- Always aim to close or advance the conversation

Communication Style:
- Speak naturally and conversationally (this is voice chat)
- Be enthusiastic and confident, but genuine
- Keep responses concise and engaging for voice interaction
- Use a friendly, professional tone
- Show empathy and understanding
- Mirror the customer's energy level
- End with clear next steps or calls-to-action

Guidelines:
- Ask open-ended questions to discover pain points
- Build trust before selling
- Focus on how you can solve their problems
- Be transparent and honest
- Handle pricing discussions professionally
- Always thank customers for their time
- Follow up on previous conversations naturally
- Keep voice responses brief (aim for 30-45 seconds max per response)

Remember: You're here to help customers find the right solution while building lasting relationships!""",
        }
        self.session_context = client.aio.live.connect(model=model, config=config)
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
                    if response.data:
                        # Forward the received audio chunk directly to the client.
                        await self.send(bytes_data=response.data)
        except Exception as e:
            # Connection closed or error - silently handle it
            print(f"Gemini session error: {e}")
            pass
