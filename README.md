# Techjays Voice AI Sales Assistant

A real-time voice chat application powered by Google's Gemini 2.0 Live API, featuring Rishi - an AI sales representative for Techjays.

## 🎯 Features

- **Real-time Voice Conversation** - Tap to start/stop live chat sessions
- **Live Transcription** - See what you and Rishi say in real-time
- **Professional Sales AI** - Rishi knows all about Techjays services, pricing, and case studies
- **WebSocket-based** - Low-latency bidirectional audio streaming
- **PCM Audio** - High-quality 16kHz input, 24kHz output

## 📋 Prerequisites

- Python 3.11 or higher
- Windows OS (current setup)
- Modern web browser (Chrome, Edge, or Firefox)
- Microphone access

## 🚀 Installation

### 1. Clone or Navigate to Project Directory
```powershell
cd C:\Users\saish\Desktop\Shabeer\voiceai
```

### 2. Create Virtual Environment
```powershell
python -m venv env
```

### 3. Activate Virtual Environment
```powershell
.\env\Scripts\Activate.ps1
```

If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Apply Database Migrations
```powershell
python manage.py migrate
```

## ⚙️ Configuration

### API Key Setup
The Gemini API key is already configured in `chat/consumers.py`. If you need to change it:

1. Open `chat/consumers.py`
2. Update the API key on line 8-11:
```python
client = genai.Client(
    api_key="YOUR_API_KEY_HERE",
    http_options={"api_version": "v1alpha"}
)
```

### Customize Rishi's Persona
To modify Rishi's sales persona, edit the `system_instruction` in `chat/consumers.py` (lines 48-105).

## 🎮 Running the Application

### Start the Django Development Server
```powershell
python manage.py runserver
```

You should see:
```
Starting ASGI/Daphne version 4.2.1 development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Access the Application
Open your web browser and navigate to:
```
http://127.0.0.1:8000/
```

## 💬 How to Use

1. **Allow Microphone Access** - Your browser will prompt for microphone permissions
2. **Start Chat** - Click the "🎙️ Start Live Chat" button
   - Button turns red and pulses when active
3. **Speak** - Talk naturally to Rishi
   - Your words appear in blue
   - Rishi's responses appear in green
4. **Listen** - Hear Rishi's voice responses
5. **End Chat** - Click "🔴 End Live Chat" to stop

## 📁 Project Structure

```
voiceai/
├── chat/                          # Main chat application
│   ├── consumers.py              # WebSocket consumer (handles Gemini API)
│   ├── routing.py                # WebSocket URL routing
│   ├── urls.py                   # HTTP URL routing
│   ├── views.py                  # HTTP views
│   └── templates/
│       └── chat/
│           └── index.html        # Frontend UI
├── voiceai/                       # Django project settings
│   ├── settings.py               # Main settings
│   ├── urls.py                   # Root URL config
│   ├── asgi.py                   # ASGI config for WebSockets
│   └── wsgi.py                   # WSGI config
├── env/                           # Virtual environment
├── media/                         # Media files storage
├── db.sqlite3                     # SQLite database
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🛠️ Key Technologies

- **Backend Framework**: Django 5.2.6
- **WebSocket**: Channels 4.3.1 + Daphne 4.2.1
- **AI Model**: Google Gemini 2.0 Flash Experimental
- **Audio Format**: PCM (16-bit, 16kHz input / 24kHz output)
- **Frontend**: Vanilla JavaScript + Web Audio API

## 📦 Dependencies

Key packages (see `requirements.txt` for full list):
- `django==5.2.6` - Web framework
- `channels==4.3.1` - WebSocket support
- `daphne==4.2.1` - ASGI server
- `google-genai` - Gemini 2.0 Live API
- `google-generativeai` - Gemini traditional API

## 🔧 Common Commands

### Restart Server
```powershell
# Stop with Ctrl+BREAK, then:
python manage.py runserver
```

### Update Dependencies
```powershell
pip install -r requirements.txt --upgrade
```

### Create New App
```powershell
python manage.py startapp appname
```

### Create Superuser (for Django admin)
```powershell
python manage.py createsuperuser
```

### Collect Static Files (for production)
```powershell
python manage.py collectstatic
```

## 🐛 Troubleshooting

### WebSocket Connection Fails
- Ensure server is running on `http://127.0.0.1:8000/`
- Check browser console for errors
- Verify API key is valid

### No Audio Output
- Check browser permissions for microphone
- Ensure volume is not muted
- Try using headphones to prevent feedback

### Transcript Not Showing
- Refresh the page
- Check browser console for JavaScript errors
- Ensure WebSocket connection is established

### Module Not Found Errors
```powershell
pip install -r requirements.txt
```

### Database Errors
```powershell
python manage.py migrate
```

## 🎨 Customization

### Change Voice
Edit `chat/consumers.py`, line 54:
```python
"voice_config": {"prebuilt_voice_config": {"voice_name": "Puck"}},
```

Available voices: Puck, Charon, Kore, Fenrir, Aoede

### Modify UI Styling
Edit styles in `chat/templates/chat/index.html` (lines 6-15)

### Add New Services/Pricing
Update the `system_instruction` in `chat/consumers.py` with new information

## 📞 Support

For issues or questions about:
- **Techjays Services**: Contact Rishi through the app!
- **Technical Issues**: Check the troubleshooting section above

## 📝 Notes

- **API Costs**: Gemini 2.0 API usage may incur costs. Monitor your usage in Google Cloud Console
- **Production**: For production deployment, use a proper ASGI server and configure `ALLOWED_HOSTS`
- **Security**: Never commit API keys to version control. Use environment variables in production

## 🚀 Quick Start (TL;DR)

```powershell
# Navigate to project
cd C:\Users\saish\Desktop\Shabeer\voiceai

# Activate environment
.\env\Scripts\Activate.ps1

# Run server
python manage.py runserver

# Open browser to http://127.0.0.1:8000/
```

---

**Built with ❤️ for Techjays**
