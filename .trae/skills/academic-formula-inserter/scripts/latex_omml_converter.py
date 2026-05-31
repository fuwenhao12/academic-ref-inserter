"""LaTeX ↔ OMML (Office Math Markup Language) converter.

Uses latex2mathml for LaTeX→MathML conversion, then transforms the MathML
DOM tree into proper OMML XML that Word can render as native equations.
"""

import re
from lxml import etree

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
MML_NS = "http://www.w3.org/1998/Math/MathML"

# Greek letter mapping
GREEK = {
    "α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta",
    "ε": "epsiv", "ζ": "zeta", "η": "eta", "θ": "theta",
    "ι": "iota", "κ": "kappa", "λ": "lambda", "μ": "mu",
    "ν": "nu", "ξ": "xi", "ο": "omicron", "π": "pi",
    "ρ": "rho", "σ": "sigma", "τ": "tau", "υ": "upsi",
    "φ": "phi", "χ": "chi", "ψ": "psi", "ω": "omega",
    "Γ": "Gamma", "Δ": "Delta", "Θ": "Theta", "Λ": "Lambda",
    "Ξ": "Xi", "Π": "Pi", "Σ": "Sigma", "Φ": "Phi",
    "Ψ": "Psi", "Ω": "omega",
}


def latex_to_omml(latex_str: str, display: bool = False) -> str:
    if not HAS_LATEX2MATHML:
        return _build_text_omml(latex_str)

    mathml = latex2mathml.converter.convert(latex_str)
    mathml = mathml.strip()
    if not mathml.startswith("<"):
        mathml = f"<math>{mathml}</math>"

    try:
        mathml_root = etree.fromstring(mathml.encode("utf-8"))
    except etree.XMLSyntaxError:
        return _build_text_omml(latex_str)

    omml_inner = _convert_mathml_node(mathml_root)

    if display:
        return (
            f'<m:oMathPara xmlns:m="{M_NS}">'
            f'<m:oMath>{omml_inner}</m:oMath>'
            f'</m:oMathPara>'
        )
    else:
        return f'<m:oMath xmlns:m="{M_NS}">{omml_inner}</m:oMath>'


def _build_text_omml(latex_str: str) -> str:
    m = M_NS
    return (
        f'<m:oMath xmlns:m="{m}">'
        f'<m:r><m:rPr><m:sty m:val="p"/></m:rPr>'
        f'<m:t>{_escape_xml(latex_str)}</m:t></m:r>'
        f'</m:oMath>'
    )


