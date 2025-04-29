
from typing import Dict, Any 
import json 
from openai import OpenAI 

class BaseAgent: 
  def __init__(self, name: str, instructions: str):
    self.name = name
    self.instructions = instructions
    self.ollama_client = OpenAI(
      base_url="http://localhost:11434/v1",
      api_key="ollama"  # required by opeai library but not used.
    )
    
    
  async def run(self, messages:list) -> Dict[str, Any]: 
    """Default run method to be overriden by child classes"""
    raise NotImplementedError("Subclasses must implement run()") 
  
  
  
  
  
  def _query_ollama(self, prompt: str) -> str: 
    """Query Ollama model with the given prompt""" 
    try: 
      response = self.ollama_client.chat.completions.create(
          model="llama3.2" ,
          messages=[
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": prompt}, 
          ], 
          
          temperature=0.7,
          max_tokens=2000,
 
          
      )
      return response.choices[0].message.content
    except Exception as e: 
        print(f"Error querying Ollama: {str(e)}")
        raise
  
  def _parse_json_safely(self, text: str) -> Dict[str, Any]: 
    """Safely parse JSON from text, handling potential errors"""
    try: 
        # Try to find JSON-like content between curly braces 
        start = text.find("{") 
        end = text.rfind("}") 
        
        if start != -1 and end != -1 and start < end:
            json_content = text[start:end + 1]
            return json.loads(json_content)
        else:
            raise ValueError("No valid JSON object found in the text.")
    except (json.JSONDecodeError, ValueError) as e: 
        print(f"Error parsing JSON: {str(e)}")
        return {}
        
      
    
