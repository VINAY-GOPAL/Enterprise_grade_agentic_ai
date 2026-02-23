import json
import logging
import sys
import threading
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    stream=sys.stdout,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from bedrock_agentcore import BedrockAgentCoreApp
    logger.info("BedrockAgentCoreApp imported successfully")
    from crew import Emergingtechnologyresearch
    logger.info("Crew imported successfully")
except Exception as e:
    logger.error(f"Import failed: {e}", exc_info=True)
    sys.exit(1)

from bedrock_agentcore import BedrockAgentCoreApp
from crew import Emergingtechnologyresearch

# Create AgentCore App
app = BedrockAgentCoreApp()

# Per-session storage for async research results (avoids HTTP timeout for long-running crew)
_session_results = {}
_session_lock = threading.Lock()


def _run_crew_in_background(task_id: int, session_id: str, topic: str):
    """Run the crew in a background thread and store the result."""
    try:
        inputs = {
            "topic": topic,
            "current_year": str(datetime.now().year),
        }
        result = Emergingtechnologyresearch().crew().kickoff(inputs=inputs)
        output = result.raw
        response = output.model_dump() if hasattr(output, "model_dump") else output
        with _session_lock:
            _session_results[session_id] = {"status": "ready", "result": response}
        logger.info("Research completed for session %s, topic=%s", session_id, topic)
    except Exception as e:
        logger.exception("Research failed for session %s", session_id)
        with _session_lock:
            _session_results[session_id] = {"status": "error", "error": str(e)}
    finally:
        app.complete_async_task(task_id)


def _extract_topic(payload) -> str:
    """Extract topic from payload. Handles various structures from CLI and Bedrock API."""
    if not isinstance(payload, dict):
        return "AI LLMs"
    topic = payload.get("topic")
    if topic is not None:
        if isinstance(topic, str):
            return topic
        if isinstance(topic, dict):
            return topic.get("topic") or topic.get("prompt") or "AI LLMs"
    # Bedrock API may wrap the original payload in "payload" key
    wrapped = payload.get("payload")
    if isinstance(wrapped, str):
        try:
            inner = json.loads(wrapped)
            return inner.get("topic", "AI LLMs") if isinstance(inner, dict) else "AI LLMs"
        except json.JSONDecodeError:
            return wrapped if wrapped else "AI LLMs"
    if isinstance(wrapped, dict):
        return wrapped.get("topic") or wrapped.get("prompt") or "AI LLMs"
    # CLI wraps in "prompt" when JSON parse fails
    prompt = payload.get("prompt")
    if isinstance(prompt, str):
        if prompt.strip().startswith("{"):
            try:
                inner = json.loads(prompt)
                return inner.get("topic", prompt) if isinstance(inner, dict) else prompt
            except json.JSONDecodeError:
                pass
        return prompt
    # Nested structure
    inner = payload.get("input") or payload.get("body")
    if isinstance(inner, dict):
        return inner.get("topic") or inner.get("prompt") or "AI LLMs"
    return "AI LLMs"


@app.entrypoint
def invoke(payload, context):
    topic = _extract_topic(payload)
    session_id = (getattr(context, "session_id", None) or "default") if context else "default"

    with _session_lock:
        stored = _session_results.get(session_id)

    # Result ready from previous invocation
    if stored and stored.get("status") == "ready":
        with _session_lock:
            del _session_results[session_id]
        return stored["result"]

    # Error from previous invocation
    if stored and stored.get("status") == "error":
        with _session_lock:
            del _session_results[session_id]
        raise Exception(stored.get("error", "Unknown error"))

    # Still processing
    if stored and stored.get("status") == "processing":
        return {
            "status": "processing",
            "message": "Research still in progress. Invoke again in about 60 seconds to get your report.",
            "topic": topic,
        }

    # Start new research
    task_id = app.add_async_task("research", {"topic": topic, "session_id": session_id})
    with _session_lock:
        _session_results[session_id] = {"status": "processing"}

    thread = threading.Thread(
        target=_run_crew_in_background,
        args=(task_id, session_id, topic),
        daemon=True,
    )
    thread.start()

    return {
        "status": "started",
        "message": f"Research started for '{topic}'. Invoke again in about 60 seconds to get your report.",
        "topic": topic,
    }

if __name__ == "__main__":
  import warnings
  warnings.filterwarnings("ignore", module="requests")
  port = 8080
  print(f"\nServer starting at http://127.0.0.1:{port}/invocations\n")
  app.run(port=port)
