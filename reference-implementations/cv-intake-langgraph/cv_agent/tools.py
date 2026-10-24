"""Mocked tools the agent can call.

Every external system (chat, Drive, parser, LLM, sheet) is replaced by an
in-memory fake so the prototype runs offline with no credentials. The "LLM"
is a deterministic keyword matcher: the point of the prototype is the control
flow around a model, not the model.
"""
from typing import Any

ALLOWED_MATCH_FIELDS = ("opportunity", "confidence", "notes")

CATALOGUE: dict[str, tuple[str, ...]] = {
    "Software Engineering": ("python", "django", "sql", "javascript", "node"),
    "Marketing": ("seo", "social media", "branding", "content"),
    "Teaching": ("tutoring", "curriculum", "training"),
}

FLAKY_FAILURES = 2


class ParseError(Exception):
    """Raised when a CV cannot be parsed."""


class Tools:
    def __init__(self, extra_llm_fields: dict[str, Any] | None = None) -> None:
        self.seen: set[str] = set()
        self.drive: dict[str, dict[str, str]] = {}
        self.sheet: dict[str, dict[str, Any]] = {}
        self.failures: list[dict[str, str]] = []
        self._parse_calls: dict[str, int] = {}
        self._extra_llm_fields = extra_llm_fields or {}

    def register_message(self, message_id: str) -> bool:
        """Return True the first time a message is seen, False after."""
        if message_id in self.seen:
            return False
        self.seen.add(message_id)
        return True

    def upload(self, message_id: str, filename: str, text: str) -> str:
        drive_id = f"drive-{message_id}"
        self.drive[drive_id] = {"filename": filename, "text": text}
        return drive_id

    def parse(self, message_id: str, text: str) -> dict[str, str]:
        calls = self._parse_calls.get(message_id, 0) + 1
        self._parse_calls[message_id] = calls
        if "[CORRUPT]" in text:
            raise ParseError("unreadable document")
        if "[FLAKY]" in text and calls <= FLAKY_FAILURES:
            raise ParseError("transient parser error")
        fields: dict[str, str] = {}
        for line in text.splitlines():
            key, sep, value = line.partition(":")
            if sep:
                fields[key.strip().lower()] = value.strip()
        return fields

    def llm_match(self, record: dict[str, Any]) -> dict[str, Any]:
        """Stand-in for an LLM call: score the candidate against the catalogue."""
        skills = {s.lower() for s in record.get("skills", [])}
        best, hits = "Unknown", 0
        for opportunity, keywords in CATALOGUE.items():
            count = len(skills & set(keywords))
            if count > hits:
                best, hits = opportunity, count
        confidence = round(min(1.0, 0.3 + 0.2 * hits), 2) if hits else 0.2
        raw_output = {
            "opportunity": best,
            "confidence": confidence,
            "notes": f"{hits} catalogue keyword(s) matched",
            **self._extra_llm_fields,
        }
        return {k: v for k, v in raw_output.items() if k in ALLOWED_MATCH_FIELDS}

    def upsert(self, key: str, entry: dict[str, Any]) -> bool:
        """Write by unique key. Return True if an existing row was updated."""
        existed = key in self.sheet
        self.sheet[key] = entry
        return existed

    def record_failure(self, message_id: str, error: str) -> None:
        self.failures.append({"message_id": message_id, "error": error})
