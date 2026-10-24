"""Run the agent over synthetic CVs, answering human-review prompts automatically."""
import json
import logging
from pathlib import Path

from langgraph.types import Command

from cv_agent.graph import build_graph
from cv_agent.tools import Tools

DATA_FILE = Path(__file__).parent / "data" / "synthetic_cvs.json"
REVIEWER_DECISION = {"action": "approve", "opportunity": "Teaching"}

log = logging.getLogger("demo")


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    tools = Tools()
    graph = build_graph(tools)

    for index, job in enumerate(json.loads(DATA_FILE.read_text(encoding="utf-8"))):
        config = {"configurable": {"thread_id": f"job-{index}"}}
        result = graph.invoke(job, config)
        if "__interrupt__" in result:
            issues = result["__interrupt__"][0].value["issues"]
            log.info("%s paused for review: %s", job["message_id"], ", ".join(issues))
            result = graph.invoke(Command(resume=REVIEWER_DECISION), config)
        log.info("%s -> %s via %s", job["message_id"], result["status"], result["trace"])

    log.info("sheet rows: %d | failures: %d", len(tools.sheet), len(tools.failures))


if __name__ == "__main__":
    main()
