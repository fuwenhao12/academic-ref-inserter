"""Reference parser: extracts structured data from raw reference text."""

import re


REF_TYPE_PATTERNS = {
    'journal': [
        r'\.\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*\d{4}',
        r'\[J\]',
        r'\.\s*(?:arXiv|IEEE|ACM|Springer|Elsevier|Nature|Science|NeurIPS|ICML|ICLR|AAAI|CVPR)',
    ],
    'conference': [
        r'\[C\]',
        r'//',
        r'Proceedings of',
        r'In\s+',
    ],
    'book': [
        r'\[M\]',
        r'\.\s*(?:Press|Publishing|Books|Wiley|Springer)\b',
    ],
    'dissertation': [
        r'\[D\]',
        r'[Pp]h\.?[Dd]\.?\s+[Dd]issertation',
        r'[Mm]aster\'?s?\s+[Tt]hesis',
        r'[Dd]issertation',
    ],
    'patent': [
        r'\[P\]',
        r'Patent',
    ],
    'standard': [
        r'\[S\]',
        r'\b(?:ISO|GB|IEC|IEEE\s+Std)\b',
        r'Standard',
    ],
    'electronic': [
        r'\[EB/OL\]',
        r'\[Online\]',
        r'Available:',
        r'http[s]?://',
    ],
}


def detect_type(ref_text: str) -> str:
    """Detect reference type from text.

    Priority: explicit type tags [J][M][C][D] > content patterns.
    """
    # First pass: check explicit type tags (highest priority)
    tag_map = {
        '[J]': 'journal', '[C]': 'conference', '[M]': 'book',
        '[D]': 'dissertation', '[P]': 'patent', '[S]': 'standard',
        '[EB/OL]': 'electronic', '[R]': 'report',
    }
    for tag, ref_type in tag_map.items():
        if tag in ref_text.upper():
            return ref_type

    # Second pass: check content-based patterns
    text_lower = ref_text.lower()
    for ref_type, patterns in REF_TYPE_PATTERNS.items():
        # Skip patterns that overlap with already-checked tag patterns
        if any(tag in ref_text.upper() for tag in ['[J]', '[M]', '[C]', '[D]', '[P]', '[S]', '[EB/OL]']):
            continue
        for pattern in patterns:
            if re.search(pattern, text_lower if not pattern.startswith(r'\.') else ref_text):
                return ref_type
    return 'other'


def parse_authors(ref_text: str) -> list:
    """Extract author names from reference text.

    Handles formats:
    - Wang Y, Wu H, Dong J, et al.
    - A. Author, B. Author
    - Author, A. A., & Author, B. B.
    - 刘云, 胡涛, 张华, 等
    """
    # Remove leading [N]
    text = re.sub(r'^\[\d+\]\s*', '', ref_text)

    # Split on patterns that separate authors from title
    # Try to find the title boundary
    title_markers = [
        r'\.[\s]*["\u201c]',     # English: . "Title"
        r'\.\s+[A-Z]',            # English: . Title
        r'\]\.\s*',               # Type tag: [J]. Title
        r'\.[\s]*\u300c',          # Chinese: . 「Title
    ]

    author_part = text
    for marker in title_markers:
        m = re.search(marker, text)
        if m:
            author_part = text[:m.start() + 1]
            break

    author_part = author_part.strip('.,; ')

    # Split by commas and "et al."/"等"
    parts = re.split(r',|\s+et\s+al\.?|\u7b49', author_part)
    authors = []
    for p in parts:
        p = p.strip('.,; ')
        if p and not p.startswith('[') and not re.match(r'^\d{4}$', p):
            # Filter out "et al" and "等" leftover fragments
            if p.lower() in ('et al', 'et al.', '等', 'al.', 'al'):
                continue
            authors.append(p)

    return authors


def parse_ref(ref_text: str) -> dict:
    """Parse a single reference text into structured fields."""
    result = {
        'raw': ref_text,
        'type': detect_type(ref_text),
        'authors': parse_authors(ref_text),
        'year': '',
        'title': '',
        'journal': '',
        'volume': '',
        'issue': '',
        'pages': '',
        'publisher': '',
        'doi': '',
    }

    # Remove leading [N]
    text = re.sub(r'^\[\d+\]\s*', '', ref_text).strip()

    # Extract title: between authors and first period/type-tag
    # Remove authors part first
    author_text = ', '.join(result['authors']) if result['authors'] else ''
    if author_text and author_text in text:
        after_authors = text.split(author_text, 1)[-1].strip().lstrip('. ')
        # Title ends at [J], [M], [C], or ". Journal" pattern
        title_end = re.search(r'(?:\.\s*\[[A-Z]+(/[A-Z]+)?\]|\.\s+[A-Z][a-z]+\s+(?:et\s+al\.)?\s*,\s*\d{4})', after_authors)
        if title_end:
            result['title'] = after_authors[:title_end.start()].strip().strip('.')
        else:
            # Try up to next period
            next_period = after_authors.find('.')
            if next_period > 0:
                result['title'] = after_authors[:next_period].strip()
            else:
                result['title'] = after_authors[:100].strip()

    # Extract year
    year_match = re.search(r'(?:\(?)(\d{4})(?:\)?)', text)
    if year_match:
        result['year'] = year_match.group(1)

    # Extract journal name (words after title, before year/volume)
    title_text = re.escape(result['title']) if result['title'] else ''
    if title_text and result['title'] in text:
        after_title = text.split(result['title'], 1)[-1].strip().lstrip('. ')
        # Remove [J] etc.
        after_title = re.sub(r'^\[[A-Z]+(/[A-Z]+)?\]\s*\.?\s*', '', after_title)
        # Try to extract journal name: up to ", YYYY" or ", vol."
        journal_end = re.search(r'(?:,\s*\d{4}|,\s*(?:vol|no)\.)', after_title)
        if journal_end:
            result['journal'] = after_title[:journal_end.start()].strip()
        else:
            # Take first 50 chars as journal guess
            result['journal'] = after_title[:50].strip().rstrip(',')

    # Extract DOI
    doi_match = re.search(r'(?:doi|DOI)\s*[:\s]\s*(10\.\S+)', ref_text)
    if doi_match:
        result['doi'] = doi_match.group(1)

    # Extract pages
    pages_match = re.search(r'(?:pp?\.?\s*)(\d+[--]\d+)', ref_text)
    if pages_match:
        result['pages'] = pages_match.group(1)

    # Extract volume/issue
    vol_match = re.search(r'(?:vol\.?\s*)(\d+)\s*(?:,\s*(?:no\.?\s*|\(?)(\d+)\)?)?', ref_text, re.IGNORECASE)
    if vol_match:
        result['volume'] = vol_match.group(1)
        if vol_match.group(2):
            result['issue'] = vol_match.group(2)

    # Extract URL
    url_match = re.search(r'(https?://\S+)', ref_text)
    if url_match:
        result['url'] = url_match.group(1)

    return result


def parse_reference_list(refs: list) -> list:
    """Parse a list of raw reference text strings into structured dicts."""
    return [parse_ref(r) for r in refs]
