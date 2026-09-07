<div align="center">

# LinXray 🛡️🔍

**An AI-Powered Threat Intelligence & Phishing Analysis Platform**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

<br>

> *LinXray is a lightweight threat intelligence tool that scans URLs for phishing and deceptive behaviors using automated browsers and multi-LLM analysis.*

</div>

---

<br>

## ✨ Key Features

<br>

* **Advanced URL & Phishing Analysis:** Captures runtime page behaviors, visual screenshots, and deep structural artifacts using Playwright.

* **Multi-LLM Intelligence:** Leverages state-of-the-art models from **OpenAI**, **Google Gemini** (`google-genai`), and **Reka** for cross-verified threat evaluation and report synthesis.

* **Scan Queue & Tracking:** Persists historical scan data, user interactions, and queue management securely via **SQLite3**.

* **Interactive Dashboard:** Dynamic Streamlit interface featuring visual report metrics, raw JSON telemetry, and clear threat severity scores.

---

<br>

## 🛠️ Tech Stack

<br>

* **Frontend / Framework:** [Streamlit](https://streamlit.io/)

* **Browser Automation:** [Playwright for Python](https://playwright.dev/python/)

* **AI Providers:** OpenAI API, Google Gemini API, Reka API

* **Data Validation:** [Pydantic](https://docs.pydantic.dev/)

* **Database:** SQLite3

---

<br>

## 🚀 Quick Start (Local Setup)

<br>

### Prerequisites

<br>

* Python 3.10 or higher

* Git

<br>

### Installation

<br>

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/suyashksingh2008-pixel/LinXray.git](https://github.com/suyashksingh2008-pixel/LinXray.git)
   cd LinXray
