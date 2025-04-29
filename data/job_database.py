import json 
from typing import Dict, Any

from swarms import Agent, Swarm 
from openai import OpenAI

ollama_client = OpenAI(
  base_url="http://localhost:11434/v1", 
  api_key="ollama" # required by the openAI library but not used 
  
)

# Initialize swarm client 
client = Swarm(client=ollama_client)

def extractor_agent_function(resume:str) -> Dict[str, Any]: 
  # use the ollama model to extract key information
  response = ollama_client.chat.completions.create(
    model="llama3.2",
    messages=[
      { 
       "role": "system", 
       "content": "Extract the name , skills, experience, and education from the following resume:\n{resume}\nReturn the data in JSON format.", 
       }
    ],
    
    
  )
  extracted_data = json.loads(response["completion"].strip()) 
  return extracted_data

extractor_agent = Agent(
  name="Extractor Agent", 
  model="llama3.2",
  instructions="Extract relevant information from resumes and provide it in JSON format.", 
  functions=[extractor_agent_function],
)