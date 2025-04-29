from typing import Dict, Any 
from .base_agent import BaseAgent 

class AnalyzerAgent(BaseAgent):
  def __init__(self):
    super().__init__(
    name="Analyzer",
    instructions="""Analyze cadidate profiles and extract:
    1 . Technical skilss (as a list) 
    2 . Years of experience (numeric) 
    3 . Education level 
    4 . Experience level (junior/mid/Senior)
    5. Key achievements 
    6 . Domain expertise
    
    Format the input as structured data.""", 
    )
    
  async def run(self, messages:list) -> Dict[str, Any]:
    """Analyze the extracted resume data"""
    print("🔍 Analyzer: Analyzing candidate profile")
    
    extracted_data =  eval(messages[-1]["content"])
    
    # Get strutured analysis from ollama
    analysis_prompt = f"""
    Analyse this resume and return a JSON object with the following structure:
    {{
      "technical_skills": ["skill1", "skill2"], 
      "years_of_experience" : number, 
      "education" : {{ 
          "level": "Bachelors/Masters/PhD",
          "field": "field of study"        
     }},
     "experience_level":"Junior/Mid/Senior", 
     "key_achievements": ["achievement1", "achievement2"], 
     "domain_expertise" : ["domain1", "domain2"],
    }}
    
    Resume data: 
    {extracted_data["structured_data"]} 
    
    Return only the JSON object, no other text.
    """
    
    analysis_results = self._query_ollama(analysis_prompt) 
    parsed_results = self._parse_json_safely(analysis_results) 
    
    # Ensure we have valid data even if parsing fails.
    if "error" in parsed_results: 
      parsed_results = { 
            "technical_skills": [], 
            "years_of_experience": 0,
            "education": {"level": "Unknown","field": "Unknown"},
            "experience_level": "Junior",
            "key_achievements": [],
            "domain_expertise": [],
      }
    return { 
            "skills_analysis": parsed_results,
            "analysis_timestamp": "2025-04-28",
            "confidence_score": 0.85 if "error" not in parsed_results else 0.5,
            }
    