def _escape_xml(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def _m(tag: str, content: str = "") -> str:
    return f"<{tag}>{content}</{tag.split()[0]}>" if content else f"<{tag}/>"


def _r(text: str, italic: bool = False) -> str:
    """Build an OMML run matching Word's native format."""
    if italic:
        return (
            f'<m:r><m:rPr><m:ital/></m:rPr>'
            f'<m:t>{_escape_xml(text)}</m:t></m:r>'
        )
    else:
        return (
            f'<m:r><m:rPr/>'
            f'<m:t>{_escape_xml(text)}</m:t></m:r>'
        )


def _build_omml_text(text: str) -> str:
    """Build OMML for simple text, splitting operators from identifiers."""
    parts = []
    buf = ""
    for ch in text:
        if ch in "+-*/=()[]<>±×÷∑∏∫∂∇√∞∝∧∨∩∪∈∉⊂⊃⊆⊇":
            if buf:
                parts.append(_r(buf))
                buf = ""
            parts.append(_r(ch))
        else:
            buf += ch
    if buf:
        parts.append(_r(buf))
    return "".join(parts)


def _convert_mathml_node(node) -> str:
    """Recursively convert a MathML node to OMML XML string."""
    tag = node.tag
    local = tag.split("}")[-1] if "}" in tag else tag

    children_text = "".join(_convert_mathml_node(c) for c in node)

    text = (node.text or "").strip()
    tail = (node.tail or "").strip()

    result = ""

    if local == "math":
        result = children_text + (_build_omml_text(text) if text else "")

    elif local == "mrow":
        result = children_text + (_build_omml_text(text) if text else "")

    elif local == "mi":
        content = text or ""
        if content in GREEK:
            result = _r(content)
        elif len(content) <= 1:
            result = _r(content, italic=True)
        elif content in ("sin", "cos", "tan", "log", "ln", "exp",
                          "sinh", "cosh", "tanh", "arcsin", "arccos", "arctan",
                          "max", "min", "lim", "det", "arg", "deg"):
            result = _r(content)
        elif content in ("MLP", "MSE", "MAE", "LSTM", "GRU", "RNN",
                          "CNN", "ReLU"):
            result = _r(content)
        else:
            result = _r(content)

    elif local == "mn":
        result = _r(text)

    elif local == "mo":
        result = _r(text)

    elif local == "mtext":
        result = _r(text)

    elif local == "msup":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        sup = parts[1] if len(parts) > 1 else ""
        result = f'<m:sSup><m:e>{base}</m:e><m:lim>{sup}</m:lim></m:sSup>'

    elif local == "msub":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        sub = parts[1] if len(parts) > 1 else ""
        result = f'<m:sSub><m:e>{base}</m:e><m:lim>{sub}</m:lim></m:sSub>'

    elif local == "msubsup":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        sub = parts[1] if len(parts) > 1 else ""
        sup = parts[2] if len(parts) > 2 else ""
        result = (
            f'<m:sSubSup>'
            f'<m:e>{base}</m:e>'
            f'<m:sub>{sub}</m:sub>'
            f'<m:sup>{sup}</m:sup>'
            f'</m:sSubSup>'
        )

    elif local == "mfrac":
        parts = _split_children(node)
        num = parts[0] if parts else ""
        den = parts[1] if len(parts) > 1 else ""
        result = f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'

    elif local == "msqrt":
        content = "".join(_convert_mathml_node(c) for c in node)
        result = (
            f'<m:rad>'
            f'<m:radPr><m:degHide m:val="on"/></m:radPr>'
            f'<m:e>{content}</m:e>'
            f'</m:rad>'
        )

    elif local == "mroot":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        deg = parts[1] if len(parts) > 1 else ""
        result = (
            f'<m:rad>'
            f'<m:radPr><m:degHide m:val="off"/></m:radPr>'
            f'<m:deg>{deg}</m:deg>'
            f'<m:e>{base}</m:e>'
            f'</m:rad>'
        )

    elif local == "mover":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        over = parts[1] if len(parts) > 1 else ""
        over_text = "".join(node[1].itertext()) if len(node) > 1 else ""
        if over_text == "\u203e" or over_text == "_":
            result = f'<m:bar><m:barPr><m:pos m:val="top"/></m:barPr><m:e>{base}</m:e></m:bar>'
        elif over_text == "\u02c7":
            result = f'<m:bar><m:barPr><m:pos m:val="top"/></m:barPr><m:e>{base}</m:e></m:bar>'
        else:
            result = base  # fallback, just show base

    elif local == "munder":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        under = parts[1] if len(parts) > 1 else ""
        under_text = "".join(node[1].itertext()) if len(node) > 1 else ""
        if under_text in ("lim", "max", "min", "sup", "inf"):
            result = (
                f'<m:limLow><m:e>{base}</m:e><m:lim>{under}</m:lim></m:limLow>'
            )
        else:
            result = f'<m:sSub><m:e>{base}</m:e><m:lim>{under}</m:lim></m:sSub>'

    elif local == "munderover":
        parts = _split_children(node)
        base = parts[0] if parts else ""
        under = parts[1] if len(parts) > 1 else ""
        over = parts[2] if len(parts) > 2 else ""
        result = (
            f'<m:limLow>'
            f'<m:limLow><m:e>{base}</m:e><m:lim>{under}</m:lim></m:limLow>'
            f'<m:lim>{over}</m:lim>'
            f'</m:limLow>'
        )

    elif local == "mfenced":
        open_delim = node.get("open", "(")
        close_delim = node.get("close", ")")
        parts = _split_children(node)
        inner = "".join(parts)
        result = (
            f'<m:d><m:dPr><m:begChr m:val="{open_delim}"/>'
            f'<m:endChr m:val="{close_delim}"/></m:dPr>'
            f'<m:e>{inner}</m:e></m:d>'
        )

    elif local == "mstyle":
        result = children_text + (_build_omml_text(text) if text else "")

    elif local in ("merror", "mphantom", "mpadded", "menclose"):
        result = children_text + (_build_omml_text(text) if text else "")

    else:
        result = children_text + (_build_omml_text(text) if text else "")

    if tail:
        result += _build_omml_text(tail)

    return result


def _split_children(node):
    """Convert each child element of a MathML node to OMML."""
    results = []
    for child in node:
        results.append(_convert_mathml_node(child))
    return results


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
            is_display = bool(para._element.findall(f'.//{{{M_NS}}}oMathPara'))
            equations.append({
                "index": len(equations) + 1,
                "paragraph_index": i,
                "is_display": is_display,
                "latex": latex,
                "omml_xml": omml_xml,
                "paragraph": para,
            })
    return equations
