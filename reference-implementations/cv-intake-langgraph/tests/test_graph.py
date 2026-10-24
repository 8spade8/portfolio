"""Behavioural tests for the CV intake graph. All data is synthetic."""
import pytest
from langgraph.types import Command

from cv_agent.graph import build_graph
from cv_agent.tools import ALLOWED_MATCH_FIELDS, Tools


def cv(message_id, name, email, skills, text_extra=""):
    return {
        "message_id": message_id,
        "filename": f"{name.replace(' ', '_')}.pdf",
        "text": f"Name: {name}\nEmail: {email}\nSkills: {skills}\n{text_extra}",
    }


def run(tools, job, thread="t1", **kwargs):
    graph = build_graph(tools, **kwargs)
    config = {"configurable": {"thread_id": thread}}
    return graph, config, graph.invoke(job, config)


def test_confident_cv_is_matched_and_written():
    tools = Tools()
    job = cv("m1", "Ada Example", "ada@example.com", "python, django, sql")

    _, _, out = run(tools, job)

    assert out["status"] == "written"
    assert tools.sheet["ada@example.com"]["match"]["opportunity"] == "Software Engineering"
    assert out["trace"] == [
        "filter_dedup", "store_drive", "parse", "normalise",
        "llm_match", "validate", "write_sheet",
    ]


def test_duplicate_message_is_skipped_without_writing():
    tools = Tools()
    job = cv("m1", "Ada Example", "ada@example.com", "python, sql")
    run(tools, job, thread="a")

    _, _, out = run(tools, job, thread="b")

    assert out["status"] == "duplicate"
    assert len(tools.sheet) == 1
    assert out["trace"] == ["filter_dedup"]


def test_flaky_parse_is_retried_then_succeeds():
    tools = Tools()
    job = cv("m2", "Bo Sample", "bo@example.com", "python, sql", "[FLAKY]")

    _, _, out = run(tools, job, max_attempts=3)

    assert out["status"] == "written"
    assert out["attempts"] == 2
    assert out["trace"].count("parse") == 3


def test_corrupt_parse_exhausts_retries_and_records_failure():
    tools = Tools()
    job = cv("m3", "Cy Broken", "cy@example.com", "python", "[CORRUPT]")

    _, _, out = run(tools, job, max_attempts=3)

    assert out["status"] == "failed"
    assert tools.sheet == {}
    assert tools.failures[0]["message_id"] == "m3"
    assert out["trace"].count("parse") == 3
    assert out["trace"][-1] == "record_failure"


def test_low_confidence_pauses_for_human_review_and_resumes_on_approve():
    tools = Tools()
    job = cv("m4", "Di Vague", "di@example.com", "communication")

    graph, config, out = run(tools, job)

    assert "__interrupt__" in out
    assert tools.sheet == {}

    final = graph.invoke(
        Command(resume={"action": "approve", "opportunity": "Marketing"}), config
    )

    assert final["status"] == "written"
    assert tools.sheet["di@example.com"]["match"]["opportunity"] == "Marketing"
    assert tools.sheet["di@example.com"]["match"]["human_reviewed"] is True


def test_human_can_reject_a_flagged_candidate():
    tools = Tools()
    job = cv("m5", "Ed Unclear", "ed@example.com", "communication")

    graph, config, _ = run(tools, job)
    final = graph.invoke(Command(resume={"action": "reject"}), config)

    assert final["status"] == "rejected"
    assert tools.sheet == {}


def test_invalid_email_is_flagged_not_written():
    tools = Tools()
    job = cv("m6", "Fay Typo", "not-an-email", "python, sql, django")

    _, _, out = run(tools, job)

    assert "__interrupt__" in out
    assert tools.sheet == {}


def test_same_candidate_twice_updates_instead_of_duplicating():
    tools = Tools()
    run(tools, cv("m7", "Gus Same", "gus@example.com", "python, sql"), thread="a")

    _, _, out = run(
        tools, cv("m8", "Gus Same", "GUS@example.com", "python, sql, django"), thread="b"
    )

    assert out["status"] == "updated"
    assert len(tools.sheet) == 1


def test_llm_output_is_restricted_to_allow_listed_fields():
    tools = Tools(extra_llm_fields={"salary": 99999, "is_admin": True})
    job = cv("m9", "Hal Strict", "hal@example.com", "python, sql, django")

    run(tools, job)

    written = tools.sheet["hal@example.com"]["match"]
    assert set(written) <= set(ALLOWED_MATCH_FIELDS) | {"human_reviewed"}
    assert "salary" not in written and "is_admin" not in written
