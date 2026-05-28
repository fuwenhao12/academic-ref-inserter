"""DOI and metadata lookup via CrossRef API.

Free, no API key required for basic usage.
Rate limit: ~50 requests/second with polite email.
"""

import json
import urllib.request
import urllib.parse
import time
from datetime import datetime


CROSSREF_BASE = "https://api.crossref.org/works"
_USER_AGENT = "AcademicRefInserter/1.0 (mailto:dev@example.com)"
_last_request = 0
_MIN_INTERVAL = 0.2  # 200ms between requests


def _rate_limit():
    global _last_request
    elapsed = time.time() - _last_request
    if elapsed < _MIN_INTERVAL:
        time.sleep(_MIN_INTERVAL - elapsed)
    _last_request = time.time()


def lookup_doi(doi: str) -> dict:
    """Look up metadata for a DOI via CrossRef API.

    Returns dict with: authors, title, journal, year, volume, issue, pages, doi, type, publisher
    Returns None if lookup fails.
    """
    _rate_limit()
    url = f"{CROSSREF_BASE}/{urllib.parse.quote(doi, safe='')}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return None

    msg = data.get("message", {})
    if not msg:
        return None

    result = {
        'type': _detect_crossref_type(msg),
        'doi': msg.get('DOI', doi),
    }

    # Authors
    authors = []
    for author in msg.get("author", []):
        family = author.get("family", "")
        given = author.get("given", "")
        if family and given:
            authors.append(f"{given} {family}")
        elif family:
            authors.append(family)
    result['authors'] = authors

    # Title
    titles = msg.get("title", [])
    result['title'] = titles[0] if titles else ""

    # Container (journal/proceedings)
    container = msg.get("container-title", [])
    result['journal'] = container[0] if container else ""

    # Year
    date_parts = msg.get("published-print", {}).get("date-parts", [[None]])[0]
    if not date_parts[0]:
        date_parts = msg.get("issued", {}).get("date-parts", [[None]])[0]
    result['year'] = str(date_parts[0]) if date_parts and date_parts[0] else ""

    # Volume/Issue
    result['volume'] = msg.get("volume", "")
    result['issue'] = msg.get("issue", "")

    # Pages
    result['pages'] = msg.get("page", "")

    # Publisher
    result['publisher'] = msg.get("publisher", "")

    # DOI URL
    result['url'] = f"https://doi.org/{result['doi']}" if result['doi'] else ""

    return result


def _detect_crossref_type(msg: dict) -> str:
    """Detect reference type from CrossRef message."""
    ref_type = msg.get("type", "").lower()
    type_map = {
        "journal-article": "journal",
        "proceedings-article": "conference",
        "book": "book",
        "book-chapter": "book",
        "dissertation": "dissertation",
        "report": "other",
        "standard": "standard",
        "dataset": "electronic",
        "posted-content": "journal",  # preprints
    }
    return type_map.get(ref_type, "other")


def lookup_by_title(title: str, max_results: int = 3) -> list:
    """Search CrossRef by title and return top matches.

    Returns list of dicts (same format as lookup_doi).
    """
    _rate_limit()
    params = urllib.parse.urlencode({
        "query": title,
        "rows": str(max_results),
    })
    url = f"{CROSSREF_BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except Exception:
        return []

    results = []
    for item in data.get("message", {}).get("items", []):
        doi = item.get("DOI", "")
        if doi:
            r = lookup_doi(doi)
            if r:
                results.append(r)
    return results


def format_from_doi(doi: str, fmt_name: str) -> str:
    """Look up DOI and format it in the given style. Returns formatted string."""
    from formats.gbt7714 import GBT7714Format
    from formats.ieee import IEEEFormat
    from formats.apa7 import APA7Format
    from formats.chicago import ChicagoFormat
    from formats.mla import MLAFormat
    from formats.harvard import HarvardFormat

    formats = {
        'gbt7714': GBT7714Format(),
        'ieee': IEEEFormat(),
        'apa7': APA7Format(),
        'chicago': ChicagoFormat(),
        'mla': MLAFormat(),
        'harvard': HarvardFormat(),
    }

    fmt = formats.get(fmt_name)
    if not fmt:
        return None

    ref = lookup_doi(doi)
    if not ref:
        return None

    return fmt.format(ref)
