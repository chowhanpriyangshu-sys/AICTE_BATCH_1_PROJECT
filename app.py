import datetime
import os
import tempfile

import streamlit as st
from google import genai
from google.genai import types

# Gemini API key
# (User can replace this string with their key. Not required to be in environment variables.)
API_KEY = "AIzaSyA7z_4jqK5rsLGJsSJ0MWAcBVPfgr9zuZg"


st.set_page_config(page_title="Syllabus-to-Schedule Agent", page_icon="📚")
st.title("📚 Syllabus-to-Schedule Agent")
st.write("Upload a PDF, set your timeline, and generate your study schedule as CSV.")

subjects = st.text_input("Subjects / topics to focus on (optional)")

col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date of Studying", datetime.date.today())
with col2:
    exam_date = st.date_input("Exam Date")

uploaded_file = st.file_uploader(
    "Upload Syllabus (PDF only)",
    type=["pdf"],
    accept_multiple_files=False,
)

if st.button("Generate Schedule", type="primary"):
    if not API_KEY:
        st.error("Missing API_KEY. Set it as an environment variable.")
        st.stop()

    if not uploaded_file:
        st.warning("Please upload a PDF syllabus.")
        st.stop()

    if exam_date <= start_date:
        st.error("Exam date must be after start date.")
        st.stop()

    with st.spinner("Reading the PDF and generating the schedule..."):
        try:
            client = genai.Client(api_key=API_KEY)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            gemini_file = client.files.upload(
                file=tmp_file_path,
                config={"display_name": "student_syllabus"},
            )

            prompt = f"""
You are a strict academic curriculum analyzer and study-plan generator.

OBJECTIVE

Convert a valid academic syllabus into a scientifically balanced study schedule that maximizes syllabus completion; retention; revision efficiency; and mental sustainability.

━━━━━━━━━━━━━━━━━━━━
TASK 1: VALIDATE INPUT
━━━━━━━━━━━━━━━━━━━━

Carefully analyze the attached document.

Determine whether the document is an academic syllabus; course curriculum; educational outline; subject-wise course structure; examination syllabus; university syllabus; board syllabus; or study guide.

If the document is NOT a valid syllabus or curriculum document including but not limited to:

* Story
* Novel
* Article
* Newspaper
* Advertisement
* Manual
* Personal notes
* Random text
* Blank page
* Corrupted file
* Image without readable syllabus content
* Insufficient academic information

Return exactly:

INVALID_INPUT

Output nothing else.

Stop immediately.

━━━━━━━━━━━━━━━━━━━━
TASK 2: EXTRACT SYLLABUS
━━━━━━━━━━━━━━━━━━━━

If the document is valid:

1. Extract all topics strictly related to:
   "{subjects}"

2. Ignore unrelated subjects.

3. Preserve topic hierarchy whenever available.

4. Merge duplicate topics.

5. Identify difficult; high-weightage; mathematical; conceptual; and cumulative topics.

━━━━━━━━━━━━━━━━━━━━
TASK 3: BUILD STUDY PLAN
━━━━━━━━━━━━━━━━━━━━

Create a study schedule using:

Start Date: {start_date}

Exam Date: {exam_date}

Calculate all available study days automatically.

Distribute topics evenly across available days.

Ensure:

* 100% syllabus coverage.
* Balanced workload.
* No topic omission.
* Difficult topics receive additional practice.
* Numerical topics receive extra problem-solving sessions.
* Theory-heavy topics receive revision reinforcement.
* High-weightage topics receive repeated exposure.
* Final revision occurs before the examination.
* No empty study days unless unavoidable.

━━━━━━━━━━━━━━━━━━━━
LEARNING SCIENCE RULES
━━━━━━━━━━━━━━━━━━━━

Apply the following evidence-based principles:

* Spaced repetition
* Active recall
* Interleaving
* Retrieval practice
* Progressive revision
* Cumulative reinforcement

Previously studied topics should reappear during revision sessions when beneficial.

━━━━━━━━━━━━━━━━━━━━
BRAIN RELAXATION AND FATIGUE MANAGEMENT
━━━━━━━━━━━━━━━━━━━━

Prevent burnout while maintaining productivity.

For every study day:

* Include one micro-break reminder in any session.
* Encourage hydration.
* Encourage short stretching.
* Avoid excessive daily workload concentration.
* Rotate difficult and moderate topics.
* Do not schedule more than one highly difficult topic in a single session.
* Maintain sustainable cognitive load.

Revision sessions may include:

* Deep breathing
* Mind reset
* Reflection
* Memory consolidation
* Error review

Keep relaxation instructions concise.

Maximum 5 words for any relaxation reminder.

Examples:

* 5 minute stretch
* Hydrate and relax
* Deep breathing break
* Short walk break
* Eye rest 5 min

━━━━━━━━━━━━━━━━━━━━
DAILY SESSION STRUCTURE
━━━━━━━━━━━━━━━━━━━━

Every day must contain exactly three study sessions.

Morning Session

Purpose:

* New theory learning
* Textbook reading
* Concept building
* Lecture viewing

Noon Session

Purpose:

* Practice problems
* Numerical solving
* Coding exercises
* Worked examples
* Assignments

Night Session

Purpose:

* Active recall
* Flashcards
* Formula revision
* Short notes
* Self-testing
* Topic summaries

━━━━━━━━━━━━━━━━━━━━
SESSION WRITING RULES
━━━━━━━━━━━━━━━━━━━━

For every session:

* Mention exact topic names.
* Use action-oriented language.
* Maximum 20 words.
* Use semicolons instead of commas.
* Keep concise and specific.
* Include relaxation reminder when appropriate.
* No blank sessions.

━━━━━━━━━━━━━━━━━━━━
REVISION REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━

Reserve the final days before examination for:

* Full syllabus revision
* Weak topic review
* Formula revision
* Previous year questions
* Mock tests
* Error analysis
* Rapid recall

━━━━━━━━━━━━━━━━━━━━
CSV OUTPUT RULES
━━━━━━━━━━━━━━━━━━━━

Output ONLY raw CSV.

Header must be exactly:

Date,Subject,Morning Session,Noon Session,Night Session

Rules:

* No markdown.
* No explanations.
* No introductory text.
* No concluding text.
* No code blocks.
* No extra columns.
* No commas inside cell values.
* Use semicolons for task separation.
* Every row must contain exactly 5 columns.
* Dates must be in chronological order.
* Start output immediately with CSV header.
* Output valid CSV only.
* Never output any text before the CSV header.


"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[gemini_file, prompt],
                config=types.GenerateContentConfig(temperature=0.2),
            )

            result_text = response.text.strip()

            # Cleanup
            try:
                client.files.delete(name=gemini_file.name)
            finally:
                try:
                    os.remove(tmp_file_path)
                except Exception:
                    pass

            if result_text == "INVALID_INPUT":
                st.error("Invalid Input: Gemini detected that the uploaded document is not a syllabus.")
            else:
                st.success("Detailed Schedule Generated Successfully!")
                st.code(result_text, language="csv")
                st.download_button(
                    label="Download Schedule (CSV)",
                    data=result_text,
                    file_name="detailed_study_schedule.csv",
                    mime="text/csv",
                )

        except Exception as e:
            st.error(f"An error occurred with the Gemini API: {e}")

