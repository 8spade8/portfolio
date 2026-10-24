"""The CV intake agent expressed as a LangGraph state graph."""
import re
from typing import Any, Callable

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from cv_agent.state import JobState
from cv_agent.tools import ParseError, Tools

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def build_graph(
    tools: Tools,
    max_attempts: int = 3,
    min_confidence: float = 0.55,
    sleep: Callable[[float], None] = lambda seconds: None,
):
    """Compile the agent graph.

    ``sleep`` receives the backoff delay between parse retries; it defaults to a
    no-op so tests and demos run instantly.
    """

    def filter_dedup(state: JobState) -> dict[str, Any]:
        is_new = tools.register_message(state["message_id"])
        update: dict[str, Any] = {"trace": ["filter_dedup"], "attempts": 0}
        return update if is_new else {**update, "status": "duplicate"}

    def store_drive(state: JobState) -> dict[str, Any]:
        drive_id = tools.upload(state["message_id"], state["filename"], state["text"])
        return {"drive_id": drive_id, "trace": ["store_drive"]}

    def parse(state: JobState) -> dict[str, Any]:
        try:
            raw = tools.parse(state["message_id"], state["text"])
        except ParseError as exc:
            attempts = state.get("attempts", 0) + 1
            sleep(2 ** attempts)
            return {"attempts": attempts, "error": str(exc), "trace": ["parse"]}
        return {"raw": raw, "error": "", "trace": ["parse"]}

    def normalise(state: JobState) -> dict[str, Any]:
        raw = state["raw"]
        skills = [s.strip() for s in raw.get("skills", "").split(",") if s.strip()]
        record = {
            "fullName": raw.get("name", ""),
            "email": raw.get("email", ""),
            "skills": skills,
        }
        return {"record": record, "trace": ["normalise"]}

    def llm_match(state: JobState) -> dict[str, Any]:
        return {"match": tools.llm_match(state["record"]), "trace": ["llm_match"]}

    def validate(state: JobState) -> dict[str, Any]:
        issues: list[str] = []
        if not EMAIL_PATTERN.match(state["record"]["email"]):
            issues.append("invalid email")
        if state["match"]["confidence"] < min_confidence:
            issues.append("low confidence match")
        return {"issues": issues, "trace": ["validate"]}

    def flag_review(state: JobState) -> dict[str, Any]:
        decision = interrupt(
            {
                "issues": state["issues"],
                "record": state["record"],
                "proposed_match": state["match"],
            }
        )
        if decision.get("action") != "approve":
            return {"review": decision, "status": "rejected", "trace": ["flag_review"]}
        match = {
            **state["match"],
            "opportunity": decision.get("opportunity", state["match"]["opportunity"]),
            "human_reviewed": True,
        }
        return {"review": decision, "match": match, "trace": ["flag_review"]}

    def write_sheet(state: JobState) -> dict[str, Any]:
        key = state["record"]["email"].lower()
        entry = {
            "record": state["record"],
            "match": state["match"],
            "source": state["message_id"],
        }
        updated = tools.upsert(key, entry)
        return {"status": "updated" if updated else "written", "trace": ["write_sheet"]}

    def record_failure(state: JobState) -> dict[str, Any]:
        tools.record_failure(state["message_id"], state.get("error", "unknown"))
        return {"status": "failed", "trace": ["record_failure"]}

    def after_dedup(state: JobState) -> str:
        return END if state.get("status") == "duplicate" else "store_drive"

    def after_parse(state: JobState) -> str:
        if not state.get("error"):
            return "normalise"
        return "parse" if state["attempts"] < max_attempts else "record_failure"

    def after_validate(state: JobState) -> str:
        return "flag_review" if state["issues"] else "write_sheet"

    def after_review(state: JobState) -> str:
        return END if state.get("status") == "rejected" else "write_sheet"

    builder = StateGraph(JobState)
    builder.add_node("filter_dedup", filter_dedup)
    builder.add_node("store_drive", store_drive)
    builder.add_node("parse", parse)
    builder.add_node("normalise", normalise)
    builder.add_node("llm_match", llm_match)
    builder.add_node("validate", validate)
    builder.add_node("flag_review", flag_review)
    builder.add_node("write_sheet", write_sheet)
    builder.add_node("record_failure", record_failure)

    builder.add_edge(START, "filter_dedup")
    builder.add_conditional_edges("filter_dedup", after_dedup, ["store_drive", END])
    builder.add_edge("store_drive", "parse")
    builder.add_conditional_edges(
        "parse", after_parse, ["parse", "normalise", "record_failure"]
    )
    builder.add_edge("normalise", "llm_match")
    builder.add_edge("llm_match", "validate")
    builder.add_conditional_edges(
        "validate", after_validate, ["flag_review", "write_sheet"]
    )
    builder.add_conditional_edges("flag_review", after_review, ["write_sheet", END])
    builder.add_edge("write_sheet", END)
    builder.add_edge("record_failure", END)

    return builder.compile(checkpointer=InMemorySaver())
