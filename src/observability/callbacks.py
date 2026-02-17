import logging
import time
from typing import Any
from langchain_core.callbacks import BaseCallbackHandler

logger = logging.getLogger("scia")


class AgentTraceCallback(BaseCallbackHandler):
    """Logs agent activity for observability and debugging."""

    def __init__(self):
        self.start_times: dict[str, float] = {}

    def on_chain_start(self, serialized: dict[str, Any], inputs: dict[str, Any], *, run_id, **kwargs):
        name = serialized.get("name", "unknown")
        self.start_times[str(run_id)] = time.time()
        logger.info(f"[START] {name} (run_id={run_id})")

    def on_chain_end(self, outputs: dict[str, Any], *, run_id, **kwargs):
        elapsed = time.time() - self.start_times.pop(str(run_id), time.time())
        logger.info(f"[END] run_id={run_id} ({elapsed:.2f}s)")

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, *, run_id, **kwargs):
        tool_name = serialized.get("name", "unknown")
        logger.info(f"[TOOL] {tool_name} called (run_id={run_id})")

    def on_tool_end(self, output: str, *, run_id, **kwargs):
        preview = output[:200] if isinstance(output, str) else str(output)[:200]
        logger.info(f"[TOOL_RESULT] run_id={run_id}: {preview}")

    def on_llm_error(self, error: BaseException, *, run_id, **kwargs):
        logger.error(f"[LLM_ERROR] run_id={run_id}: {error}")

    def on_tool_error(self, error: BaseException, *, run_id, **kwargs):
        logger.error(f"[TOOL_ERROR] run_id={run_id}: {error}")
