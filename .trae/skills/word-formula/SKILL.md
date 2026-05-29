---
name: "word-formula"
description: "Inspect, extract, validate, and fix Word equation formulas (OMML/MathML). Invoke when user needs to check Word formula layout, convert LaTeX to Word equations, or batch-validate formula numbering in docx files."
---

# Word Formula Manager Skill

This skill handles Word formula/equation operations — inspecting OMML (Office Math Markup Language), validating layout, extracting formulas for review, and converting between LaTeX and Word equation format.

## Prerequisites

```bash
py -m pip install python-docx lxml
```

## Formula Storage in Word

Word equations are stored in `.docx` as **OMML** (Office Math Markup Language) inside `<m:oMath>` elements within paragraph runs. Key facts:

- **Namespace**: `http://schemas.openxmlformats.org/officeDocument/2006/math`
- **Container**: `<m:oMath>` (inline) or `<m:oMathPara>` (display/block)
- **Text representation**: `<m:t>` elements contain formula text
- **Font**: Cambria Math is the default equation font; size 10.5pt (5号) for Chinese journals

## Core Capabilities

### 1. Extract All Formulas from a Word Document

```python
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from lxml import etree

MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

doc = Document("paper.docx")

print("=" * 60)
print("Word 公式提取报告")
print("=" * 60)

formula_count = 0
for pi, para in enumerate(doc.paragraphs):
    # Search for oMath elements
    math_elements = para._element.findall(f'{{{MATH_NS}}}oMath')
    
    if math_elements:
        print(f"\n[P{pi}] 发现 {len(math_elements)} 个公式:")
        
        for mi, math in enumerate(math_elements):
            # Extract all <m:t> text
            texts = math.findall(f'.//{{{MATH_NS}}}t')
            formula_text = ''.join(t.text or '' for t in texts)
            print(f"  公式{mi+1}: {formula_text[:120]}")
            formula_count += 1
    
    # Also check for oMathPara
    math_paras = para._element.findall(f'{{{MATH_NS}}}oMathPara')
    if math_paras:
        print(f"\n[P{pi}] 发现 {len(math_paras)} 个显示公式:")
        for mi, mp in enumerate(math_paras):
            texts = mp.findall(f'.//{{{MATH_NS}}}t')
            formula_text = ''.join(t.text or '' for t in texts)
            print(f"  显示公式{mi+1}: {formula_text[:120]}")
            formula_count += 1

print(f"\n总计: {formula_count} 个公式")
```

### 2. Validate Formula Numbering

Check if formula numbers are sequential and correctly mapped:

```python
import re

def validate_formula_numbering(doc):
    """Check formula numbering consistency in text references"""
    numbers_in_text = []
    
    for para in doc.paragraphs:
        # Find "式(N)" or "公式(N)" or "式(N)" references
        refs = re.findall(r'式[（(](\d+)[）)]', para.text)
        numbers_in_text.extend(int(n) for n in refs)
    
    # Find actual formula labels in math elements
    numbers_in_formulas = []
    for para in doc.paragraphs:
        math_elements = para._element.findall(f'{{{MATH_NS}}}oMath')
        # Check for equation numbers nearby
    
    print(f"文中引用公式: {sorted(set(numbers_in_text))}")
    # Report gaps, duplicates, or out-of-order refs
```

### 3. Check Formula Layout Issues

Common layout problems to detect:

| Issue | Detection | Fix |
|-------|-----------|-----|
| Broken fraction lines | `<m:f>` without proper `<m:bar>` | Check OMML structure |
| Missing subscript/superscript | Check `<m:sSub>` / `<m:sSup>` | Rebuild in Word editor |
| Font inconsistency | Non-Cambria-Math in `<m:rPr>` | Apply Cambria Math |
| Overflow (formula too wide) | Measure `m:argSz` | Split into multi-line |
| Chinese text inside formula | Chinese chars in `<m:t>` | Use `\text{}` or separate run |

### 4. Extract Formula Text for Manual Review

Generate a readable report listing all formulas with context:

```python
def generate_formula_report(doc):
    """Generate a report of all formulas with surrounding text"""
    report = []
    
    for pi, para in enumerate(doc.paragraphs):
        math_elements = para._element.findall(f'{{{MATH_NS}}}oMath')
        math_paras = para._element.findall(f'{{{MATH_NS}}}oMathPara')
        
        if math_elements or math_paras:
            all_math = list(math_elements) + list(math_paras)
            for mi, math in enumerate(all_math):
                texts = math.findall(f'.//{{{MATH_NS}}}t')
                formula_text = ''.join(t.text or '' for t in texts)
                
                # Get surrounding context (±200 chars)
                context = para.text[:200] if para.text else "(无上下文)"
                
                report.append({
                    'paragraph': pi,
                    'index': mi,
                    'context': context,
                    'formula': formula_text
                })
    
    return report
```

