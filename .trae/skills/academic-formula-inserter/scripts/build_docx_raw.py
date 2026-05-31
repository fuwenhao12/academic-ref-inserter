"""Build a Word .docx from scratch at the raw XML level.

This completely bypasses python-docx to avoid any OMML corruption.
Creates a minimal but valid .docx with MathType-compatible formulas.
"""
import zipfile, io, os, re
from pathlib import Path
from lxml import etree

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W14_NS = "http://schemas.microsoft.com/office/word/2010/wordml"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"

# ─── helper: OMML builders (from latex_omml_converter) ───

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


def _tx(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _run(text, italic=False):
    if italic:
        return f'<m:r><m:rPr><m:ital/></m:rPr><m:t>{_tx(text)}</m:t></m:r>'
    else:
        return f'<m:r><m:rPr/><m:t>{_tx(text)}</m:t></m:r>'


def latex_to_omml_raw(latex):
    """Convert LaTeX to OMML without namespace prefix on oMath."""
    try:
        import latex2mathml.converter
        mathml = latex2mathml.converter.convert(latex)
        if not mathml.strip().startswith("<"):
            mathml = f"<math>{mathml}</math>"
        root = etree.fromstring(mathml.encode("utf-8"))
        inner = _convert_node(root)
    except Exception:
        inner = _build_text(latex)

    return f'<m:oMath>{inner}</m:oMath>'


def _build_text(s):
    parts = []
    buf = ""
    for ch in s:
        if ch in "+-*/=()[]<>±×÷∑∏∫∂∇√∞∝∧∨∩∪∈∉⊂⊃⊆⊇":
            if buf:
                parts.append(_run(buf))
                buf = ""
            parts.append(_run(ch))
        else:
            buf += ch
    if buf:
        parts.append(_run(buf))
    return "".join(parts)


def _convert_node(node):
    tag = node.tag
    local = tag.split("}")[-1] if "}" in tag else tag
    children = "".join(_convert_node(c) for c in node)
    text = (node.text or "").strip()
    tail = (node.tail or "").strip()
    result = ""

    if local in ("math", "mrow", "mstyle"):
        result = children + (_build_text(text) if text else "")
    elif local == "mi":
        content = text or ""
        if content in GREEK:
            result = _run(content)
        elif len(content) <= 1:
            result = _run(content, italic=True)
        elif content in ("sin", "cos", "tan", "log", "ln", "exp",
                         "sinh", "cosh", "tanh", "arcsin", "arccos", "arctan",
                         "max", "min", "lim", "det", "arg", "deg"):
            result = _run(content)
        else:
            result = _run(content)
    elif local == "mn":
        result = _run(text)
    elif local == "mo":
        result = _run(text)
    elif local == "mtext":
        result = _run(text)
    elif local == "msup":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if parts else ""
        sup = parts[1] if len(parts) > 1 else ""
        result = f'<m:sSup><m:e>{base}</m:e><m:lim>{sup}</m:lim></m:sSup>'
    elif local == "msub":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if parts else ""
        sub = parts[1] if len(parts) > 1 else ""
        result = f'<m:sSub><m:e>{base}</m:e><m:lim>{sub}</m:lim></m:sSub>'
    elif local == "msubsup":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if len(parts) > 0 else ""
        sub = parts[1] if len(parts) > 1 else ""
        sup = parts[2] if len(parts) > 2 else ""
        result = f'<m:sSubSup><m:e>{base}</m:e><m:sub>{sub}</m:sub><m:sup>{sup}</m:sup></m:sSubSup>'
    elif local == "mfrac":
        parts = [_convert_node(c) for c in node]
        num = parts[0] if len(parts) > 0 else ""
        den = parts[1] if len(parts) > 1 else ""
        result = f'<m:f><m:num>{num}</m:num><m:den>{den}</m:den></m:f>'
    elif local == "msqrt":
        content = "".join(_convert_node(c) for c in node)
        result = f'<m:rad><m:radPr><m:degHide m:val="on"/></m:radPr><m:e>{content}</m:e></m:rad>'
    elif local == "mroot":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if len(parts) > 0 else ""
        deg = parts[1] if len(parts) > 1 else ""
        result = f'<m:rad><m:radPr><m:degHide m:val="off"/></m:radPr><m:deg>{deg}</m:deg><m:e>{base}</m:e></m:rad>'
    elif local == "mover":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if len(parts) > 0 else ""
        result = base
    elif local == "munder":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if len(parts) > 0 else ""
        under = parts[1] if len(parts) > 1 else ""
        under_text = "".join(node[1].itertext()) if len(node) > 1 else ""
        if under_text in ("lim", "max", "min", "sup", "inf"):
            result = f'<m:limLow><m:e>{base}</m:e><m:lim>{under}</m:lim></m:limLow>'
        else:
            result = f'<m:sSub><m:e>{base}</m:e><m:lim>{under}</m:lim></m:sSub>'
    elif local == "munderover":
        parts = [_convert_node(c) for c in node]
        base = parts[0] if len(parts) > 0 else ""
        under = parts[1] if len(parts) > 1 else ""
        over = parts[2] if len(parts) > 2 else ""
        result = f'<m:limLow><m:limLow><m:e>{base}</m:e><m:lim>{under}</m:lim></m:limLow><m:lim>{over}</m:lim></m:limLow>'
    elif local == "mfenced":
        open_d = node.get("open", "(")
        close_d = node.get("close", ")")
        inner = "".join(_convert_node(c) for c in node)
        result = f'<m:d><m:dPr><m:begCh m:val="{open_d}"/><m:endCh m:val="{close_d}"/></m:dPr><m:e>{inner}</m:e></m:d>'
    else:
        result = children + (_build_text(text) if text else "")

    if tail:
        result += _build_text(tail)
    return result


# ─── XML templates ───

DOC_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
            xmlns:v="urn:schemas-microsoft-com:vml"
            xmlns:w10="urn:schemas-microsoft-com:office:word"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
            xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"
            xmlns:wpi="http://schemas.microsoft.com/office/word/2010/wordprocessingInk"
            xmlns:wne="http://schemas.microsoft.com/office/word/2006/wordml"
            xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape"
            mc:Ignorable="w14 w16cex w16cid w16 w16du w16sdtdh w16sdtfl">
<w:body>{body}</w:body></w:document>"""

STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
          xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
          xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
          xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
          mc:Ignorable="w14">
  <w:docDefaults>
    <w:rPrDefault><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr></w:rPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="a1">
    <w:name w:val="Normal"/>
    <w:rPr><w:lang w:eastAsia="zh-CN"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="MTDisplayEquation">
    <w:name w:val="MTDisplayEquation"/>
    <w:basedOn w:val="a1"/>
    <w:pPr>
      <w:tabs><w:tab w:val="center" w:pos="4820"/><w:tab w:val="right" w:pos="9640"/></w:tabs>
      <w:jc w:val="center"/>
    </w:pPr>
    <w:rPr><w:lang w:eastAsia="zh-CN"/></w:rPr>
  </w:style>
  <w:style w:type="character" w:default="1" w:styleId="a2">
    <w:name w:val="Default Paragraph Font"/>
  </w:style>
  <w:style w:type="character" w:customStyle="1" w:styleId="MTDisplayEquation0">
    <w:name w:val="MTDisplayEquation Char"/>
    <w:basedOn w:val="a2"/>
    <w:link w:val="MTDisplayEquation"/>
    <w:rPr><w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/><w:sz w:val="21"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="a1"/>
    <w:rPr><w:b/><w:sz w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="a1"/>
    <w:rPr><w:b/><w:sz w:val="28"/></w:rPr>
  </w:style>
</w:styles>"""

SETTINGS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
            mc:Ignorable="w14">
  <w:zoom w:percent="100"/>
  <w:defaultTabStop w:val="420"/>
</w:settings>"""

FONT_TABLE_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:font w:name="Times New Roman"><w:panose1 w:val="02020603050405020304"/><w:charset w:val="00"/><w:family w:val="roman"/></w:font>
  <w:font w:name="宋体"><w:panose1 w:val="02010600030101010101"/><w:charset w:val="86"/><w:family w:val="auto"/></w:font>
</w:fonts>"""

THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:theme xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:themeElements/></w:theme>"""

CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>"""

RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

DOC_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>
</Relationships>"""

CORE_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/">
  <dc:creator>Academic Formula Inserter</dc:creator>
</cp:coreProperties>"""

APP_PROPS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Academic Formula Inserter</Application>
</Properties>"""


def build_paragraph(text="", omml="", number=None, style="MTDisplayEquation"):
    """Build a paragraph XML string."""
    runs = ""
    if text:
        runs = f'<w:r><w:rPr><w:lang w:eastAsia="zh-CN"/></w:rPr><w:t xml:space="preserve">{_tx(text)}</w:t></w:r>'
    if omml:
        runs += omml
    if number is not None:
        runs += (f'<w:fldSimple w:instr=" SEQ MTEqn \\\\c \\\\* Arabic \\\\* MERGEFORMAT ">'
                 f'<w:r><w:rPr><w:noProof/></w:rPr>'
                 f'<w:t>({number})</w:t></w:r>'
                 f'</w:fldSimple>')
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>{runs}</w:p>'


def build_heading(text, level=1):
    style = f"Heading{level}"
    return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr><w:r><w:t>{_tx(text)}</w:t></w:r></w:p>'


def build_docx(formulas, output_path):
    """Build a complete docx from scratch.

    formulas: list of (label, latex) tuples
    """
    body_parts = []

    # Title
    body_parts.append(build_heading('学术公式插入演示 — MathType 原生格式', 1))
    body_parts.append(build_paragraph('以下公式使用 MathType 原生 OMML 格式，双击可在 MathType 或 Word 中编辑。'))
    body_parts.append(build_paragraph('已安装 MathType 时，打开公式即可在 MathType 中修改。'))

    # Regular paragraph for spacing
    body_parts.append('<w:p><w:r><w:br/></w:r></w:p>')

    for i, (label, latex) in enumerate(formulas):
        title = label.split('：')[0] if '：' in label else label
        body_parts.append(build_heading(title, 2))

        omml = latex_to_omml_raw(latex)
        # Formula in its own paragraph (no text run), matching recovered doc format
        body_parts.append(build_paragraph(text="", omml=omml, number=i + 1, style="MTDisplayEquation"))
        body_parts.append('<w:p><w:r><w:br/></w:r></w:p>')

    body_xml = "".join(body_parts)
    document_xml = DOC_TEMPLATE.replace("{body}", body_xml)

    # Build the ZIP package
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', CONTENT_TYPES_XML)
        zf.writestr('_rels/.rels', RELS_XML)
        zf.writestr('word/document.xml', document_xml.encode('utf-8'))
        zf.writestr('word/_rels/document.xml.rels', DOC_RELS_XML)
        zf.writestr('word/styles.xml', STYLES_XML)
        zf.writestr('word/settings.xml', SETTINGS_XML)
        zf.writestr('word/fontTable.xml', FONT_TABLE_XML)
        zf.writestr('word/theme/theme1.xml', THEME_XML)
        zf.writestr('docProps/core.xml', CORE_PROPS_XML)
        zf.writestr('docProps/app.xml', APP_PROPS_XML)

    with open(output_path, 'wb') as f:
        f.write(buffer.getvalue())

    return output_path


def verify_docx(path):
    """Verify the generated docx structure."""
    with zipfile.ZipFile(path, 'r') as zf:
        names = zf.namelist()
        doc_xml = zf.read('word/document.xml').decode('utf-8')

    # Check essential files exist
    required = ['[Content_Types].xml', '_rels/.rels', 'word/document.xml',
                'word/_rels/document.xml.rels', 'word/styles.xml']
    missing = [r for r in required if r not in names]
    if missing:
        return {"valid": False, "error": f"Missing files: {missing}"}

    # Check OMML
    omml_count = len(re.findall(r'<m:oMath[ >]', doc_xml))
    seq_count = doc_xml.count('SEQ MTEqn')
    mt_style = 'MTDisplayEquation' in doc_xml

    # Check for corruptions
    corrupt = {}
    for c in ['sSupPr', 'sSubPr', 'ctrlPr']:
        count = doc_xml.count(c)
        if count > 0:
            corrupt[c] = count

    return {
        "valid": True,
        "files": len(names),
        "omml": omml_count,
        "seq_mteqn": seq_count,
        "mt_style": mt_style,
        "corruptions": corrupt if corrupt else "none",
    }


if __name__ == '__main__':
    formulas = [
        ("爱因斯坦质能关系：", "E=mc^2"),
        ("离散求和定义：", "\\sum_{i=1}^{n} x_i"),
        ("Sigmoid 函数定义：", "\\frac{1}{1+e^{-x}}"),
        ("时域门控函数：", "g_t = \\sigma(W_t x_t + b_t)"),
        ("多尺度损失函数：", "L = \\frac{1}{N}\\sum_{i=1}^{N}(y_i - \\hat{y}_i)^2 + \\lambda\\|\\theta\\|_2^2"),
    ]

    output = Path(__file__).parent / "formula_demo_v6_raw.docx"
    build_docx(formulas, str(output))
    result = verify_docx(str(output))
    print(f"Created: {output}")
    print(f"Verification: {result}")
    if result.get("valid"):
        print(f"\n✅ Document is valid!")
        print(f"   OMML formulas: {result['omml']}")
        print(f"   SEQ MTEqn: {result['seq_mteqn']}")
        print(f"   MTDisplayEquation: {'yes' if result['mt_style'] else 'no'}")
        print(f"   Corruptions: {result['corruptions']}")
    else:
        print(f"\n❌ Document invalid: {result.get('error')}")
