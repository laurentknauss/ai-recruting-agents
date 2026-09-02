from typing import List, Dict, Any
import json
import sqlite3
from .base_agent import BaseAgent
from db.database import JobDatabase


class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Matcher",
            instructions="""Match candidate profiles with job positions.
            Consider skills match, experience level, and location preference.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields.""",
        )
        self.db = JobDatabase()

    async def run(self, messages: list) -> Dict[str, Any]:
        """Match candidate with available positions."""
        print("Matcher: Finding suitable job matches")

        try:
            content = messages[-1].get("content", "{}")
            analysis_result = json.loads(content)
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            print(f"Error parsing analysis results: {e}")
            return {"matched_jobs": [], "match_timestamp": "2026-09-02", "number_of_matches": 0}

        skills_analysis = analysis_result.get("skills_analysis", {})
        if not skills_analysis:
            print("No skills analysis provided in the input.")
            return {"matched_jobs": [], "match_timestamp": "2026-09-02", "number_of_matches": 0}

        skills = skills_analysis.get("technical_skills", [])
        experience_level = skills_analysis.get("experience_level", "Mid")

        if not isinstance(skills, list):
            skills = []
        skills = [skill for skill in skills if isinstance(skill, str) and skill.strip()]

        if experience_level not in ["Junior", "Mid", "Senior"]:
            print("Invalid experience level detected, defaulting to Mid")
            experience_level = "Mid"

        print(f"==>> Skills: {skills}, Experience Level: {experience_level}")
        matching_jobs = self.search_jobs(skills, experience_level)

        scored_jobs = []
        candidate_skills = {skill.lower() for skill in skills}
        for job in matching_jobs:
            required_skills = {skill.lower() for skill in job["requirements"]}
            overlap = len(required_skills.intersection(candidate_skills))
            total_required = len(required_skills)
            match_score = int((overlap / total_required) * 100) if total_required else 0

            if match_score >= 30:
                scored_jobs.append({
                    "title": f"{job['title']} at {job['company']}",
                    "match_score": f"{match_score}%",
                    "location": job["location"],
                    "salary_range": job["salary_range"],
                    "requirements": job["requirements"],
                })

        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)

        return {
            "matched_jobs": scored_jobs[:3],
            "match_timestamp": "2026-09-02",
            "number_of_matches": len(scored_jobs),
        }

    def search_jobs(self, skills: List[str], experience_level: str) -> List[Dict[str, Any]]:
        """Search jobs based on skills and experience level."""
        level_aliases = {
            "Junior": ["Junior", "Entry-level"],
            "Mid": ["Mid", "Mid-level"],
            "Senior": ["Senior"],
        }
        levels = level_aliases.get(experience_level, [experience_level])

        if not skills:
            return []

        placeholders = ", ".join("?" for _ in levels)
        query = f"""
            SELECT * FROM jobs
            WHERE experience_level IN ({placeholders})
            AND ({" OR ".join("requirements LIKE ?" for _ in skills)})
        """
        params = levels + [f"%{skill}%" for skill in skills]

        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(query, params).fetchall()
                return [
                    {
                        "id": row["id"],
                        "title": row["title"],
                        "company": row["company"],
                        "location": row["location"],
                        "type": row["type"],
                        "experience_level": row["experience_level"],
                        "salary_range": row["salary_range"],
                        "description": row["description"],
                        "requirements": json.loads(row["requirements"]),
                        "benefits": json.loads(row["benefits"]) if row["benefits"] else [],
                    }
                    for row in rows
                ]
        except (sqlite3.Error, json.JSONDecodeError, KeyError) as e:
            print(f"Error searching jobs: {e}")
            return []
