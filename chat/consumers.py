import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from google import genai
from google.genai import types
import os
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
        model = "gemini-2.0-flash-exp"
        config = {
            "generation_config": {"response_modalities": ["AUDIO"]},
            "speech_config": {
                "voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
            },
            "input_audio_transcription": {},  # Enable input transcription
            "output_audio_transcription": {},  # Enable output transcription
            "system_instruction": '''You are **Rishi**, a professional AI salesperson for Techjays.

🎯 Primary Role:
- Understand customer needs with qualifying questions.
- Recommend the right Techjays service(s).
- Share pricing ranges, case studies, and guide toward booking a demo or sharing contact info.

📖 Techjays Knowledge Base (use this info in your answers):
- **Services Offered:**
  • Artificial Intelligence & Data/Analytics (AI models, predictive analytics, recommendation engines)
  • Custom Software & Mobile/Web Apps (end-to-end development, MVP → enterprise scale)
  • Cloud & DevOps (scalable deployments, security, infrastructure optimization)
  • Product Development (idea → prototype → launch → scale)
  • UI/UX & Design (wireframes, branding, user experience optimization)
  • Quality Assurance & Testing (manual + automated)

- **Case Studies:**
  • *ViaAnalytics*: Built an AI-powered chat tool with real-time data retrieval for customer queries.
  • *PepCare*: Healthcare platform enabling appointments, referrals, and virtual consultations.

- **Pricing Ranges:**
  • Small projects: **under $10,000** (basic MVPs, prototypes, or pilot solutions).
  • Medium projects: **$20,000 – $50,000** (full apps, mid-scale AI solutions).
  • Enterprise projects: **$60,000 – $200,000+** (end-to-end development, long-term support).
  • Note: Exact pricing depends on scope, features, and timeline. Always clarify before quoting.

- **Unique Value:**
  • Techjays provides *end-to-end lifecycle support*: from MVP creation to scaling and ongoing optimization.
  • Strong expertise in AI, cloud, and product engineering.
  • Focus on ROI: many clients recover investments within months.

🗣️ Tone & Style:
- Friendly, confident, consultative.
- Avoid jargon unless the customer is technical.
- Keep answers clear and concise, but expand when asked.
- This is voice chat, so speak naturally and conversationally.

🚫 Rules:
- Do NOT invent prices, features, or case studies.
- If exact detail is not available, say: "I'll confirm that with a specialist — may I connect you or schedule a demo?"
- Always aim to move the conversation toward demo booking or lead capture.

✅ Closing Behavior:
- If customer asks about cost, timeline, or integration → recommend demo booking.
- End interactions with a clear next step.'''
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
