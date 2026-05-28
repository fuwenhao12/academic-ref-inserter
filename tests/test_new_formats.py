"""Tests for Chicago, MLA, and Harvard citation formats."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from formats.chicago import ChicagoFormat
from formats.mla import MLAFormat
from formats.harvard import HarvardFormat


def make_journal_ref():
    return {
        'authors': ['Yun Wang', 'Haixu Wu', 'Jie Dong'],
        'title': 'TimeXer: Empowering transformers for time series forecasting',
        'journal': 'Advances in Neural Information Processing Systems',
        'volume': '37',
        'issue': '',
        'pages': '469-498',
        'year': '2024',
        'doi': '10.1234/example',
        'type': 'journal',
    }


def make_book_ref():
    return {
        'authors': ['George Box', 'Gwilym Jenkins'],
        'title': 'Time series analysis: forecasting and control',
        'publisher': 'John Wiley & Sons',
        'year': '2015',
        'type': 'book',
    }


def test_chicago_journal():
    fmt = ChicagoFormat()
    ref = make_journal_ref()
    result = fmt.format(ref)
    assert '"TimeXer:' in result
    assert 'Wang, Yun' in result
    assert '2024' in result
    assert '469-498' in result
    print(f"  [PASS] chicago journal: {result[:80]}...")


def test_chicago_book():
    fmt = ChicagoFormat()
    ref = make_book_ref()
    result = fmt.format(ref)
    assert 'Box, George' in result
    assert '2015' in result
    assert 'John Wiley' in result or 'Sons' in result
    print(f"  [PASS] chicago book: {result[:80]}...")


def test_mla_journal():
    fmt = MLAFormat()
    ref = make_journal_ref()
    result = fmt.format(ref)
    assert 'Wang, Yun' in result
    assert 'vol. 37' in result
    assert '2024' in result
    print(f"  [PASS] mla journal: {result[:80]}...")


def test_mla_book():
    fmt = MLAFormat()
    ref = make_book_ref()
    result = fmt.format(ref)
    assert 'Box, George' in result
    assert '2015' in result
    print(f"  [PASS] mla book: {result[:80]}...")


def test_harvard_journal():
    fmt = HarvardFormat()
    ref = make_journal_ref()
    result = fmt.format(ref)
    assert 'Wang, Y.' in result
    assert '2024' in result
    assert 'Neural Information' in result or 'Advances' in result
    print(f"  [PASS] harvard journal: {result[:80]}...")


def test_harvard_book():
    fmt = HarvardFormat()
    ref = make_book_ref()
    result = fmt.format(ref)
    assert 'Box, G.' in result
    assert '2015' in result
    print(f"  [PASS] harvard book: {result[:80]}...")


if __name__ == '__main__':
    print("=== New Format Tests ===")
    test_chicago_journal()
    test_chicago_book()
    test_mla_journal()
    test_mla_book()
    test_harvard_journal()
    test_harvard_book()
    print("\nAll new format tests passed!")
