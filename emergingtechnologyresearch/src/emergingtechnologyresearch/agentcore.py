from bedrock_agentcore import BedrockAgentCoreApp
from datetime import datetime
# from . crews.researchCrew import Emergingtechnologyresearch
# from . utils.env import populateEnvWithSecrets
import json
from .crew import Emergingtechnologyresearch

# Create AgentCore App
app = BedrockAgentCoreApp()

# # Populate environment variables from AWS secrets manager
# populateEnvWithSecrets()

@app.entrypoint
def invoke(payload):
  topic = payload.get("topic", "AI LLMs")
  inputs = {
      'topic': topic,
      'current_year': str(datetime.now().year)
  }
  response = ""
  try:
    # Execute the crew
    response = Emergingtechnologyresearch().crew().kickoff(inputs=inputs).json
    response = json.loads(response)
  except Exception as e:
    raise Exception(f"An error occurred while running the crew: {e}")
  
  return response

if __name__ == "__main__":
  import warnings
  warnings.filterwarnings("ignore", module="requests")
  port = 8080
  print(f"\nServer starting at http://127.0.0.1:{port}/invocations\n")
  app.run(port=port)
