"""Tests for validator and docx_utils modules."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from utils.validator import (
    check_type_tag, check_year_valid, check_citation_coverage,
    check_sequential, check_duplicates, check_recency, validate_all
)
from utils.docx_utils import _parse_citation_range


def test_check_type_tag():
    assert check_type_tag("[1] Wang Y, et al. TimeXer...[J]. NeurIPS, 2024.")
    assert check_type_tag("[2] Box G E. Time series analysis[M]. Wiley, 2015.")
    assert check_type_tag("[3] Zeng A. Are transformers effective?[C]//AAAI, 2023.")
    assert check_type_tag("[4] ... [EB/OL]. https://example.com")
    assert not check_type_tag("[5] Wang Y. TimeXer. NeurIPS, 2024.")
    print("  [PASS] check_type_tag")


def test_check_year_valid():
    assert check_year_valid("2024")
    assert check_year_valid("1990")
    assert check_year_valid("2026")
    assert not check_year_valid("1899")
    assert not check_year_valid("")
    assert not check_year_valid(None)
    assert not check_year_valid("abcd")
    print("  [PASS] check_year_valid")


def test_check_citation_coverage():
    cited = {1, 2, 3, 5}
    refs = {1, 2, 3, 4, 5}
    result = check_citation_coverage(cited, refs)
    assert result['orphan'] == [4]
    assert result['missing'] == []
    assert not result['ok']

    cited2 = {1, 2, 3}
    refs2 = {1, 2}
    result2 = check_citation_coverage(cited2, refs2)
    assert result2['missing'] == [3]
    assert not result2['ok']

    cited3 = {1, 2, 3}
    refs3 = {1, 2, 3}
    result3 = check_citation_coverage(cited3, refs3)
    assert result3['ok']
    print("  [PASS] check_citation_coverage")


def test_check_sequential():
    assert check_sequential([1, 2, 3, 4, 5]) == []
    issues = check_sequential([1, 2, 4, 5])
    assert len(issues) > 0
    assert "not sequential" in issues[0].lower()
    print("  [PASS] check_sequential")


def test_check_duplicates():
    refs = [
        "Wang Y. TimeXer[J]. NeurIPS, 2024.",
        "Liu Y. iTransformer[J]. arXiv, 2023.",
        "Wang Y. TimeXer[J]. NeurIPS, 2024.",
    ]
    dups = check_duplicates(refs)
    assert len(dups) >= 1
    print("  [PASS] check_duplicates")


def test_check_recency():
    refs = ["ref1", "ref2", "ref3", "ref4"]
    years = ["2024", "2023", "2022", "2019"]
    result = check_recency(refs, years, threshold=5)
    assert result['ok']  # 3/4 >= 50%
    assert result['recent_count'] == 3

    years2 = ["2019", "2018", "2017", "2016"]
    result2 = check_recency(refs, years2, threshold=5)
    assert not result2['ok']  # 0/4 < 50%
    print("  [PASS] check_recency")


def test_validate_all_comprehensive():
    ref_texts = [
        "Wang Y. TimeXer[J]. NeurIPS, 2024, 37: 469-498.",
        "Liu Y. iTransformer[J]. arXiv, 2023.",
        "Box G E. Time series analysis[M]. Wiley, 2015.",
    ]
    cited = {1, 2, 3}
    ref_nums = {1, 2, 3}
    years = ["2024", "2023", "2015"]

    report = validate_all(ref_texts, cited, ref_nums, years, style='gbt7714')
    assert 'passed' in report
    assert report['total_refs'] == 3
    print(f"  [PASS] validate_all: passed={report['passed']}, issues={len(report['issues'])}")


def test_parse_citation_range():
    assert _parse_citation_range("1") == [1]
    assert _parse_citation_range("1-3") == [1, 2, 3]
    assert _parse_citation_range("1,3,5") == [1, 3, 5]
    assert _parse_citation_range("1-3,5,7-9") == [1, 2, 3, 5, 7, 8, 9]
    assert _parse_citation_range("10-12") == [10, 11, 12]
    assert _parse_citation_range("") == []
    print("  [PASS] parse_citation_range: 1, 1-3, 1,3,5, 1-3,5,7-9")


if __name__ == '__main__':
    print("=== Validator Tests ===")
    test_check_type_tag()
    test_check_year_valid()
    test_check_citation_coverage()
    test_check_sequential()
    test_check_duplicates()
    test_check_recency()
    test_validate_all_comprehensive()
    print("\n=== Range Citation Tests ===")
    test_parse_citation_range()
    print("\nAll tests passed!")
