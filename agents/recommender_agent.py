from typing import Dict, Any
from .base_agent import BaseAgent

class RecommenderAgent(BaseAgent):
  def __init__(self): 
    super().__init__(
      name="Recommender", 
      instructions="""Generate final recommendations considering:
      1 . Extracted profile
      2 . skills analysis 
      3 . job matches 
      4 . Screening results  
      Provide clear next steps and specific recommendations.""",
      
    )
    
    async def run(self, messages: list) -> Dict[str, Any]: 
      """Generate final recommendations""" 
      print("💡 Recommender: Generating final recommendations")
      workflow_context = eval(messages[-1]["content"])
      recommendation = self._query_ollama(str(workflow_context))
      
      return { 
              "final recommendation": recommendation,
              "recommendation_timestamp": "2025-04-28",
              "confidence_level": "high", 
              }
      
      