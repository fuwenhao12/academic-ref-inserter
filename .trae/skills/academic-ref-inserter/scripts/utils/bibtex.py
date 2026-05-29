"""BibTeX (.bib) import and export utilities."""

import re


def parse_bibtex(bib_text: str) -> list:
    """Parse BibTeX content into a list of structured dicts.

    Each dict has: type, key, authors, title, journal, year, volume, pages, doi, publisher
    """
    entries = []

    blocks = _split_bibtex_blocks(bib_text)
    for entry_type, cite_key, fields_str in blocks:
        entry = {
            'type': _bib_type_to_ref_type(entry_type),
            'key': cite_key,
            'authors': [],
            'title': '',
            'journal': '',
            'year': '',
            'volume': '',
            'issue': '',
            'pages': '',
            'doi': '',
            'publisher': '',
        }

        for key, value in _parse_bibtex_fields(fields_str).items():
            if key in ('author', 'authors'):
                entry['authors'] = _parse_bibtex_authors(value)
            elif key == 'title':
                entry['title'] = value
            elif key in ('journal', 'journaltitle'):
                entry['journal'] = value
            elif key == 'year':
                entry['year'] = value.strip()
            elif key == 'volume':
                entry['volume'] = value
            elif key in ('number', 'issue'):
                entry['issue'] = value
            elif key == 'pages':
                entry['pages'] = value.replace('--', '-')
            elif key == 'doi':
                entry['doi'] = value
            elif key == 'publisher':
                entry['publisher'] = value
            elif key == 'booktitle':
                entry['journal'] = value
                entry['type'] = 'conference'

        entries.append(entry)

    return entries


def _split_bibtex_blocks(bib_text: str) -> list:
    """Split BibTeX text into (entry_type, cite_key, fields_str) tuples."""
    blocks = []
    depth = 0
    in_entry = False
    current = ""
    for ch in bib_text:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and in_entry:
                current += ch
                blocks.append(_parse_single_block(current))
                current = ""
                in_entry = False
                continue
        if ch == '@' and depth == 0:
            in_entry = True
        if in_entry:
            current += ch
    return blocks


def _parse_single_block(block: str) -> tuple:
    """Parse a single @type{key, fields} block."""
    m = re.match(r'@(\w+)\s*\{\s*([^,]+)\s*,\s*(.*)\}', block, re.DOTALL)
    if not m:
        return ('misc', 'unknown', block)
    return (m.group(1).lower(), m.group(2).strip(), m.group(3).strip())


def _parse_bibtex_fields(text: str) -> dict:
    """Parse key = {value} pairs from BibTeX field text."""
    result = {}
    current_key = None
    current_value = ""
    depth = 0

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        if '=' in line and depth == 0 and not current_key:
            key, _, rest = line.partition('=')
            key = key.strip().lower().rstrip(',')
            value = rest.strip()
            if value.endswith(','):
                value = value[:-1]
            value = value.strip().strip('{}').strip().strip('"').strip()

            # Count nested braces
            for ch in rest:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1

            if depth <= 0:
                result[key] = value
            else:
                current_key = key
                current_value = value
        elif current_key:
            val = line.strip().rstrip(',')
            for ch in val:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1

            val_clean = val.strip().strip('{}').strip().strip('"').strip()
            if current_value:
                current_value += ' ' + val_clean
            else:
                current_value = val_clean

            if depth <= 0:
                result[current_key] = current_value
                current_key = None
                current_value = ""

    return result


def _bib_type_to_ref_type(bib_type: str) -> str:
    type_map = {
        'article': 'journal',
        'inproceedings': 'conference',
        'conference': 'conference',
        'book': 'book',
        'phdthesis': 'dissertation',
        'mastersthesis': 'dissertation',
        'patent': 'patent',
        'techreport': 'other',
        'misc': 'other',
        'unpublished': 'other',
    }
    return type_map.get(bib_type, 'other')


def _parse_bibtex_authors(author_str: str) -> list:
    """Parse BibTeX author field (e.g., 'Wang, Yun and Wu, Haixu')."""
    authors = []
    for part in re.split(r'\s+and\s+', author_str, flags=re.IGNORECASE):
        part = part.strip()
        if not part:
            continue
        if ',' in part:
            last, first = part.split(',', 1)
            first = first.strip()
            last = last.strip()
            authors.append(f"{first} {last}")
        else:
            authors.append(part)
    return authors


def export_bibtex(refs: list) -> str:
    """Convert a list of structured ref dicts to BibTeX format."""
    lines = []
    for i, ref in enumerate(refs):
        bib_type = _ref_type_to_bib(ref.get('type', 'other'))
        cite_key = ref.get('key', f'ref{i+1}')

        lines.append(f"@{bib_type}{{{cite_key},")
        lines.append(f"  title = {{{ref.get('title', '')}}},")

        authors = ref.get('authors', [])
        if authors:
            bib_authors = ' and '.join(_to_bibtex_author(a) for a in authors)
            lines.append(f"  author = {{{bib_authors}}},")

        if ref.get('journal'):
            lines.append(f"  journal = {{{ref['journal']}}},")
        if ref.get('year'):
            lines.append(f"  year = {{{ref['year']}}},")
        if ref.get('volume'):
            lines.append(f"  volume = {{{ref['volume']}}},")
        if ref.get('issue'):
            lines.append(f"  number = {{{ref['issue']}}},")
        if ref.get('pages'):
            lines.append(f"  pages = {{{ref['pages']}}},")
        if ref.get('doi'):
            lines.append(f"  doi = {{{ref['doi']}}},")
        if ref.get('publisher'):
            lines.append(f"  publisher = {{{ref['publisher']}}},")

        lines[-1] = lines[-1].rstrip(',')
        lines.append("}\n")

    return '\n'.join(lines)


def _ref_type_to_bib(ref_type: str) -> str:
    type_map = {
        'journal': 'article',
        'conference': 'inproceedings',
        'book': 'book',
        'dissertation': 'phdthesis',
        'patent': 'patent',
        'standard': 'techreport',
        'electronic': 'misc',
        'other': 'misc',
    }
    return type_map.get(ref_type, 'misc')


def _to_bibtex_author(name: str) -> str:
    """Convert 'Yun Wang' to 'Wang, Yun'."""
    parts = name.strip().split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name
