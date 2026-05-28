"""Reference validation utilities."""

import re
from datetime import datetime


def check_type_tag(ref_text: str) -> bool:
    """Check if reference has a proper document type tag [J], [M], [C], etc."""
    return bool(re.search(r'\[[A-Z]+(/[A-Z]+)?\]', ref_text))


def check_year_valid(year: str) -> bool:
    """Check if year is valid (1900 to current year)."""
    if not year:
        return False
    try:
        y = int(year)
        current_year = datetime.now().year
        return 1900 <= y <= current_year
    except (ValueError, TypeError):
        return False


def check_author_format(authors: list, style: str = 'gbt7714') -> list:
    """Validate author name formatting.

    Returns list of issues found.
    """
    issues = []
    for author in authors:
        parts = author.strip().split()
        if len(parts) < 2:
            issues.append(f"Author name may be incomplete: '{author}'")
    return issues


def check_citation_coverage(cited_nums: set, ref_nums: set) -> dict:
    """Compare cited numbers vs reference list numbers.

    Returns:
        { 'orphan': [uncited refs], 'missing': [unmatched citations], 'ok': bool }
    """
    orphan = sorted(ref_nums - cited_nums)
    missing = sorted(cited_nums - ref_nums)
    return {
        'orphan': orphan,
        'missing': missing,
        'ok': len(orphan) == 0 and len(missing) == 0,
    }


def check_sequential(ref_nums: list) -> list:
    """Check if reference numbers are sequential with no gaps.

    Returns list of issues (empty if OK).
    """
    issues = []
    sorted_nums = sorted(ref_nums)
    expected = list(range(1, len(sorted_nums) + 1))
    if sorted_nums != expected:
        issues.append(f"Numbers not sequential. Expected {expected}, got {sorted_nums}")
    return issues


def check_duplicates(ref_texts: list) -> list:
    """Check for duplicate references.

    Returns list of (idx1, idx2) pairs that appear to be duplicates.
    """
    duplicates = []
    for i in range(len(ref_texts)):
        for j in range(i + 1, len(ref_texts)):
            # Compare first 100 chars (title similarity)
            a = ref_texts[i][:100].lower().strip()
            b = ref_texts[j][:100].lower().strip()
            if a == b or _similarity(a, b) > 0.8:
                duplicates.append((i + 1, j + 1))
    return duplicates


def _similarity(a: str, b: str) -> float:
    """Simple Jaccard similarity on word sets."""
    set_a = set(a.split())
    set_b = set(b.split())
    if not set_a and not set_b:
        return 1.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union > 0 else 0.0


def check_recency(refs: list, years: list, threshold: int = 5) -> dict:
    """Check proportion of references from last N years.

    Returns {'recent_count': N, 'total': N, 'ratio': float, 'ok': bool}
    """
    current_year = datetime.now().year
    recent_count = sum(1 for y in years if y and (current_year - int(y)) <= threshold)
    total = len(refs)
    ratio = recent_count / total if total > 0 else 0
    return {
        'recent_count': recent_count,
        'total': total,
        'ratio': ratio,
        'ok': ratio >= 0.5,
    }


def validate_all(ref_texts: list, cited_nums: set, ref_nums: set, years: list, style: str = 'gbt7714') -> dict:
    """Run all validation checks and return comprehensive report."""
    report = {
        'total_refs': len(ref_texts),
        'style': style,
        'issues': [],
        'warnings': [],
        'passed': True,
    }

    # Check type tags
    missing_tags = 0
    for ref in ref_texts:
        if not check_type_tag(ref):
            missing_tags += 1
    if missing_tags > 0:
        report['warnings'].append(f"{missing_tags} references missing type tag [J]/[M]/[C]/etc.")
        report['passed'] = False

    # Check citation coverage
    coverage = check_citation_coverage(cited_nums, ref_nums)
    if coverage['orphan']:
        report['issues'].append(f"Orphan refs (in bib but not cited): {coverage['orphan']}")
        report['passed'] = False
    if coverage['missing']:
        report['issues'].append(f"Missing refs (cited but not in bib): {coverage['missing']}")
        report['passed'] = False

    # Check sequential
    seq_issues = check_sequential(list(ref_nums))
    report['issues'].extend(seq_issues)
    if seq_issues:
        report['passed'] = False

    # Check duplicates
    dups = check_duplicates(ref_texts)
    if dups:
        report['warnings'].append(f"Potential duplicates: {dups}")
        report['passed'] = False

    # Check recency
    recency = check_recency(ref_texts, years)
    report['recency'] = recency
    if not recency['ok']:
        report['warnings'].append(
            f"Only {recency['recent_count']}/{recency['total']} refs from last 5 years "
            f"({recency['ratio']*100:.0f}%, need >=50%)"
        )

    # Check minimum count
    min_refs = 15
    if report['total_refs'] < min_refs:
        report['issues'].append(f"Only {report['total_refs']} refs, minimum recommended is {min_refs}")
        report['passed'] = False

    return report
