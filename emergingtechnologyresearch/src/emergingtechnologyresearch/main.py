#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from emergingtechnologyresearch.crew import Emergingtechnologyresearch

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

from langfuse import get_client
from openinference.instrumentation.crewai import CrewAIInstrumentor 
from openinference.instrumentation.litellm import LiteLLMInstrumentor 

langfuse = get_client()
CrewAIInstrumentor().instrument(skip_dep_check=True)
LiteLLMInstrumentor().instrument()
# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")
 

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'topic': 'Quantum Computing in cybersecurity',
        'current_year': str(datetime.now().year)
    }

    with langfuse.start_as_current_observation(
        as_type="span",
        name="emerging-technology-research-trace",
        input=inputs,
    ) as span:
        try:
            result = Emergingtechnologyresearch().crew().kickoff(inputs=inputs)
            # Serialize output for Langfuse (CrewOutput has .raw for task outputs)
            output = (
                result.model_dump()
                if hasattr(result, "model_dump")
                else (result.raw if hasattr(result, "raw") else str(result))
            )
            span.update(output=output)
        except Exception as e:
            span.update(output={"error": str(e)})
            raise Exception(f"An error occurred while running the crew: {e}")
    langfuse.flush()


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Emergingtechnologyresearch().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Emergingtechnologyresearch().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        Emergingtechnologyresearch().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = Emergingtechnologyresearch().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
