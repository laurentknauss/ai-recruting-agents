import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError

st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

logger = setup_logger()

st.markdown(
    """
    <style>
        .stProgress .st-bo { background-color: #00a0dc; }
        .success-text { color: #00c853; }
        .warning-text { color: #ffd700; }
        .error-text { color: #ff5252; }
        .st-emotion-cache-1v0mbdj.e115fcil1 { border: 1px solid #ddd; border-radius: 10px; padding: 20px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return the file path."""
    try:
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = "".join(
            c for c in uploaded_file.name if c.isalnum() or c in ("_", "-")
        ).rstrip()
        file_path = save_dir / f"resume_{timestamp}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"File saved successfully to: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving file '{uploaded_file.name}': {str(e)}", exc_info=True)
        raise Exception(f"Error saving file: {str(e)}") from e


async def process_resume_async(file_path: str) -> dict:
    """Process resume through the AI recruitment pipeline."""
    try:
        logger.info(f"Starting resume processing for: {file_path}")
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": datetime.now().isoformat(),
        }
        result = await orchestrator.process_application(resume_data)
        logger.info(
            f"Finished resume processing for: {file_path}, "
            f"Status: {result.get('status', 'N/A')}"
        )
        return result
    except Exception as e:
        logger.error(
            f"Critical error during async processing of {file_path}: {str(e)}",
            exc_info=True,
        )
        raise ResumeProcessingError(
            f"Error processing resume via orchestrator: {str(e)}"
        ) from e


def display_results(result_data: dict):
    """Display analysis results using Streamlit tabs."""
    st.header("📊 Analysis Results")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Analysis", "Job Matches", "Screening", "Recommendation"]
    )

    with tab1:
        st.subheader("Skills Analysis")
        analysis_results = result_data.get("analysis_results")
        if analysis_results:
            st.write(analysis_results.get("skills_analysis", "N/A"))
            score = analysis_results.get("confidence_score")
            if score is not None:
                st.metric("Confidence Score", f"{score:.0%}")
            else:
                st.info("Confidence score not available.")
        else:
            st.warning("Analysis results not found.")

    with tab2:
        st.subheader("Matched Positions")
        job_matches = result_data.get("job_matches")
        if job_matches:
            matched_jobs = job_matches.get("matched_jobs", [])
            if not matched_jobs:
                st.warning("No suitable positions found based on the analysis.")
            else:
                seen_titles = set()
                for job in matched_jobs:
                    if job.get("title") in seen_titles:
                        continue
                    seen_titles.add(job["title"])
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{job.get('title', 'N/A')}**")
                        with col2:
                            st.write(f"Match: {job.get('match_score', 'N/A')}")
                        with col3:
                            st.write(f"📍 {job.get('location', 'N/A')}")
                    st.divider()
        else:
            st.warning("Job match results not found.")

    with tab3:
        st.subheader("Screening Results")
        screening_results = result_data.get("screening_results")
        if screening_results:
            score = screening_results.get("screening_score")
            if score is not None:
                st.metric("Screening Score", f"{score}%")
            else:
                st.info("Screening score not available.")
            st.write(screening_results.get("screening_report", "N/A"))
        else:
            st.warning("Screening results not found.")

    with tab4:
        st.subheader("Final Recommendation")
        final_recommendation = result_data.get("final_recommendation")
        if final_recommendation:
            st.info(
                final_recommendation.get(
                    "final_recommendation", "No recommendation provided."
                ),
                icon="💡",
            )
        else:
            st.warning("Final recommendation not found.")

    try:
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(str(result_data))
        st.success(f"Full results saved to: {output_file}")
        logger.info(f"Results successfully saved to {output_file}")
    except Exception as e:
        st.error(f"Could not save results file: {str(e)}")
        logger.error(f"Failed to save results to file: {str(e)}", exc_info=True)


def cleanup_file(file_path: str):
    """Safely remove the temporary file."""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Successfully cleaned up temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {str(e)}", exc_info=True)


