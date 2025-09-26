------
**StudyAI ✏️**

StudyAI is an intelligent desktop application designed to revolutionize the way students learn from lectures.  
Too often, students fall behind due to fast-paced teaching, unclear explanations, or distractions. StudyAI bridges these gaps by transforming raw lectures into personalized, accessible, and actionable study material.

-----
## Features

### Core Capabilities
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
```plaintext
LectureAI/
│── README.md
│── requirements.txt
│── .gitignore
│── main.py

# ── Core Application
│── app/
│   ├── ui.py
│   ├── notes.py
│   ├── audio.py
│   ├── transcription.py
│   ├── summarizer.py
│   ├── agents.py
│   ├── integrations.py
│   ├── storage.py
│   ├── utils.py
│   └── agents/
│       ├── study_buddy.py
│       ├── quiz_master.py
│       └── base_agent.py

# ── Assets
│── assets/
│   ├── logo.png
│   ├── icons/
│   └── styles.css (optional)

# ── Data
│── data/
│   ├── notes/
│   ├── transcripts/
│   ├── summaries/
│   ├── quizzes/
│   └── textbooks/

# ── Google Integrations
│── integrations/
│   ├── drive_api.py
│   ├── docs_api.py
│   └── gemini_api.py
``````
-----
## Installation

Follow these steps to set up **StudyAI** locally:

```bash
# 1. Clone the repository
git clone https://github.com/itsjustgiio/StudyAI.git
cd StudyAI








