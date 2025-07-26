import streamlit as st
import pandas as pd
from tqdm import tqdm
from scraper.description_cleaner import clean_html_text, chunk_text
from scraper.ai_parser import parse_job_with_llm
from utils.url_builder import build_linkedin_url
from scraper.linkedin_browser import scrape_linkedin_jobs_from_url
from streamlit_lottie import st_lottie
import json


if "jobs" not in st.session_state:
    st.session_state.jobs = None
if "summaries" not in st.session_state:
    st.session_state.summaries = []
if "scraping_in_progress" not in st.session_state:
    st.session_state.scraping_in_progress = False



st.set_page_config(page_title="LinkedIn AI Job Scraper", layout="wide")
st.title("🤖 LinkedIn AI Job Scraper (GPT 3.5 Turbo)")

def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)

st.set_page_config(page_title="Custom Lottie", layout="wide")

lottie_animation = load_lottie_file("Business data search women.json")

# Show instruction panel and graphic only before scraping
if not st.session_state.scraping_in_progress and not st.session_state.jobs:
    with st.container():
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("🚀 How to Use This App")
            st.markdown("""
            1. **Enter Job Title and Location** in the sidebar.
            2. Adjust filters like **Date Posted**, **Experience Level**, **Job Type**, etc.
            3. Click **'Scrape Jobs 🚀'** to begin scraping LinkedIn.
            4. Let GPT-3.5 summarize job descriptions for quick review.
            5. Download results as a CSV if needed.
            """)

            st.markdown("👉 This tool helps you skip manual job browsing and get AI-powered summaries instantly!")

        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/942/942748.png", width=200, caption="Start your job hunt smart!")




# Sidebar
with st.sidebar:
    st.header("🔍 Search Filters")
    role = st.selectbox("Job Title", [
        "Data Analyst", "Data Scientist", "Data Associate", "Data Engineer",
        "AI Engineer", "ML Engineer", "Software Engineer", "Software Developer"
    ], index=0)

    location = st.text_input("Location", value="United States")

    date_posted = st.selectbox("Date Posted", [
        "Anytime", "Past Month", "Past Week", "Past 24 Hours"
    ])

    experience_level = st.multiselect("Experience Level", [
        "Internship", "Entry Level", "Associate", "Mid-Senior Level"
    ], default=["Entry Level", "Associate"])

    sort_by = st.radio("Sort By", ["Most Relevant", "Most Recent"], index=1)

    job_type = st.multiselect("Job Type", [
        "Full-time", "Contract", "Volunteer", "Part-time", "Temporary", "Internship"
    ], default=["Full-time"])

    remote_type = st.multiselect("Remote Type", ["On-site", "Hybrid", "Remote"], default=[])

    easy_apply = st.checkbox("Easy Apply Only", value=False)
    under_10_applicants = st.checkbox("Under 10 Applicants Only", value=False)

    max_jobs = st.slider("Max Jobs to Scrape", min_value=1, max_value=25, value=5)
    scrape_button = st.button("Scrape Jobs 🚀")

# Handle Scraping Logic
if scrape_button:
    st.session_state.scraping_in_progress = True
    st.session_state.jobs = None  # 🔁 Reset to allow re-scraping
    st.session_state.summaries = []
    st.rerun()

if st.session_state.scraping_in_progress and not st.session_state.jobs:
    animation_placeholder = st.empty()  # Create placeholder for animation
    with animation_placeholder:
        st_lottie(lottie_animation, height=300, key="custom-job-animation")
    with st.spinner("🔄 Scraping LinkedIn jobs... This may take a few seconds..."):
        url = build_linkedin_url(
        role=role,
        location=location,
        date_posted=date_posted,
        exp_levels=experience_level,
        sort_by=sort_by,
        job_types=job_type,
        remote_types=remote_type,
        easy_apply=easy_apply,
        under_10=under_10_applicants
        )
        st.markdown(f"[🔗 View LinkedIn Search]({url})")

        jobs = scrape_linkedin_jobs_from_url(url=url, max_jobs=max_jobs)    
        animation_placeholder.empty() 

        if not jobs:
            st.error("❌ No jobs found or scraping failed.")
            st.session_state.scraping_in_progress = False
            st.stop()

        st.session_state.jobs = jobs
        st.session_state.cleaned_descriptions = [
            " ".join(chunk_text(clean_html_text(job["Description"]))) for job in jobs
        ]
    st.success(f"✅ Successfully scraped {len(jobs)} jobs.")
    st.markdown("🧠 Running GPT summarization using default expert prompt...")

    # Run GPT summaries
    summaries = []
    progress_bar = st.progress(0)
    for i, desc in enumerate(st.session_state.cleaned_descriptions):
        summary = parse_job_with_llm(desc)  # uses the default expert prompt inside
        summaries.append(summary)
        progress_bar.progress((i + 1) / len(st.session_state.cleaned_descriptions))

    st.session_state.summaries = summaries
    st.session_state.scraping_in_progress = False
    st.success("✅ GPT processing complete.")

# Display results
# Display filter options for scraped fields only
# Display results
if "jobs" in st.session_state and st.session_state.jobs:
    st.markdown("### 📌 Select Columns to Display")

    available_columns = ["Job Title", "Company", "Location", "URL"]
    selected_columns = st.multiselect(
        "Choose the fields you want to display:",
        options=available_columns,
        default=available_columns
    )

    if not selected_columns:
        st.warning("⚠️ Please select at least one field to display.")
    else:
        filtered_data = pd.DataFrame([
            {
                "Job Title": job["Job Title"],
                "Company": job["Company"],
                "Location": job["Location"],
                "URL": job["URL"]
            }
            for job in st.session_state.jobs
        ])[selected_columns]

        st.dataframe(filtered_data, use_container_width=True)

        csv = filtered_data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "📥 Download Results as CSV",
            data=csv,
            file_name=f"{role}_filtered_jobs.csv",
            mime="text/csv"
        )
