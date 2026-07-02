# ⚡ AutoReel AI

> **AutoReel AI** is an AI-powered SaaS web application that transforms a simple text prompt into a fully produced vertical short-form video. It automatically generates a script, creates AI images, synthesizes a natural voiceover, and renders everything into a ready-to-share MP4 reel.

Perfect for creating content for **Instagram Reels, TikTok, YouTube Shorts, and other short-form video platforms.**

---

# ✨ Features

- 🤖 AI-generated scripts from any topic
- 🎨 Automatic AI image generation for every scene
- 🎙️ Natural AI voiceover using ElevenLabs
- 🎬 Automatic video rendering with FFmpeg
- 📱 Vertical 1080 × 1920 MP4 output
- 🔐 Secure user authentication
- 📂 Personal dashboard with project history
- 📥 Download completed reels
- ⚡ Background processing (non-blocking)
- 📊 Live generation status updates

---

# 🎥 Demo

### Workflow

```
User enters a topic
        │
        ▼
AI generates script
        │
        ▼
AI generates scene images
        │
        ▼
AI generates narration
        │
        ▼
FFmpeg renders final reel
        │
        ▼
Download MP4
```

Example prompt:

> "The History of the Roman Empire"

↓

AutoReel AI generates:

- 6-scene script
- 6 AI-generated images
- AI voice narration
- Final vertical video

---

# 🧠 AI Pipeline

```
Topic (text input)
        │
        ▼
Groq (Llama 3.1)
Generates:
• Script
• Narration
• Scene image prompts
        │
        ▼
Pollinations AI
Creates one image per scene
        │
        ▼
ElevenLabs
Converts narration into MP3
        │
        ▼
FFmpeg
Combines images + narration
        │
        ▼
1080×1920 MP4 Reel
```

---

# 🏗️ Architecture

```
Frontend
(Jinja2 + HTML + CSS + JS)
        │
        ▼
Flask Backend
        │
        ▼
Background Worker
        │
 ┌──────────────┬─────────────┬─────────────┐
 ▼              ▼             ▼
Groq      Pollinations    ElevenLabs
 │              │             │
 └──────────────┴─────────────┘
               │
               ▼
            FFmpeg
               │
               ▼
          Generated Reel
```

---

# 💻 Tech Stack

| Layer | Technology |
|--------|------------|
| Backend | Flask |
| Language | Python |
| Database | MySQL |
| Authentication | bcrypt + Flask Sessions |
| Script Generation | Groq API (Llama 3.1) |
| Image Generation | Pollinations.ai |
| Text-to-Speech | ElevenLabs |
| Video Rendering | FFmpeg |
| Frontend | HTML, CSS, JavaScript, Jinja2 |

---

# 🚀 Project Structure

```
autoreel/
│
├── app.py
├── config.py
├── requirements.txt
│
├── database/
│   └── db.py
│
├── models/
│   ├── user.py
│   └── project.py
│
├── routes/
│   ├── auth.py
│   ├── reels.py
│   └── dashboard.py
│
├── services/
│   ├── script_service.py
│   ├── image_service.py
│   ├── audio_service.py
│   └── video_service.py
│
├── workers/
│   └── generate_worker.py
│
├── templates/
├── static/
├── uploads/
└── screenshots/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/yourusername/autoreel-ai.git
cd autoreel-ai
```

---

## 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Install FFmpeg

Download FFmpeg from:

https://ffmpeg.org/download.html

Ensure FFmpeg is added to your system PATH.

---

## 5. Configure MySQL

Create a MySQL database named:

```
autoreel
```

Update your `.env` file with your database credentials.

---

## 6. Configure Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Example:

```env
SECRET_KEY=

DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=autoreel

GROQ_API_KEY=
ELEVENLABS_API_KEY=
```

---

## 7. Run the application

```bash
python app.py
```

Open:

```
http://localhost:5000
```

---

# 🔑 API Services

| Service | Purpose | Free Tier |
|----------|----------|-----------|
| Groq | Script Generation | ✅ |
| Pollinations | AI Images | ✅ Unlimited |
| ElevenLabs | Voice Generation | ✅ Limited |
| FFmpeg | Video Rendering | Open Source |

---


# 🛣️ Future Improvements

- Google Authentication
- Credit-based usage system
- Stripe payment integration
- Cloudinary storage
- Multiple AI voice options
- Background music generation
- Subtitle generation
- AI thumbnail generation
- Video templates
- Multi-language support
- Docker support
- REST API

---

# 🤝 Contributing

Contributions, suggestions, and bug reports are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Aman Kumar**

BBA Graduate • Aspiring Data Analyst / Business Analyst • AI & Data Enthusiast

If you found this project useful, consider giving it a ⭐ on GitHub!