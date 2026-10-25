# AI-Powered Lead Scraper (ScrapeGraphAI)

A structured B2B lead generation scraper powered by [ScrapeGraphAI](https://github.com/ScrapeGraphAI/Scrapegraph-ai.git) and Large Language Models.

---

## 🚀 Features

- **Automated Contact & Company Extraction:**
  - Company name, website, industry, description/value proposition
  - Headquarters and office locations
  - General contact emails (`info@`, `sales@`, `contact@`)
  - Direct telephone & hotline numbers
  - Social media profiles (LinkedIn, X / Twitter, GitHub, Facebook)
  - Key personnel (Founders, Executives, Head of Sales, etc.) with titles, emails, and LinkedIn URLs
- **Multi-Model / LLM Support:**
  - Google Gemini (Gemini 2.0 Flash, Gemini 1.5 Pro)
  - OpenAI (GPT-4o, GPT-4o-mini)
  - Groq (Llama-3.3-70b)
  - Ollama (Local free models like `llama3.2`)
- **Automated Export:**
  - Exports extracted leads into structured **JSON** (`outputs/leads_*.json`)
  - Exports flattened leads into clean **CSV** (`outputs/leads_*.csv`) ready for Excel / Google Sheets
  - Displays a summary table in the terminal

---

## 🛠️ Installation & Setup

All prerequisites and dependencies have already been installed in this workspace:
- Dedicated virtual environment: `.venv` (Python 3.12)
- ScrapeGraphAI & LangChain libraries
- Playwright Chromium headless browser binaries
- Cloned ScrapeGraphAI source code repository: `Scrapegraph-ai/`

### 1. Configure Your API Key

Open the [.env](file:///e:/Code/Projects/Antigravity/Lead%20Scrapper/.env) file and add your preferred API key:

```env
# Google Gemini (Free tier available)
GEMINI_API_KEY=AIzaSy...

# Or OpenAI
OPENAI_API_KEY=sk-...

# Or Groq
GROQ_API_KEY=gsk_...
```

---

## 💻 How to Run

### Option 1: Using the PowerShell / Command Line

```powershell
# Scrape a single website
.\.venv\Scripts\python.exe lead_scraper.py https://example.com

# Scrape multiple websites from a text file
.\.venv\Scripts\python.exe lead_scraper.py --file targets_example.txt

# Specify provider and model
.\.venv\Scripts\python.exe lead_scraper.py https://example.com --provider gemini --model gemini-2.0-flash

# Run with visible browser window (headful mode)
.\.venv\Scripts\python.exe lead_scraper.py https://example.com --headful
```

### Option 2: Using the Batch Launcher (`run_lead_scraper.bat`)

```cmd
run_lead_scraper.bat https://example.com
run_lead_scraper.bat --file targets_example.txt
```

---

## 📂 Project Structure

```
Lead Scrapper/
├── .venv/                      # Python 3.12 virtual environment
├── Scrapegraph-ai/             # Cloned official ScrapeGraphAI repository
├── lead_scraper.py             # Main AI lead scraper script
├── targets_example.txt         # Sample list of target websites
├── run_lead_scraper.bat        # Windows one-click launcher
├── .env                        # Active environment variables (API keys)
├── .env.example                # Example environment variables
├── outputs/                    # Generated JSON and CSV lead reports
└── README.md                   # Project documentation
```
