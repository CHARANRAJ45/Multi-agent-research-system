import streamlit as st

from pipeline import run_research_pipeline


st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1100px; padding-top: 3rem; padding-bottom: 4rem; }
    .hero { padding: 1.5rem 0 2rem; }
    .hero h1 { margin-bottom: 0.35rem; }
    .hero p { color: #667085; font-size: 1.05rem; margin: 0; }
    .stage-label { color: #667085; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.08em; }
    .stDownloadButton > button { width: 100%; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Multi-Agent Research System</h1>
        <p>Search. Read. Write. Critique. Turn a research question into a structured report.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("research_form"):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Advances in renewable energy storage for 2026",
    )
    submitted = st.form_submit_button("Generate research report", type="primary", use_container_width=True)

if submitted:
    topic = topic.strip()

    if not topic:
        st.warning("Enter a topic before starting the research pipeline.")
    else:
        try:
            with st.status("Running the research pipeline...", expanded=True) as status:
                st.write("1. Search agent is finding recent and reliable sources.")
                st.write("2. Reader agent is selecting and scraping the most relevant URL.")
                st.write("3. Writer agent is composing the report.")
                st.write("4. Critic agent is reviewing the report.")
                results = run_research_pipeline(topic)
                status.update(label="Research pipeline complete", state="complete", expanded=False)
        except Exception as error:
            st.error(f"The research pipeline failed: {error}")
        else:
            report = results.get("report", "No report was returned.")
            feedback = results.get("feedback", "No critic feedback was returned.")
            search_results = results.get("search_results", "No search results were returned.")
            scraped_content = results.get("scraped_content", "No scraped content was returned.")

            st.divider()
            st.subheader(f"Research report: {topic}")

            report_tab, critique_tab, evidence_tab, raw_tab = st.tabs(
                ["Report", "Critic feedback", "Research evidence", "Pipeline state"]
            )

            with report_tab:
                st.markdown(report)
                st.download_button(
                    "Download report",
                    data=report,
                    file_name="research_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            with critique_tab:
                st.markdown(feedback)

            with evidence_tab:
                st.markdown("<div class='stage-label'>Search agent output</div>", unsafe_allow_html=True)
                st.text_area("Search results", search_results, height=260, label_visibility="collapsed")
                st.markdown("<div class='stage-label'>Reader agent output</div>", unsafe_allow_html=True)
                st.text_area("Scraped content", scraped_content, height=260, label_visibility="collapsed")

            with raw_tab:
                st.json(results)