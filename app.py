
import streamlit as st
import datetime
import tempfile
import os
import google.generativeai as genai # Changed from transformers
from PyPDF2 import PdfReader # For PDF text extraction
# import torch # No longer needed for Google Generative AI

st.set_page_config(page_title="Syllabus-to-Schedule Agent", page_icon="📚")

st.title("📚 Syllabus-to-Schedule Agent")
st.write("Upload a PDF, set your timeline, and let the Agent generate your daily study schedule in a beautifully formatted CSV.")

# --- Model Initialization ---
@st.cache_resource
def load_gemini_model(): # Function name changed to reflect Gemini
    # Configure the Google Generative AI library with the API key
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY_1'))
    # Initialize the Gemini model
    model = genai.GenerativeModel('gemini-2.5-flash') # Using gemini-2.5-flash as requested
    return model

model = load_gemini_model() # Call the new function

# --- Main Inputs ---
subjects = st.text_input("What specific subjects/topics from the syllabus are you focusing on?")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date of Studying", datetime.date.today())
with col2:
    exam_date = st.date_input("Exam Date")

uploaded_file = st.file_uploader("Upload Syllabus (PDF only)", type=["pdf"])

# --- Helper Function for PDF Text Extraction ---
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None
    return text

# --- Processing Logic ---
if st.button("Generate Schedule"):
    if not uploaded_file or not subjects:
        st.warning("Please upload a PDF and specify your subjects.")
    else:
        with st.spinner("Processing document and building your detailed schedule..."):
            try:

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name

                # Extract text from the PDF
                pdf_text_content = extract_text_from_pdf(tmp_file_path)
                os.remove(tmp_file_path) # Clean up local temp file

                if pdf_text_content is None:
                    st.error("Failed to extract text from the uploaded PDF. Please try another file.")
                else:
                    # 4. Prompt Engineering
                    full_prompt = f"""
You are a strict academic syllabus parser and study-plan generator.

INPUTS:

* Syllabus Content: {pdf_text_content}
* Target Subjects: {subjects}
* Start Date: {start_date}
* Exam Date: {exam_date}

========================================
STEP 1: DOCUMENT VALIDATION
===========================

Analyze the provided content.

A valid document must clearly be one of the following:

* Academic syllabus
* Course outline
* Curriculum
* Subject-wise teaching plan
* Semester/course structure containing topics, units, chapters, modules, learning outcomes, or examination-related content

If the content is:

* A story
* A novel
* A blank or nearly blank document
* A user manual
* Terms and conditions
* Marketing material
* Random notes
* Any non-academic content

THEN OUTPUT EXACTLY:

INVALID_INPUT

Do not output any explanation, notes, reasoning, markdown, or additional text.

========================================
STEP 2: TOPIC EXTRACTION
========================

If the document is valid:

1. Extract ONLY topics relevant to:
   {subjects}

2. Ignore:

   * Administrative information
   * Faculty details
   * Contact information
   * Assessment policies
   * Attendance rules
   * References/Bibliography
   * General announcements

3. Remove duplicates.

4. Preserve topic hierarchy when available:
   Unit → Chapter → Topic → Subtopic

========================================
STEP 3: STUDY PLAN GENERATION
=============================

Create a day-by-day study schedule from:

Start Date: {start_date}
Exam Date: {exam_date}

Rules:

* Use every available day.
* Distribute topics evenly across the entire timeline.
* Follow syllabus order unless dependency requires a different sequence.
* Ensure workload is balanced.
* Avoid assigning too many new concepts on one day.
* Reserve the final 10–15% of available days for:

  * Revision
  * Practice problems
  * Mock tests
  * Weak-topic review

========================================
STEP 4: DAILY SESSION STRUCTURE
===============================

Every day MUST contain exactly three study sessions:

Morning Session:

* New concepts
* Reading
* Theory learning

Noon Session:

* Practice
* Problem solving
* Numerical exercises
* Examples

Night Session:

* Revision
* Recall
* Summary notes
* Self-testing

Each session must contain specific topics.
Never leave a session empty.

========================================
STEP 5: OUTPUT FORMAT (STRICT)
==============================

Output ONLY raw CSV.

Headers must be EXACTLY:

Date,Subject,Morning Session,Noon Session,Night Session

Requirements:

* No markdown.
* No code fences.
* No explanations.
* No notes.
* No introductory text.
* No concluding text.
* No extra columns.
* No blank lines before or after the CSV.
* Enclose every field in double quotes.
* Escape internal quotes according to CSV rules.
* One row per date.

Example:

"Date","Subject","Morning Session","Noon Session","Night Session"
"2026-01-01","Physics","Unit 1: Kinematics","Practice on displacement and velocity","Revise formulas and key concepts"
"2026-01-02","Physics","Unit 1: Acceleration","Numerical problems on acceleration","Flashcard review and summary"

========================================
QUALITY REQUIREMENTS
====================

* Generate complete coverage of all extracted topics.
* No topic omission.
* No duplicate day entries.
* Dates must be sequential.
* Sessions must be concise, actionable, and specific.
* Output must be directly importable into Excel, Google Sheets, or CSV parsers without modification.
========================================
STEP 4A: BRAIN REFRESH & WELLNESS
=================================

For each study day, include a short brain-refresh activity within the Night Session description.

Requirements:

* Activity duration: 5–15 minutes.
* Keep activities simple and realistic.
* Rotate activities to avoid repetition.
* Activities must not significantly reduce study time.

Examples:

* 5-minute stretching routine
* Short walk
* Deep breathing exercise
* Mindfulness practice
* Light music break
* Journaling key learnings
* Gratitude reflection
* Eye relaxation exercise
* Hydration reminder
* Screen-free relaxation

Format example:

Morning Session:
"Unit 2: Thermodynamics"

Noon Session:
"Practice numerical problems on heat transfer"

Night Session:
"Revise thermodynamics formulas, create summary notes, 10-minute walk for mental refresh"

Do not create separate wellness columns.
Integrate the refresh activity naturally into the Night Session.
Keep the primary focus on academic progress.
"""


                    # 5. Call the Gemini model (Changed from Gemma/transformers)
                    # Use generate_content for Google Generative AI models
                    response = model.generate_content(full_prompt)
                    result_text = response.text

                    # Post-processing: The model might echo the input prompt.
                    # This might not be necessary for Gemini API, but kept as a safeguard.
                    if full_prompt in result_text:
                        result_text = result_text.replace(full_prompt, "").strip()


                    # 6. Display Results based on model's output
                    # Check for "INVALID_INPUT" in the response.
                    if result_text.startswith("INVALID_INPUT"):
                        st.error("Invalid Input: The agent detected that the uploaded document is not a syllabus.")
                    else:
                        st.success("Detailed Schedule Generated Successfully!")
                        st.code(result_text, language="csv")

                        st.download_button(
                            label="Download Schedule (CSV)",
                            data=result_text,
                            file_name="detailed_study_schedule.csv",
                            mime="text/csv"
                        )

            except Exception as e:
                st.error(f"An error occurred: {e}")