### 5. Known OMML Fragments & Their LaTeX Equivalents

For cross-referencing between Word and LaTeX:

| OMML Element | Meaning | LaTeX |
|-------------|---------|-------|
| `<m:f>` | Fraction | `\frac{}{}` |
| `<m:sSup>` | Superscript | `^{}` |
| `<m:sSub>` | Subscript | `_{}` |
| `<m:sSubSup>` | Both sub/sup | `_{}^{}` |
| `<m:rad>` | Square root | `\sqrt{}` |
| `<m:deg>` | Root degree | `\sqrt[n]{}` |
| `<m:nary>` | Sum/Product/Integral | `\sum` `\prod` `\int` |
| `<m:limLow>` | Lower limit | `_{n=1}` |
| `<m:limUpp>` | Upper limit | `^{N}` |
| `<m:acc>` | Accent (hat/bar/dot) | `\hat{}` `\bar{}` |
| `<m:bar>` | Overbar | `\overline{}` |
| `<m:d>` | Delimiter (parentheses) | `()` `[]` `\{\}` |
| `<m:eqArr>` | Equation array | `\begin{aligned}` |
| `<m:m>` | Matrix | `\begin{matrix}` |
| `<m:groupChr>` | Grouped character | `\underbrace{}` `\overbrace{}` |

### 6. Key Formulas to Check for This Paper

Based on your LaTeX source, priority check items:

| Formula | Location | OMML Check |
|---------|----------|------------|
| **SAL Loss** (Eq 1) | Section 3.4 | Check double summation, subscript alignment |
| **Time Gate** | Section 3.2.1 | Check sigmoid `σ(w_t)`, bold vectors |
| **Variable Gate** | Section 3.2.2 | Check MLP concatenation, GELU |
| **Fusion output** | Section 3.2.3 | Check Hadamard product `⊙` |
| **y_D, y_T definition** | Section 3.2.1 | Check `ℝ^{B×L×D}` notation |

## Batch Validation Script

```python
# -*- coding: utf-8 -*-
"""Batch validate all formulas in a submission Word document"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from docx import Document
from lxml import etree

MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def check_formulas(doc_path):
    doc = Document(doc_path)
    issues = []
    
    for pi, para in enumerate(doc.paragraphs):
        math_elements = para._element.findall(f'{{{MATH_NS}}}oMath')
        math_paras = para._element.findall(f'{{{MATH_NS}}}oMathPara')
        all_math = list(math_elements) + list(math_paras)
        
        for mi, math in enumerate(all_math):
            texts = math.findall(f'.//{{{MATH_NS}}}t')
            formula_text = ''.join(t.text or '' for t in texts)
            
            # Check 1: Empty formula
            if not formula_text.strip():
                issues.append(f"⚠️ P{pi} 公式{mi+1}: 空公式 (可能损坏)")
            
            # Check 2: Broken fraction (missing numerator/denominator)
            fracs = math.findall(f'{{{MATH_NS}}}f')
            for fi, f in enumerate(fracs):
                num = f.find(f'{{{MATH_NS}}}num')
                den = f.find(f'{{{MATH_NS}}}den')
                if num is None or den is None:
                    issues.append(f"⚠️ P{pi} 公式{mi+1} 分数{fi+1}: 缺分子/分母")
                elif len(num) == 0 or len(den) == 0:
                    issues.append(f"⚠️ P{pi} 公式{mi+1} 分数{fi+1}: 分子/分母为空")
    
    return issues

# Usage
issues = check_formulas("paper.docx")
if issues:
    print("公式问题报告:")
    for issue in issues:
        print(f"  {issue}")
else:
    print("✅ 未发现明显公式问题")
```

## Common Pattern: Insert a New Formula

```python
from docx import Document
from docx.oxml.ns import qn
from lxml import etree

doc = Document("paper.docx")

# To insert a formula, you typically need to:
# 1. Create an oMath element with proper structure
# 2. Insert it into a paragraph run
# 
# Simplified: Use Word's built-in formula editor to create formulas,
# then use python-docx only for inspection and validation.

# For programmatic insertion, work with the OMML XML directly:
MATH_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

def create_simple_formula(latex_style_text):
    """Create a minimal oMath element (for simple formulas only)"""
    # Complex formulas should be created in Word editor
    omath = etree.Element(f'{{{MATH_NS}}}oMath')
    r = etree.SubElement(omath, f'{{{MATH_NS}}}r')
    t = etree.SubElement(r, f'{{{MATH_NS}}}t')
    t.text = latex_style_text
    return omath
```

## When to Use This Skill

- User says "检查公式" / "Check formulas"
- User says "公式排版对不对" / "Is formula layout correct?"
- User says "提取 Word 中的公式" / "Extract formulas from Word"
- User says "对比 LaTeX 和 Word 公式" / "Compare LaTeX and Word formulas"
- Before journal submission — check critical formulas (SAL loss, gates)
