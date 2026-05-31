import re
from copy import deepcopy
from lxml import etree
from docx.oxml import parse_xml
from docx.oxml.ns import qn

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"

NUMBERING_STYLES = {
    "1": {"name": "中文核心", "format": "式({num})", "example": "式(1)", "desc": "适用于中文核心期刊"},
    "2": {"name": "圆括号", "format": "({num})", "example": "(1)", "desc": "适用于 IEEE、Elsevier 等国际期刊"},
    "3": {"name": "方括号", "format": "[{num}]", "example": "[1]", "desc": "适用于部分物理/数学期刊"},
    "4": {"name": "章节编号", "format": "({chapter}.{num})", "example": "(1.1)", "desc": "适用于学位论文/多章节文档"},
    "5": {"name": "LaTeX标签", "format": "\\tag{{{num}}}\\label{{eq:{num}}}", "example": "\\tag{1}", "desc": "LaTeX 原生格式"},
    "6": {"name": "中文+括号", "format": "式({num})", "example": "式(1)", "desc": "中文括号组合"},
    "7": {"name": "无编号", "format": "", "example": "无", "desc": "不添加编号"},
}


def interactive_numbering_prompt(prompt_text="请选择编号格式") -> str:
    print(f"\n{'='*50}")
    print(f"  {prompt_text}")
    print(f"{'='*50}")
    print(f"  {'编号':>4}  {'名称':<12} {'示例':<16} {'说明'}")
    print(f"  {'-'*46}")
    for key, style in NUMBERING_STYLES.items():
        print(f"  {key:>4}  {style['name']:<12} {style['example']:<16} {style['desc']}")
    print(f"  {'-'*46}")
    print(f"  输入编号 (1-7)，或按 Enter 使用默认 [2-圆括号]")

    while True:
        try:
            choice = input(f"  > ").strip()
            if choice == "":
                return "parentheses"
            if choice in NUMBERING_STYLES:
                return _style_key_to_id(choice)
            print(f"  ❌ 无效选择，请输入 1-7")
        except (EOFError, KeyboardInterrupt):
            print()
            return "parentheses"


def _style_key_to_id(key: str) -> str:
    mapping = {
        "1": "chinese",
        "2": "parentheses",
        "3": "brackets",
        "4": "section",
        "5": "latex-tag",
        "6": "chinese-alt",
        "7": "none",
    }
    return mapping.get(key, "parentheses")


def _style_id_to_format(style: str) -> str:
    fmt_formats = {
        "chinese": "式({num})",
        "parentheses": "({num})",
        "brackets": "[{num}]",
        "section": "({chapter}.{num})",
        "latex-tag": "\\tag{{{num}}}",
        "chinese-alt": "式({num})",
        "none": "",
    }
    return fmt_formats.get(style, "({num})")


def build_number_element(number_text: str, style: str, run_props: dict = None):
    m = M_NS
    w = W_NS

    nsmap = {
        'm': m,
        'w': w,
        'r': R_NS,
    }

    omath = etree.SubElement(etree.Element("_root"), f"{{{m}}}oMath")
    arg = etree.SubElement(omath, f"{{{m}}}arg")

    run = etree.SubElement(arg, f"{{{w}}}r")
    rpr = etree.SubElement(run, f"{{{w}}}rPr")

    sz = etree.SubElement(rpr, f"{{{w}}}sz")
    sz.set(f"{{{w}}}val", "20")

    rFonts = etree.SubElement(rpr, f"{{{w}}}rFonts")
    rFonts.set(f"{{{w}}}ascii", "Cambria Math")
    rFonts.set(f"{{{w}}}hAnsi", "Cambria Math")

    t = etree.SubElement(run, f"{{{m}}}t")
    t.set("xml:space", "preserve")
    t.text = number_text

    return omath


def number_equations_in_docx(doc, style: str = "parentheses", profile: dict = None, interactive: bool = False):
    from latex_omml_converter import detect_equations_in_docx

    equations = detect_equations_in_docx(doc)
    chapter_number = "1"

    if interactive:
        style = interactive_numbering_prompt(
            f"已检测到 {len(equations)} 个公式，请选择编号格式"
        )

    if style == "none":
        return 0

    if profile:
        fmt = profile.get("numbering_format", "({num})")
    else:
        fmt = _style_id_to_format(style)

    for i, eq in enumerate(equations):
        if style == "section":
            num_text = fmt.format(chapter=chapter_number, num=i + 1)
        else:
            num_text = fmt.format(num=i + 1)

        para = eq["paragraph"]
        _add_number_to_paragraph(para, num_text)

    return len(equations)


def _add_number_to_paragraph(para, number_text):
    p_elem = para._element
    jc = p_elem.find(f'{{{W_NS}}}pPr/{{{W_NS}}}jc')
    if jc is None:
        pPr = p_elem.find(f'{{{W_NS}}}pPr')
        if pPr is None:
            pPr = etree.SubElement(p_elem, f"{{{W_NS}}}pPr")
        jc = etree.SubElement(pPr, f"{{{W_NS}}}jc")
    jc.set(f"{{{W_NS}}}val", "center")

    tab = etree.SubElement(p_elem, f"{{{W_NS}}}r")
    tabPr = etree.SubElement(tab, f"{{{W_NS}}}rPr")
    tabChar = etree.SubElement(tab, f"{{{W_NS}}}tab")

    num_element = parse_xml(
        f'<w:r xmlns:w="{W_NS}">'
        f'  <w:rPr>'
        f'    <w:sz w:val="20"/>'
        f'    <w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/>'
        f'  </w:rPr>'
        f'  <w:rPr>'
        f'    <w:rStyle w:val="EquationNumber"/>'
        f'  </w:rPr>'
        f'  <w:t xml:space="preserve">{number_text}</w:t>'
        f'</w:r>'
    )

    p_elem.append(num_element)
