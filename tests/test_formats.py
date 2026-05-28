"""Tests for all citation format implementations."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from formats.gbt7714 import GBT7714Format
from formats.ieee import IEEEFormat
from formats.apa7 import APA7Format
from utils.parser import parse_ref, detect_type


def test_gbt7714_journal():
    fmt = GBT7714Format()
    ref = {
        'authors': ['Wang Y', 'Wu H', 'Dong J'],
        'title': 'TimeXer: Empowering transformers for time series forecasting with exogenous variables',
        'journal': 'Advances in Neural Information Processing Systems',
        'year': '2024',
        'volume': '37',
        'issue': '',
        'pages': '469-498',
        'type': 'j',
    }
    result = fmt.format(ref)
    assert '[J]' in result, f"Missing [J] tag: {result[:80]}"
    assert 'Wang Y' in result, f"Missing authors: {result[:80]}"
    assert '2024' in result, f"Missing year: {result[:80]}"
    assert result.endswith('.'), f"Should end with period"
    print(f"  [PASS] gbt7714 journal: {result[:80]}...")


def test_gbt7714_book():
    fmt = GBT7714Format()
    ref = {
        'authors': ['Box G E', 'Jenkins G M', 'Reinsel G C'],
        'title': 'Time series analysis: forecasting and control',
        'publisher': 'John Wiley & Sons',
        'year': '2015',
        'type': 'm',
    }
    result = fmt.format(ref)
    assert '[M]' in result, f"Missing [M] tag"
    assert 'Box G E' in result
    print(f"  [PASS] gbt7714 book: {result[:80]}...")


def test_gbt7714_chinese_authors():
    fmt = GBT7714Format()
    ref = {
        'authors': ['刘云', '胡涛', '张华'],
        'title': '基于深度学习的空气质量预测综述',
        'journal': '计算机工程与应用',
        'year': '2024',
        'volume': '60',
        'issue': '2',
        'pages': '1-15',
        'type': 'j',
    }
    result = fmt.format(ref)
    assert '刘云' in result, f"Chinese author lost: {result[:80]}"
    assert '[J]' in result
    print(f"  [PASS] gbt7714 Chinese: {result[:80]}...")


def test_ieee_journal():
    fmt = IEEEFormat()
    ref = {
        'authors': ['Yun Wang', 'Haixu Wu', 'Jie Dong'],
        'title': 'TimeXer: Empowering transformers for time series forecasting',
        'journal': 'Advances in Neural Information Processing Systems',
        'volume': '37',
        'pages': '469-498',
        'year': '2024',
        'type': 'j',
    }
    result = fmt.format(ref)
    assert 'Y. Wang' in result, f"IEEE name format wrong: {result[:80]}"
    assert 'vol. 37' in result, f"Missing vol.: {result[:80]}"
    print(f"  [PASS] ieee journal: {result[:80]}...")


def test_apa_journal():
    fmt = APA7Format()
    ref = {
        'authors': ['Yun Wang', 'Haixu Wu', 'Jie Dong'],
        'title': 'TimeXer: Empowering transformers for time series forecasting',
        'journal': 'Advances in Neural Information Processing Systems',
        'volume': '37',
        'pages': '469-498',
        'year': '2024',
        'doi': '10.1234/example',
        'type': 'j',
    }
    result = fmt.format(ref)
    assert 'Wang, Y.' in result, f"APA name format wrong: {result[:80]}"
    assert '2024' in result
    assert 'doi' in result.lower()
    print(f"  [PASS] apa journal: {result[:80]}...")


def test_parse_ref():
    raw = "[1] Wang Y, Wu H, Dong J, et al. TimeXer: Empowering transformers[J]. NeurIPS, 2024, 37: 469-498."
    parsed = parse_ref(raw)
    assert parsed['type'] == 'journal'
    assert parsed['year'] == '2024'
    assert len(parsed['authors']) > 0
    print(f"  [PASS] parse_ref: type={parsed['type']}, year={parsed['year']}")


def test_detect_type():
    tests = [
        ("[1] ... [J]. Journal, 2024", "journal"),
        ("[2] ... [C]//Proceedings", "conference"),
        ("[3] ... [M]. Publisher, 2020", "book"),
        ("[4] ... [D]. University, 2022", "dissertation"),
        ("[5] ... [P]. Patent No.", "patent"),
        ("[6] ... [S]. ISO 9001", "standard"),
        ("[7] ... [EB/OL]. URL", "electronic"),
    ]
    for text, expected in tests:
        detected = detect_type(text)
        assert detected == expected, f"Expected {expected}, got {detected}: {text[:50]}"
    print(f"  [PASS] detect_type: all 7 types correct")


if __name__ == '__main__':
    print("=== Format Tests ===")
    test_gbt7714_journal()
    test_gbt7714_book()
    test_gbt7714_chinese_authors()
    test_ieee_journal()
    test_apa_journal()
    print("\n=== Parser Tests ===")
    test_parse_ref()
    test_detect_type()
    print("\nAll tests passed!")
