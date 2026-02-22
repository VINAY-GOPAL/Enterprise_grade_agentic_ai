import logging
import sys
logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from bedrock_agentcore import BedrockAgentCoreApp
    logger.info("BedrockAgentCoreApp imported successfully")
    from datetime import datetime
    import json
    logger.info("Standard imports successful")
    from crew import Emergingtechnologyresearch
    logger.info("Crew imported successfully")
except Exception as e:
    logger.error(f"Import failed: {e}", exc_info=True)
    sys.exit(1)

from bedrock_agentcore import BedrockAgentCoreApp
from datetime import datetime
# from . crews.researchCrew import Emergingtechnologyresearch
# from . utils.env import populateEnvWithSecrets
import json
from crew import Emergingtechnologyresearch

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
