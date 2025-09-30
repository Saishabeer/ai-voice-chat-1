import speech_recognition as sr

def voice_to_text(audio_file_path):
    r = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = r.record(source)
    return r.recognize_google(audio)


from gtts import gTTS

def text_to_voice(text, filename="reply.mp3"):
    tts = gTTS(text=text, lang="en")
    tts.save(filename)
    return filename
