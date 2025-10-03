from django.shortcuts import render
from django.conf import settings
import os, uuid
import google.generativeai as genai
from gtts import gTTS
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()


genai.configure(api_key=os.getenv("API_KEY"))


def chat_page(request):
    """Renders chat page with audio upload and TTS reply."""
    context = {}

    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]
        file_path = f"/tmp/{audio_file.name}"

        # Save uploaded file temporarily
        with open(file_path, "wb+") as f:
            for chunk in audio_file.chunks():
                f.write(chunk)

        # 1️⃣ Speech → Text
        r = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = r.record(source)
        user_text = r.recognize_google(audio)

        # 2️⃣ Gemini text reply
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_text)
        reply_text = response.text

        # 3️⃣ Text → Speech (save to /media/)
        if not os.path.exists(settings.MEDIA_ROOT):
            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        filename = f"reply_{uuid.uuid4().hex}.mp3"
        reply_path = os.path.join(settings.MEDIA_ROOT, filename)
        tts = gTTS(text=reply_text, lang="en")
        tts.save(reply_path)

        context["user_text"] = user_text
        context["reply_text"] = reply_text
        context["reply_audio"] = settings.MEDIA_URL + filename

    return render(request, "chat/index.html", context)
