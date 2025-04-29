import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from streamlit_option_menu import option_menu
from agents.orchestrator import OrchestratorAgent  # Assuming these imports are correct
from utils.logger import setup_logger
from utils.exceptions import ResumeProcessingError # Assuming these imports are correct

# --- Configuration and Setup ---
st.set_page_config(
    page_title="AI Recruiter Agency",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize logger
logger = setup_logger()

# Custom CSS (remains the same)
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

# --- Helper Functions ---

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file and return the file path. Raises Exception on error."""
    try:
        save_dir = Path("uploads")
        save_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Sanitize filename slightly (optional but good practice)
        safe_filename = "".join(c for c in uploaded_file.name if c.isalnum() or c in ('_', '-')).rstrip()
        file_path = save_dir / f"resume_{timestamp}_{safe_filename}"

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        logger.info(f"File saved successfully to: {file_path}")
        return str(file_path)
    except Exception as e:
        logger.error(f"Error saving file '{uploaded_file.name}': {str(e)}", exc_info=True)
        # Re-raise the exception to be caught by the caller
        raise Exception(f"Error saving file: {str(e)}")


async def process_resume_async(file_path: str) -> dict:
    """Async helper to process resume through the AI recruitment pipeline."""
    try:
        logger.info(f"Starting resume processing for: {file_path}")
        orchestrator = OrchestratorAgent()
        resume_data = {
            "file_path": file_path,
            "submission_timestamp": datetime.now().isoformat(),
        }
        result = await orchestrator.process_application(resume_data)
        logger.info(f"Finished resume processing for: {file_path}, Status: {result.get('status', 'N/A')}")
        return result
    except Exception as e:
        logger.error(f"Critical error during async processing of {file_path}: {str(e)}", exc_info=True)
        # Raise a more specific error if desired, or just re-raise
        raise ResumeProcessingError(f"Error processing resume via orchestrator: {str(e)}")


def display_results(result_data: dict):
    """Displays the analysis results using Streamlit tabs and components."""
    st.header("📊 Analysis Results")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Analysis", "Job Matches", "Screening", "Recommendation"]
    )

    with tab1:
        st.subheader("Skills Analysis")
        if "analysis_results" in result_data and result_data["analysis_results"]:
            st.write(result_data["analysis_results"].get("skills_analysis", "N/A"))
            score = result_data["analysis_results"].get("confidence_score", None)
            if score is not None:
                st.metric("Confidence Score", f"{score:.0%}")
            else:
                st.info("Confidence score not available.")
        else:
            st.warning("Analysis results not found.")

    with tab2:
        st.subheader("Matched Positions")
        if "job_matches" in result_data and result_data["job_matches"]:
            matched_jobs = result_data["job_matches"].get("matched_jobs", [])
            if not matched_jobs:
                st.warning("No suitable positions found based on the analysis.")
            else:
                seen_titles = set()
                for job in matched_jobs:
                    if job.get("title") in seen_titles:
                        continue
                    seen_titles.add(job["title"])

                    with st.container(): # Use st.container for better grouping
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
        if "screening_results" in result_data and result_data["screening_results"]:
            score = result_data["screening_results"].get("screening_score", None)
            if score is not None:
                 st.metric("Screening Score", f"{score}%")
            else:
                st.info("Screening score not available.")
            st.write(result_data["screening_results"].get("screening_report", "N/A"))
        else:
            st.warning("Screening results not found.")

    with tab4:
        st.subheader("Final Recommendation")
        if "final_recommendation" in result_data and result_data["final_recommendation"]:
            st.info(
                result_data["final_recommendation"].get("final_recommendation", "No recommendation provided."),
                icon="💡",
            )
        else:
            st.warning("Final recommendation not found.")

    # Option to save results (consider if this should be automatic or button-triggered)
    try:
        output_dir = Path("results")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(output_file, "w") as f:
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
            # Optionally inform the user, but often not necessary
            # st.warning(f"Could not clean up temporary file: {file_path}")


def clear_state():
    """Callback function to clear session state when file uploader changes."""
    logger.debug("File uploader changed, clearing session state.")
    keys_to_clear = ["processing_started", "processing_done", "result_data", "error_message", "current_file_path"]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    # Clear the file uploader widget state itself indirectly by removing its tracking variable
    if 'uploaded_file_key' in st.session_state:
         del st.session_state['uploaded_file_key']


# --- Main Application Logic ---

def main():
    # Initialize session state variables if they don't exist
    if "processing_started" not in st.session_state:
        st.session_state.processing_started = False
    if "processing_done" not in st.session_state:
        st.session_state.processing_done = False
    if "result_data" not in st.session_state:
        st.session_state.result_data = None
    if "error_message" not in st.session_state:
        st.session_state.error_message = None
    if "current_file_path" not in st.session_state:
        st.session_state.current_file_path = None

    # Sidebar navigation
    with st.sidebar:
        # Placeholder for logo - replace with your actual image path/URL if needed
        # st.image("path/to/your/logo.png", width=50)
        st.title("AI Recruiter Agency")
        selected = option_menu(
            key="main_menu", # Added key
            menu_title="Navigation",
            options=["Upload Resume", "About"],
            icons=["cloud-upload", "info-circle"],
            menu_icon="cast",
            default_index=0,
        )

    # Page Content
    if selected == "Upload Resume":
        st.header("📄 Resume Analysis")
        st.write("Upload a resume (PDF) to get AI-powered insights and job matches.")

        # Use a key and on_change callback for the file uploader
        uploaded_file = st.file_uploader(
            "Choose a PDF resume file",
            type=["pdf"],
            help="Upload a PDF resume to analyze",
            key="uploaded_file_key", # Added key
            on_change=clear_state # Reset state when file changes
        )

        # --- Processing Logic ---
        if uploaded_file is not None:
            # Check if we haven't started processing this specific uploaded file yet
            if not st.session_state.processing_started:
                st.session_state.processing_started = True
                st.session_state.processing_done = False
                st.session_state.result_data = None
                st.session_state.error_message = None
                st.session_state.current_file_path = None # Reset file path

                file_path = None # Define file_path here to ensure it's available in finally
                try:
                    with st.spinner(f"Saving {uploaded_file.name}..."):
                        file_path = save_uploaded_file(uploaded_file)
                        st.session_state.current_file_path = file_path # Store path in state

                    with st.spinner(f"Analyzing {uploaded_file.name}... Please wait."):
                        # Progress bar simulation (optional, real progress is harder with async external calls)
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        status_text.text("Initializing analysis...")
                        progress_bar.progress(10)

                        # Run the asynchronous processing
                        status_text.text("Running AI agents...")
                        progress_bar.progress(25)
                        result = asyncio.run(process_resume_async(file_path)) # Use helper
                        progress_bar.progress(90) # Simulate near completion
                        status_text.text("Finalizing results...")

                        # Store results or error in session state
                        if result and result.get("status") == "completed":
                            st.session_state.result_data = result
                            st.session_state.error_message = None # Clear any previous error
                            logger.info("Processing completed successfully.")
                        else:
                            error_msg = f"Processing failed or did not complete. Status: {result.get('status', 'Unknown')}, Stage: {result.get('current_stage', 'N/A')}, Error: {result.get('error', 'No specific error reported.')}"
                            st.session_state.error_message = error_msg
                            st.session_state.result_data = None
                            logger.warning(error_msg)

                        progress_bar.progress(100) # Complete progress bar
                        status_text.empty() # Clear status text

                except Exception as e:
                    # Catch errors from saving or async processing
                    st.session_state.error_message = f"An error occurred: {str(e)}"
                    st.session_state.result_data = None
                    logger.error(f"Error during file processing flow: {str(e)}", exc_info=True)
                    # Ensure progress indicators are cleared on error
                    if 'progress_bar' in locals(): progress_bar.empty()
                    if 'status_text' in locals(): status_text.empty()

                finally:
                    st.session_state.processing_done = True # Mark processing as attempted
                    # Cleanup handled after display based on state

        # --- Display Logic (runs on every rerun if file was uploaded) ---
        if st.session_state.processing_done:
            if st.session_state.result_data:
                st.success("Resume processed successfully!")
                display_results(st.session_state.result_data)
            elif st.session_state.error_message:
                st.error(st.session_state.error_message)

            # Cleanup the file associated with this completed/failed attempt
            cleanup_file(st.session_state.current_file_path)
            # We might want to clear current_file_path after cleanup
            # st.session_state.current_file_path = None # Uncomment if needed

        elif st.session_state.processing_started:
             # If processing started but isn't done yet (e.g., page refreshed during processing)
             # You might want to show a persistent spinner or message
             st.info("Processing is in progress...")


    elif selected == "About":
        st.header("About AI Recruiter Agency")
        # Content remains the same
        st.write(
            """
        Welcome to AI Recruiter Agency, a cutting-edge recruitment analysis system powered by:

        - **Ollama (llama3.2)**: Advanced language model for natural language processing
        - **Swarm Framework**: Coordinated AI agents for specialized tasks
        - **Streamlit**: Modern web interface for easy interaction

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
    # Initialize session state keys needed by the clear_state callback before widgets are rendered
    # if 'uploaded_file_key' not in st.session_state:
    #    st.session_state['uploaded_file_key'] = None
    main()