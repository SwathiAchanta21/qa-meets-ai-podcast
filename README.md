# 🎙️ QA Meets AI — Automated ASTQB AI Testing Podcast Pipeline

An end-to-end Python automation pipeline that transforms the **ASTQB Certified Tester AI Testing (CT-AI)** syllabus into ~15–18 minute, two-host conversational commute podcasts, complete with multi-voice neural audio synthesis and automated 1080p YouTube video rendering.

---

## 🏗️ Architecture & Pipeline Flow

```text
[ASTQB Syllabus PDF]
        │
        ▼
1. PDF Ingestion & Parsing (PyMuPDF / LangChain)
        │  Extracts structured chapter text & learning objectives
        ▼
2. 2-Stage Map-Reduce Script Planner (GPT-4o)
        │  Generates ~2,200–2,700 word, 60+ turn dialogue (Swathi & Sage)
        ▼
3. Multi-Voice Neural TTS Synthesis (ElevenLabs Multilingual v2 + pydub)
        │  Synthesizes per-turn audio & stitches clean 192k MP3 episodes
        ▼
4. Automated Video Rendering (FFmpeg)
        │  Combines 1920x1080 cover art + MP3 at 1 FPS → YouTube-ready MP4
        ▼
[YouTube & YouTube Music Podcast]
✨ Key Features
Two-Host Persona Scripting: Uses LangChain and GPT-4o to convert dense technical syllabus material into natural, engaging conversations between Swathi (QA practitioner) and Sage (AI systems specialist).
Map-Reduce Length Expansion: Breaks chapters into sub-topics so episodes consistently hit 15–18 minutes (~2,200–2,700 words) without LLM truncation.  
 Clean Audio Stitching: Uses ElevenLabs (eleven_multilingual_v2) per turn and pydub (AudioSegment) to strip MP3 header artifacts and insert natural speaker pauses.  
  Fast 1-FPS Video Rendering: Uses FFmpeg (libx264 -tune stillimage) to render 18-minute 1080p MP4 videos in ~15 seconds for YouTube upload.
  
  📂 Project Structure
-qa-meets-ai-podcast/
├── data/
│   ├── assets/              # Static 1920x1080 podcast cover art
│   ├── input_pdfs/          # Source ASTQB syllabus PDF
│   ├── intermediate/        # Structured JSON dialogue scripts per chapter
│   ├── output_audio/        # Generated 192k MP3 episodes (gitignored)
│   └── output_video/        # Rendered 1080p MP4 videos (gitignored)
├── src/
│   ├── ingestion/           # PDF extraction and chapter chunking
│   ├── nlp/                 # LangChain + GPT-4o script planner
│   └── audio/               # ElevenLabs TTS + pydub audio synthesizer
├── main.py                  # Pipeline orchestrator
├── requirements.txt         # Python dependencies
└── .gitignore               # Excludes .env, venv/, and generated media
🚀 Setup & Usage1. P
rerequisitesPython 3.11+
FFmpeg installed and available in your system PATH
API keys for OpenAI and ElevenLabs
2. Installation
Bash
git clone [https://github.com/SwathiAchanta21/qa-meets-ai-podcast.git](https://github.com/SwathiAchanta21/qa-meets-ai-podcast.git)
cd qa-meets-ai-podcast

python -m venv venv
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt

3. Environment Variables
Create a .env file in the project root:
Code snippet
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
SWATHI_VOICE_ID=your_elevenlabs_voice_id_1
SAGE_VOICE_ID=your_elevenlabs_voice_id_2


4. Run the Pipeline
Generate Episode Script: Run main.py (or src/nlp/planner.py) to output data/intermediate/chapter_1_script.json.Synthesize Audio:

python src/audio/synthesizer.py

Render YouTube MP4:

ffmpeg -y -loop 1 -r 1 -i data/assets/cover.png -i data/output_audio/episode_1_chapter_1.mp3 -vf scale=1920:1080 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest data/output_video/episode_1_chapter_1.mp4

🛠️ Tech StackLLM & Orchestration: Python, LangChain, OpenAI GPT-4oAudio Synthesis: ElevenLabs API (eleven_multilingual_v2), pydub   Video Encoding: FFmpeg (H.264 / AAC 192k)
---

