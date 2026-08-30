LinXray 🛡️🔍
LinXray is a web-based threat intelligence platform built with Streamlit that scans, analyzes, and detects phishing and deceptive behavior across web URLs. It integrates headless browser automation via Playwright, asynchronous tasks, SQLite data persistence, and multi-provider Generative AI models (OpenAI, Google Gemini, and Reka) to generate comprehensive security analysis reports.

Key Features
URL & Phishing Analysis: Captures runtime page behaviors, screenshots, and structural artifacts using Playwright.

Multi-LLM Intelligence: Leverages OpenAI, Google Gemini, and Reka API models for threat evaluation and report synthesis.

Scan Queue & Tracking: Persists scan history, user authentication, and queue management using SQLite.

Interactive Dashboard: Dynamic Streamlit web interface displaying visual report metrics, raw JSON analysis, and threat scores.

Tech Stack
Frontend / Framework: Streamlit

Browser Automation: Playwright

AI Providers: OpenAI, Google Gemini (google-genai), Reka

Data Validation: Pydantic

Database: SQLite3

Quick Start (Local Setup)
Prerequisites
Python 3.10+

Git

Installation
Clone the repository:

Bash
git clone https://github.com/suyashksingh2008-pixel/LinXray.git
cd LinXray
Create and activate a virtual environment:

Bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash
pip install -r requirements.txt
Install Playwright Chromium binaries:

Bash
playwright install chromium
Configure Environment Variables:
Create a .env file in the project root:

Code snippet
OPENAI_API_KEY=your_openai_api_key
GEMINI_API_KEY=your_gemini_api_key
REKA_API_KEY=your_reka_api_key
DB_PATH=/app/data/linxray.db
Run the Streamlit application:

Bash
streamlit run app.py
Open http://localhost:8501 in your browser.

Deployment with Docker
Because LinXray requires system-level Playwright dependencies and SQLite persistence, deployment via Docker is recommended.

Dockerfile
Ensure a Dockerfile exists in your repository root:

Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browser and OS dependencies
RUN playwright install --with-deps chromium

# Copy app files
COPY . .

# Persistent storage directory for SQLite
RUN mkdir -p /app/data

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
Build and Run
Bash
# Build Docker image
docker build -t linxray:latest .

# Run container with volume mount for SQLite database persistence
docker run -d \
  --name linxray \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  --restart unless-stopped \
  linxray:latest
License
Distributed under the MIT License. See LICENSE for more information.
