# Syllabus-to-Schedule Agent

Upload a syllabus PDF, set your start date and exam date, and generate a detailed study schedule as **CSV** using Gemini.

## Features
- Validates that the uploaded PDF looks like an academic syllabus
- Extracts topics (filtered by your optional subject keywords)
- Generates a day-by-day plan with **exactly three sessions per day**
- Produces **raw CSV output only** (downloadable)

## Prerequisites
- Python 3.9+
- A Gemini API key

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set your Gemini API key as an environment variable:
   - Windows (PowerShell):
     ```powershell
     setx API_KEY "YOUR_GEMINI_API_KEY"
     ```
   - Then restart your terminal.

> Note: `app.py` also contains a default `API_KEY` placeholder. For safety, prefer using the environment variable.

## Run the app
```bash
streamlit run app.py
```

## How to use
1. (Optional) Enter topics/subjects to focus on.
2. Choose:
   - Start Date
   - Exam Date
3. Upload your syllabus PDF.
4. Click **Generate Schedule**.
5. Copy the generated CSV from the page or use **Download Schedule (CSV)**.

## Output format
The model is instructed to output:
- **No markdown**
- **Only raw CSV**
- Header must be exactly:
  `Date,Subject,Morning Session,Noon Session,Night Session`

## Files
- `app.py` — Streamlit UI + Gemini prompt + CSV generation

