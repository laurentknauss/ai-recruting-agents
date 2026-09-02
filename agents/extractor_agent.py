from typing import Dict, Any
import json
from pdfminer.high_level import extract_text
from .base_agent import BaseAgent


class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Extractor",
            instructions="""Extract and structure information from resumes.
            Focus on: personal info, work experience, education, skills, and certifications.
            Provide output in a clear, structured format."""
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process the resume and extract information."""
        print("Extractor: Processing resume")

        try:
            resume_data = json.loads(messages[-1]["content"])
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Invalid resume payload: {e}") from e

        if not isinstance(resume_data, dict):
            raise ValueError("Resume payload must be a JSON object")

        if resume_data.get("file_path"):
            raw_text = extract_text(resume_data["file_path"])
        else:
            raw_text = resume_data.get("text", "")

        extracted_info = self._query_ollama(raw_text)

        return {
            "raw_text": raw_text,
            "structured_data": extracted_info,
            "extraction_status": "completed"
        }
