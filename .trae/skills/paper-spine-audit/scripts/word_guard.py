#!/usr/bin/env python3
"""Lightweight structural checks for generated Word .docx files."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree


PLACEHOLDER_PATTERNS = (
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\?\?",
    r"\[\[",
    r"\]\]",
)


@dataclass
class WordGuardResult:
    path: str
    ok: bool
    text_length: int
    paragraph_count: int
    findings: list[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a generated .docx file.")
    parser.add_argument("docx_path")
    parser.add_argument("--min-chars", type=int, default=200)
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path, help="Optional report path.")
    return parser.parse_args()


def extract_text(document_xml: bytes) -> tuple[str, int]:
    root = ElementTree.fromstring(document_xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    for paragraph in root.findall(".//w:p", ns):
        parts = [node.text or "" for node in paragraph.findall(".//w:t", ns)]
        text = "".join(parts).strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs), len(paragraphs)


def check_docx(path: Path, min_chars: int) -> WordGuardResult:
    findings: list[str] = []
    text = ""
    paragraph_count = 0

    if not path.exists():
        return WordGuardResult(str(path), False, 0, 0, ["file does not exist"])
    if path.suffix.lower() != ".docx":
        findings.append("file extension is not .docx")

    try:
        with zipfile.ZipFile(path) as docx:
            names = set(docx.namelist())
            for required in ("[Content_Types].xml", "word/document.xml"):
                if required not in names:
                    findings.append(f"missing {required}")
            if "word/document.xml" in names:
                text, paragraph_count = extract_text(docx.read("word/document.xml"))
    except zipfile.BadZipFile:
        return WordGuardResult(str(path), False, 0, 0, ["not a valid zip/docx file"])
    except ElementTree.ParseError as exc:
        findings.append(f"word/document.xml parse error: {exc}")

    if len(text) < min_chars:
        findings.append(f"text is too short: {len(text)} chars < {min_chars}")
    if paragraph_count == 0:
        findings.append("no non-empty paragraphs found")
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(f"unresolved placeholder pattern found: {pattern}")

    return WordGuardResult(str(path), not findings, len(text), paragraph_count, findings)


def to_markdown(result: WordGuardResult) -> str:
    lines = [
        "# Word Guard Report",
        "",
        f"- Path: `{result.path}`",
        f"- Status: {'PASS' if result.ok else 'FAIL'}",
        f"- Text length: {result.text_length}",
        f"- Paragraph count: {result.paragraph_count}",
        "",
        "## Findings",
        "",
    ]
    if result.findings:
        lines.extend(f"- {finding}" for finding in result.findings)
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    result = check_docx(Path(args.docx_path), args.min_chars)
    markdown = to_markdown(result)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")

    if args.json:
        print(json.dumps(result.__dict__, ensure_ascii=False, indent=2))
    if args.markdown or not args.json:
        print(markdown)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
