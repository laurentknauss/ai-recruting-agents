# AI-Powered Resume Screening System

This project uses a custom multi-agent pipeline and **Ollama-hosted LLMs** (running locally) to analyze and rank candidate resumes based on multiple key criteria. It aims to assist recruiters in identifying top talent efficiently and privately — without relying on external LLM APIs.

## Architecture

The pipeline is orchestrated by `OrchestratorAgent` and delegates work to five specialized agents:

1. **Extractor** — extracts resume text and structured information
2. **Analyzer** — analyzes skills, experience, education, achievements, and domain expertise
3. **Matcher** — matches candidates against jobs stored in SQLite
4. **Screener** — performs an initial candidate screening
5. **Recommender** — produces the final recommendation

All agents inherit from `BaseAgent` and use the OpenAI-compatible Ollama endpoint at `localhost:11434`.

## Features

- Automatic PDF resume parsing
- Local language models via **Ollama** (no cloud LLM dependency)
- Intelligent ranking based on:
  - Technical Skills
  - Years of Experience
  - Education Level
  - Experience Level (Junior / Mid / Senior)
  - Key Achievements
  - Domain Expertise
- SQLite-backed job matching

## Tech Stack

- **Python**
- **Ollama** for local LLM hosting (for example, `llama3.2`)
- **Streamlit** for the user interface
- **SQLite** for job data
- **pdfminer.six** for PDF text extraction

## How to run

Install the project dependencies, make sure Ollama is running with the configured model, then seed the sample jobs database:

```bash
python db/seed_jobs.py
python -m streamlit run app.py
```
