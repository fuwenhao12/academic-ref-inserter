"""Tests for bibtex and doi_lookup modules."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils.bibtex import parse_bibtex, export_bibtex, _parse_bibtex_authors, _to_bibtex_author


SAMPLE_BIB = """
@article{wang2024,
  title = {TimeXer: Empowering transformers for time series forecasting},
  author = {Wang, Yun and Wu, Haixu and Dong, Jie},
  journal = {Advances in Neural Information Processing Systems},
  year = {2024},
  volume = {37},
  pages = {469--498}
}

@book{box2015,
  title = {Time series analysis: forecasting and control},
  author = {Box, George E. and Jenkins, Gwilym M. and Reinsel, Gregory C.},
  publisher = {John Wiley \\& Sons},
  year = {2015}
}
"""


def test_parse_bibtex():
    entries = parse_bibtex(SAMPLE_BIB)
    assert len(entries) == 2
    assert entries[0]['title'] == 'TimeXer: Empowering transformers for time series forecasting'
    assert entries[0]['year'] == '2024'
    assert entries[0]['journal'] == 'Advances in Neural Information Processing Systems'
    assert len(entries[0]['authors']) == 3
    assert entries[1]['type'] == 'book'
    assert entries[1]['publisher'] == 'John Wiley \\& Sons'
    print("  [PASS] parse_bibtex: 2 entries, journal + book")


def test_parse_bibtex_authors():
    assert _parse_bibtex_authors("Wang, Yun and Wu, Haixu") == ["Yun Wang", "Haixu Wu"]
    assert _parse_bibtex_authors("Doe, John") == ["John Doe"]
    print("  [PASS] parse_bibtex_authors")


def test_to_bibtex_author():
    assert _to_bibtex_author("Yun Wang") == "Wang, Yun"
    assert _to_bibtex_author("John Doe") == "Doe, John"
    print("  [PASS] to_bibtex_author")


def test_export_bibtex():
    refs = [{
        'type': 'journal',
        'key': 'test2024',
        'title': 'Test Paper',
        'authors': ['Yun Wang', 'Haixu Wu'],
        'journal': 'Test Journal',
        'year': '2024',
        'volume': '1',
        'pages': '1-10',
    }]
    result = export_bibtex(refs)
    assert '@article{test2024,' in result
    assert 'title = {Test Paper}' in result
    assert 'Wang, Yun' in result
    print("  [PASS] export_bibtex")


def test_bibtex_roundtrip():
    entries = parse_bibtex(SAMPLE_BIB)
    exported = export_bibtex(entries)
    reimported = parse_bibtex(exported)
    assert len(reimported) == 2
    assert reimported[0]['title'] == entries[0]['title']
    print("  [PASS] bibtex roundtrip")


if __name__ == '__main__':
    print("=== BibTeX Tests ===")
    test_parse_bibtex()
    test_parse_bibtex_authors()
    test_to_bibtex_author()
    test_export_bibtex()
    test_bibtex_roundtrip()
    print("\nAll BibTeX tests passed!")