def clear_state():
    """Clear session state when the file uploader changes."""
    logger.debug("File uploader changed, clearing session state.")
    for key in [
        "processing_started",
        "processing_done",
        "result_data",
        "error_message",
        "current_file_path",
    ]:
        st.session_state.pop(key, None)
    st.session_state.pop("uploaded_file_key", None)


def main():
    st.session_state.setdefault("processing_started", False)
    st.session_state.setdefault("processing_done", False)
    st.session_state.setdefault("result_data", None)
    st.session_state.setdefault("error_message", None)
    st.session_state.setdefault("current_file_path", None)

    with st.sidebar:
        st.title("AI Recruiter Agency")
        selected = option_menu(
            key="main_menu",
            menu_title="Navigation",
            options=["Upload Resume", "About"],
            icons=["cloud-upload", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    if selected == "Upload Resume":
        st.header("📄 Resume Analysis")
        st.write("Upload a resume (PDF) to get AI-powered insights and job matches.")

        uploaded_file = st.file_uploader(
            "Choose a PDF resume file",
            type=["pdf"],
            help="Upload a PDF resume to analyze",
            key="uploaded_file_key",
            on_change=clear_state,
        )

        if uploaded_file is not None and not st.session_state.processing_started:
            st.session_state.processing_started = True
            st.session_state.processing_done = False
            st.session_state.result_data = None
            st.session_state.error_message = None
            st.session_state.current_file_path = None

            try:
                with st.spinner(f"Saving {uploaded_file.name}..."):
                    file_path = save_uploaded_file(uploaded_file)
                    st.session_state.current_file_path = file_path

                with st.spinner(f"Analyzing {uploaded_file.name}... Please wait."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    status_text.text("Initializing analysis...")
                    progress_bar.progress(10)
                    status_text.text("Running AI agents...")
                    progress_bar.progress(25)
                    result = asyncio.run(process_resume_async(file_path))
                    progress_bar.progress(90)
                    status_text.text("Finalizing results...")

                    if result and result.get("status") == "completed":
                        st.session_state.result_data = result
                        st.session_state.error_message = None
                    else:
                        error_msg = (
                            f"Processing failed or did not complete. "
                            f"Status: {result.get('status', 'Unknown')}, "
                            f"Stage: {result.get('current_stage', 'N/A')}, "
                            f"Error: {result.get('error', 'No specific error reported.')}"
                        )
                        st.session_state.error_message = error_msg
                        st.session_state.result_data = None

                    progress_bar.progress(100)
                    status_text.empty()

            except Exception as e:
                st.session_state.error_message = f"An error occurred: {str(e)}"
                st.session_state.result_data = None
                logger.error(f"Error during file processing flow: {str(e)}", exc_info=True)
            finally:
                st.session_state.processing_done = True

        if st.session_state.processing_done:
            if st.session_state.result_data:
                st.success("Resume processed successfully!")
                display_results(st.session_state.result_data)
            elif st.session_state.error_message:
                st.error(st.session_state.error_message)

            cleanup_file(st.session_state.current_file_path)

        elif st.session_state.processing_started:
            st.info("Processing is in progress...")

    elif selected == "About":
        st.header("About AI Recruiter Agency")
        st.write(
            """
        Welcome to AI Recruiter Agency, a recruitment analysis system powered by:

        - **Ollama (llama3.2)**: Local language model for natural language processing
        - **Custom agent pipeline**: Specialized agents coordinated by `OrchestratorAgent`
        - **Streamlit**: Web interface for easy interaction

        Our system uses specialized AI agents to:
        1. 📄 Extract information from resumes
        2. 🔍 Analyze candidate profiles
        3. 🎯 Match with suitable positions
        4. 👥 Screen candidates
        5. 💡 Provide detailed recommendations

        Upload a resume to experience AI-powered recruitment analysis!
        """
        )


if __name__ == "__main__":
    main()
