import re
from copy import deepcopy
from lxml import etree
from docx.oxml import parse_xml
from docx.oxml.ns import qn

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


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


def number_equations_in_docx(doc, style: str = "parentheses", profile: dict = None):
    from latex_omml_converter import detect_equations_in_docx

    equations = detect_equations_in_docx(doc)
    chapter_number = "1"

    if profile:
        fmt = profile.get("numbering_format", "({num})")
    else:
        fmt_formats = {
            "chinese": "式({num})",
            "parentheses": "({num})",
            "brackets": "[{num}]",
            "section": "({chapter}.{num})",
            "latex-tag": "\\tag{{{num}}}",
        }
        fmt = fmt_formats.get(style, "({num})")

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
