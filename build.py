#!/usr/bin/env python3
"""Embed questions.json into index.html so the page runs with no server.

Usage: python build.py
"""
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent
JSON_PATH = BASE_DIR / "questions.json"
HTML_PATH = BASE_DIR / "index.html"

REQUIRED_FIELDS = ("category", "grade", "question", "answer")

BLOCK_PATTERN = re.compile(
    r'(<script id="questions-data">\s*const QUESTIONS_DATA = )'
    r'.*?'
    r'(;\s*</script>)',
    re.DOTALL,
)


def load_and_validate_questions():
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    questions = data.get("questions", [])
    if not questions:
        sys.exit("questions.json has no questions.")

    for i, q in enumerate(questions):
        missing = [f for f in REQUIRED_FIELDS if f not in q]
        if missing:
            sys.exit(f"Question {i} is missing fields: {missing}")
        if not str(q["answer"]).strip():
            sys.exit(f"Question {i} has an empty answer.")

    return data, questions


def embed(data):
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    # Every "<" in the dump lives inside a JSON string value, so this is a
    # safe, still-valid-JSON way to stop a literal "</script>" from
    # prematurely closing the surrounding <script> tag.
    json_str = json_str.replace("<", "\\u003c")

    html = HTML_PATH.read_text(encoding="utf-8")
    new_html, count = BLOCK_PATTERN.subn(
        lambda m: m.group(1) + json_str + m.group(2), html
    )
    if count == 0:
        sys.exit('Could not find the <script id="questions-data"> block in index.html.')

    HTML_PATH.write_text(new_html, encoding="utf-8")


def main():
    data, questions = load_and_validate_questions()
    embed(data)
    print(f"Embedded {len(questions)} questions into {HTML_PATH.name}. Just open it in a browser.")


if __name__ == "__main__":
    main()
