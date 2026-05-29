---
name: "reference-manager"
description: "Manage academic references in GB/T 7714-2015 format. Invoke when user needs to format, validate, reorder, or batch-process Chinese/English references for journal submission."
---

# Reference Manager Skill (GB/T 7714-2015)

This skill manages academic references for Chinese journal submission, specifically following **GB/T 7714-2015** (sequential numbering system, 顺序编码制).

## Reference Format Rules (GB/T 7714-2015)

### Journal Article [J]
```
[序号] 作者. 题名[J]. 刊名, 出版年, 卷(期): 起止页码.
```
Example:
```
[1] Wang Y, Wu H, Dong J, et al. TimeXer: Empowering transformers for time series forecasting with exogenous variables[J]. Advances in Neural Information Processing Systems, 2024, 37: 469-498.
```

### Conference Paper [C]
```
[序号] 作者. 题名[C]//会议录名称. 出版地: 出版者, 出版年: 起止页码.
```
Example:
```
[2] Zeng A, Chen M, Zhang L, et al. Are transformers effective for time series forecasting?[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2023: 11121-11128.
```

### Book [M]
```
[序号] 作者. 书名[M]. 出版地: 出版者, 出版年.
```
Example:
```
[3] Box G E, Jenkins G M, Reinsel G C, et al. Time series analysis: forecasting and control[M]. John Wiley & Sons, 2015.
```

### Preprint / arXiv [J]
```
[序号] 作者. 题名[J]. arXiv preprint arXiv:xxxx, 出版年.
```
Example:
```
[4] Liu Y, Hu T, Zhang H, et al. iTransformer: Inverted transformers are effective for time series forecasting[J]. arXiv preprint arXiv:2310.06625, 2023.
```

## Validation Checklist

For each reference, verify:
1. ✅ **Sequential numbering** [1], [2], [3]... matching citation order in text
2. ✅ **Author format**: Lastname FirstInitial., (e.g., "Wang Y, Wu H,")
3. ✅ **Title** in original language, no quotes
4. ✅ **Journal name** in full (not abbreviated) for Chinese journals
5. ✅ **Year, Volume(Issue): Pages** format
6. ✅ **[J]** for journals, **[C]** for conferences, **[M]** for books
7. ✅ **No DOI** required in GB/T 7714-2015 (but can be added)

## Common Issues & Fixes

### Issue 1: Author names reversed
❌ `Yun Wang, Haixu Wu`  
✅ `Wang Y, Wu H`

### Issue 2: Missing document type tag
❌ `... transformers for time series forecasting. Advances in...`  
✅ `... transformers for time series forecasting[J]. Advances in...`

### Issue 3: Conference paper format wrong
❌ `...forecasting? In: Proceedings of AAAI, 2023`  
✅ `...forecasting?[C]//Proceedings of the AAAI Conference on Artificial Intelligence. 2023: 11121-11128.`

### Issue 4: Chinese author names
Chinese authors: Keep in original Chinese (e.g., `刘云`), not translated.
English papers by Chinese authors: Use `Liu Y, Hu T,` format.

## Batch Processing Script

```python
# -*- coding: utf-8 -*-
"""Validate and renumber GB/T 7714 references"""
import re

def parse_reference(ref_str):
    """Parse a single reference entry"""
    match = re.match(r'\[(\d+)\]\s+(.*)', ref_str.strip())
    if match:
        return int(match.group(1)), match.group(2)
    return None, ref_str

def check_ref_type(ref_text):
    """Check if reference has proper type tag"""
    types = ['[J]', '[C]', '[M]', '[D]', '[N]', '[S]', '[P]', '[EB/OL]']
    for t in types:
        if t in ref_text:
            return True
    return False

def renumber_references(refs):
    """Renumber references sequentially [1], [2], [3]..."""
    result = []
    for i, ref in enumerate(refs, 1):
        text = re.sub(r'^\[\d+\]', f'[{i}]', ref.strip())
        result.append(text)
    return result

# Usage example
refs = [
    "[3] Wang Y, et al. TimeXer...[J]. NeurIPS, 2024",
    "[1] Box G E, et al. Time series...[M]. Wiley, 2015",
]

# Detect problems
for ref in refs:
    if not check_ref_type(ref):
        print(f"⚠️ Missing type tag: {ref[:60]}...")

# Fix order
fixed = sorted(refs, key=lambda r: int(re.match(r'\[(\d+)\]', r).group(1)))
print("\n".join(fixed))
```

## 《计算机工程与应用》Specific Requirements

- **Minimum**: 15+ references for research papers
- **Recent**: ≥50% from last 5 years
- **Language**: Both Chinese and English allowed
- **Order**: Sequential numbering matching citation order in main text
- **Format**: GB/T 7714-2015 strict compliance
- **No DOI** required but encouraged

## Quick Reference: Type Tags

| Tag | Document Type |
|-----|--------------|
| [J] | Journal article |
| [C] | Conference paper |
| [M] | Monograph (book) |
| [D] | Dissertation |
| [N] | Newspaper |
| [S] | Standard |
| [P] | Patent |
| [EB/OL] | Electronic resource |

## When to Use This Skill

- User says "检查参考文献格式" / "Check reference format"
- User says "参考文献格式不对" / "Reference format is wrong"
- User says "按GB/T 7714排序参考文献" / "Sort references by GB/T 7714"
- User says "帮我检查引用" / "Help me check citations"
- Before journal submission — always validate references
