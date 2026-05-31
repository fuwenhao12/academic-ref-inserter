import subprocess
import tempfile
import os
import re
from pathlib import Path
from lxml import etree

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def latex_to_omml(latex_str: str, display: bool = False) -> str:
    steps = []
    steps.append(("input", latex_str))

    if not HAS_LATEX2MATHML:
        mathml = _fallback_latex_to_mathml(latex_str)
    else:
        mathml = latex2mathml.converter.convert(latex_str)
    steps.append(("mathml", mathml))

    omml = _mathml_to_omml(mathml)
    steps.append(("omml", omml))

    return omml


def _fallback_latex_to_mathml(latex_str: str) -> str:
    patterns = [
        (r'\\frac\{([^}]*)\}\{([^}]*)\}', r'<m:f><m:num>\1</m:num><m:den>\2</m:den></m:f>'),
        (r'\^\{([^}]*)\}', r'<m:sup>\1</m:sup>'),
        (r'_\{([^}]*)\}', r'<m:sub>\1</m:sub>'),
        (r'\^([a-zA-Z0-9])', r'<m:sup>\1</m:sup>'),
        (r'_([a-zA-Z0-9])', r'<m:sub>\1</m:sub>'),
        (r'\\sum', r'<m:sum/>'),
        (r'\\int', r'<m:int/>'),
        (r'\\pi', r'<m:pi/>'),
        (r'\\alpha', r'<m:alpha/>'),
        (r'\\beta', r'<m:beta/>'),
        (r'\\sigma', r'<m:sigma/>'),
        (r'\\mu', r'<m:mu/>'),
        (r'\\theta', r'<m:theta/>'),
        (r'\\lambda', r'<m:lambda/>'),
        (r'\\infty', r'<m:infin/>'),
    ]
    result = latex_str
    for pattern, replacement in patterns:
        result = re.sub(pattern, replacement, result)
    return f"<math>{result}</math>"


def _mathml_to_omml(mathml: str) -> str:
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mathml_file = Path(tmpdir) / "math.html"
            mathml_file.write_text(
                f"<html><body>{mathml}</body></html>", encoding="utf-8"
            )
            output_file = Path(tmpdir) / "output.docx"

            result = subprocess.run(
                ["pandoc", str(mathml_file), "-o", str(output_file)],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0 and output_file.exists():
                import zipfile
                with zipfile.ZipFile(output_file, 'r') as zf:
                    if 'word/document.xml' in zf.namelist():
                        doc_xml = zf.read('word/document.xml').decode('utf-8')
                        omml_match = re.search(
                            r'<m:oMath[^>]*>.*?</m:oMath>', doc_xml, re.DOTALL
                        )
                        if omml_match:
                            return omml_match.group(0)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return _build_omml_standalone(mathml)


def _build_omml_standalone(mathml: str) -> str:
    m = "http://schemas.openxmlformats.org/officeDocument/2006/math"
    w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    omml_parts = []
    content = re.sub(r'</?math[^>]*>', '', mathml)
    content = re.sub(r'<m:', '<', content)
    content = re.sub(r'</m:', '</', content)

    omml_parts.append(f'<m:oMathPara xmlns:m="{m}" xmlns:w="{w}">')
    omml_parts.append(f'<m:oMath>')
    omml_parts.append(f'<m:r><m:t xml:space="preserve">{content}</m:t></m:r>')
    omml_parts.append(f'</m:oMath>')
    omml_parts.append(f'</m:oMathPara>')

    return "".join(omml_parts)


def omml_to_latex(omml_xml: str) -> str:
    if not omml_xml:
        return ""
    text_parts = []
    for match in re.finditer(r'<m:t[^>]*>(.*?)</m:t>', omml_xml, re.DOTALL):
        text_parts.append(match.group(1).strip())
    return "".join(text_parts)


def detect_equations_in_docx(doc):
    equations = []
    for i, para in enumerate(doc.paragraphs):
        omml = para._element.findall(f'.//{{{M_NS}}}oMath')
        if not omml:
            omml = para._element.findall(f'.//{{{M_NS}}}oMathPara')
        if omml:
            omml_xml = "".join(
                [etree.tostring(elem, encoding='unicode') for elem in omml]
            )
            latex = omml_to_latex(omml_xml)
            is_display = para._element.findall(f'.//{{{M_NS}}}oMathPara') or \
                         len(omml) > 1
            equations.append({
                "index": len(equations) + 1,
                "paragraph_index": i,
                "is_display": bool(is_display),
                "latex": latex,
                "omml_xml": omml_xml,
                "paragraph": para,
            })
    return equations
