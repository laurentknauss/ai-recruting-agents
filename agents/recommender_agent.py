from typing import Dict, Any
import json
from .base_agent import BaseAgent


class RecommenderAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Recommender",
            instructions="""Generate final recommendations considering:
            1. Extracted profile
            2. Skills analysis
            3. Job matches
            4. Screening results
            Provide clear next steps and specific recommendations.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Generate final recommendations."""
        print("Recommender: Generating final recommendations")

        try:
            workflow_context = json.loads(messages[-1]["content"])
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"Invalid workflow context: {e}") from e

        if not isinstance(workflow_context, dict):
            raise ValueError("Workflow context must be a JSON object")

        recommendation = self._query_ollama(json.dumps(workflow_context))

        return {
            "final_recommendation": recommendation,
            "recommendation_timestamp": "2026-09-02",
            "confidence_level": "high",
        }
