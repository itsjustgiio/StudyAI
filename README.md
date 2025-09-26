StudyAI ✏️
----
**StudyAI** is an intelligent desktop application designed to revolutionize the way students learn from lectures.  
Too often, students fall behind due to fast-paced teaching, unclear explanations, or distractions. StudyAI bridges these gaps by transforming raw lectures into **personalized, accessible, and actionable study material**.
-----

## 🚀 Features

### 📌 Core Capabilities
**Capture** → Upload or record lecture audio with real-time transcription (Whisper).  
**Condense** → Summarize lectures in three modes:
  - *Topics Only* → Quick review of key concepts  
  - *Questions Asked* → Extracted Q&A from the lecture  
  - *Detailed Summary* → Narrative-style overview for deep study
    
**Comprehend** → Learn actively through two AI agents:
  - *Study Buddy* → Explains difficult concepts in plain language  
  - *Quiz Master* → Generates personalized practice questions 

-----

## Project Structure

LectureAI/
│── README.md                  # Overview, setup, and usage instructions
│── requirements.txt           # Python dependencies (Flet, Whisper, Gemini SDK, etc.)
│── .gitignore                 # Ignore virtualenv, cache, and local files
│── main.py                    # Entry point for the app (launches UI)

# ── Core Application
│── app/
│   │── __init__.py
│   │── ui.py                  # UI components (Flet layouts, sidebar, editor, etc.)
│   │── notes.py               # Note-taking editor logic
│   │── audio.py               # Handles recording & uploading lecture audio
│   │── transcription.py       # Whisper transcription + live captions
│   │── summarizer.py          # Summarization modes (topics, Q&A, detailed)
│   │── agents.py              # Study Buddy & Quiz Master
│   │── integrations.py        # Google API wrappers (Drive, Docs, etc.)
│   │── storage.py             # Local save/load for notes & transcripts
│   │── utils.py               # Shared helpers (formatting, logging, etc.)
│   │── agents/
│   │── __init__.py
│   │── study_buddy.py     # Explains lecture concepts
│   │── quiz_master.py     # Generates adaptive practice questions
│   │── base_agent.py      # (optional) Shared logic / utilities for both

# ── Assets (optional but nice for hackathon polish)
│── assets/
│   │── logo.png               # App/mascot branding (beaver 🦫 optional)
│   │── icons/                 # Button & UI icons
│   │── styles.css (optional)  # Custom styles if needed

# ── Data (local storage only, no DB for hackathon)
│── data/
│   │── notes/                 # Saved notes by class
│   │── transcripts/           # Lecture transcripts
│   │── summaries/             # Generated summaries
│   │── quizzes/               # Saved quiz questions/answers
│   │── textbooks/             # Uploaded textbooks/chapters for agents


# ── Google Integrations
│── integrations/
│   │── drive_api.py           # Import lecture slides/notes from Google Drive
│   │── docs_api.py            # Export polished notes/summaries to Google Docs
│   │── gemini_api.py          # Summarization, Q&A, quiz generation
│   │── translate_api.py       # (optional) Google Translate for transcripts
│   │── calendar_api.py        # (optional) Study reminders via Google Calendar
│   │── vertex_ai.py           # (optional) Advanced ML pipelines / embeddings

# ── Testing (optional, if you have time)
│── tests/
│   │── test_notes.py
│   │── test_transcription.py
│   │── test_summarizer.py
│   │── test_integrations.py





