# -*- coding: utf-8 -*-
"""全面检查Word文档格式问题"""
import zipfile, os, re
from lxml import etree

docx = r"c:\Users\HP\Desktop\汇总\submission_package_computer_engineering\submission_package\论文_面向多尺度时序预测的时域门控混合模型_终版.docx"

NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS_M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'

with zipfile.ZipFile(docx, 'r') as z:
    doc_xml = z.read('word/document.xml')
    root = etree.fromstring(doc_xml)

    paragraphs = root.findall(f'.//{{{NS_W}}}p')
    texts = []
    for p in paragraphs:
        runs = p.findall(f'.//{{{NS_W}}}t')
        ptext = ''.join([r.text or '' for r in runs])
        texts.append(ptext)
    full_text = '\n'.join(texts)

    print("=" * 70)
    print("  《计算机工程与应用》格式检查报告")
    print("=" * 70)

    # 1. Page
    print("\n[1] 页面设置")
    sectPr = root.find(f'.//{{{NS_W}}}sectPr')
    if sectPr is not None:
        pgSz = sectPr.find(f'{{{NS_W}}}pgSz')
        pgMar = sectPr.find(f'{{{NS_W}}}pgMar')
        if pgSz is not None:
            w = int(pgSz.get(f'{{{NS_W}}}w', 0))
            h = int(pgSz.get(f'{{{NS_W}}}h', 0))
            ok = abs(w - 11906) < 100 and abs(h - 16838) < 100
            print(f"  纸张: {w}x{h} EMU" + (" [OK] A4" if ok else " [ERROR] 非A4"))
        if pgMar is not None:
            top = int(pgMar.get(f'{{{NS_W}}}top', 0))
            bot = int(pgMar.get(f'{{{NS_W}}}bottom', 0))
            lef = int(pgMar.get(f'{{{NS_W}}}left', 0))
            rig = int(pgMar.get(f'{{{NS_W}}}right', 0))
            ok2 = all(abs(x - 720000) < 50000 for x in [top, bot, lef, rig])
            print(f"  边距: 上{top/914400:.1f}in 下{bot/914400:.1f}in 左{lef/914400:.1f}in 右{rig/914400:.1f}in" + (" [OK] 2cm" if ok2 else " [ERROR] 非2cm"))

    # 2. Font
    print("\n[2] 正文字体")
    fonts_found = set()
    for r in root.iter(f'{{{NS_W}}}r'):
        rPr = r.find(f'{{{NS_W}}}rPr')
        if rPr is not None:
            rFonts = rPr.find(f'{{{NS_W}}}rFonts')
            if rFonts is not None:
                af = rFonts.get(f'{{{NS_W}}}ascii', '')
                ef = rFonts.get(f'{{{NS_W}}}eastAsia', '')
                if af and af != 'Symbol':
                    fonts_found.add(af)
                if ef:
                    fonts_found.add(ef)
    print(f"  字体: {', '.join(fonts_found)}")
    if '宋体' in str(fonts_found):
        print("   [OK] 含宋体")
    else:
        print("   [ERROR] 未使用宋体")

    # 3. Headings
    print("\n[3] 标题格式")
    hcount = 0
    for p in paragraphs:
        pPr = p.find(f'{{{NS_W}}}pPr')
        if pPr is not None:
            ps = pPr.find(f'{{{NS_W}}}pStyle')
            if ps is not None:
                s = ps.get(f'{{{NS_W}}}val', '')
                if 'heading' in s.lower() or 'head' in s.lower():
                    hcount += 1
    print(f"  标题样式段落: {hcount}")

    # 4. Abstract & Keywords
    print("\n[4] 摘要与关键词")
    print(f"  '摘要': {'[OK]' if '摘要' in full_text else '[ERROR] 未找到'}")
    print(f"  '关键词': {'[OK]' if '关键词' in full_text else '[ERROR] 未找到'}")
    print(f"  'Abstract': {'[OK]' if 'Abstract' in full_text else '[ERROR] 未找到'}")
    print(f"  'Key words': {'[OK]' if 'Key words' in full_text.lower() else '[ERROR] 未找到'}")

    # 5. References
    print("\n[5] 参考文献")
    refs = re.findall(r'\[(\d+)\]', full_text)
    unique = sorted(set(int(x) for x in refs))
    print(f"  引用: [{min(unique)}-{max(unique)}] 共{len(unique)}个")
    print(f"  参考文献列表: {'[OK]' if '参考文献' in full_text else '[ERROR] 未找到'}")

    # 6. Figures & Tables
    print("\n[6] 图表")
    blips = len(root.findall(f'.//{{http://schemas.openxmlformats.org/drawingml/2006/main}}blip'))
    tables = len(root.findall(f'.//{{{NS_W}}}tbl'))
    print(f"  图片: {blips}")
    print(f"  表格: {tables}")

    # 7. Superscript
    print("\n[7] 参考文献上标")
    va_count = 0
    for r in root.iter(f'{{{NS_W}}}r'):
        rPr = r.find(f'{{{NS_W}}}rPr')
        if rPr is not None:
            va = rPr.find(f'{{{NS_W}}}vertAlign')
            if va is not None and va.get(f'{{{NS_W}}}val') == 'superscript':
                va_count += 1
    print(f"  上标格式运行: {va_count}" + (" [OK]" if va_count > 0 else " [ERROR] 无上标"))

    # 8. Formulas
    print("\n[8] 公式")
    omml = len(root.findall(f'.//{{{NS_M}}}oMath'))
    ommlp = len(root.findall(f'.//{{{NS_M}}}oMathPara'))
    # Check for OLE objects (MathType)
    ole_count = len(root.findall(f'.//{{{NS_W}}}object'))
    # Check for embedded objects in relationships
    print(f"  OMML公式: {omml} 内联 + {ommlp} 独立行")
    print(f"  OLE对象(Mathtype): {ole_count}")
    if omml + ommlp == 0 and ole_count == 0:
        # Check for images that might be formula screenshots
        # Look for small images near formula text
        print("  [ERROR] 无OMML/OLE公式，可能为图片格式")
    elif ole_count > 0:
        print("  [INFO] 公式为MathType OLE格式")

    # 9. Classification
    print("\n[9] 中图分类号")
    print(f"  TP183: {'[OK]' if 'TP183' in full_text else '[ERROR] 未找到'}")

    # 10. Word count
    print("\n[10] 字数")
    cn = len(re.findall(r'[\u4e00-\u9fff]', full_text))
    en = len(re.findall(r'[a-zA-Z]+', full_text))
    print(f"  中文字: {cn}, 英文词: {en}, 合计: ~{cn+en}")

    # 11. Cross-ref
    print("\n[11] 交叉引用")
    seq = doc_xml.count(b'SEQ ')
    ref = doc_xml.count(b'REF ')
    print(f"  SEQ题注: {seq}, REF引用: {ref}")

    # 12. Summary
    print("\n" + "=" * 70)
    print("  问题汇总:")
    issues = []
    if pgMar is not None:
        if not all(abs(int(pgMar.get(f'{{{NS_W}}}{x}', 0)) - 720000) < 50000 for x in ['top','bottom','left','right']):
            issues.append("  [ERROR] 页边距不是2cm")
    if omml + ommlp == 0 and ole_count == 0:
        issues.append("  [ERROR] 公式不是OMML/MathType格式（可能是图片）")
    elif omml + ommlp == 0 and ole_count > 0:
        pass  # MathType OLE is acceptable
    if '宋体' not in str(fonts_found):
        issues.append("  [ERROR] 未使用宋体")
    if 'TP183' not in full_text:
        issues.append("  [ERROR] 未标注中图分类号TP183")
    if va_count == 0:
        issues.append("  [ERROR] 参考文献未设为上标")
    if cn+en < 7500:
        issues.append(f"  [WARN] 字数约{cn+en}，建议7500+")
    if seq == 0:
        issues.append("  [WARN] 缺少题注自动编号")

    if issues:
        for i in issues:
            print(i)
    else:
        print("  [OK] 全部通过！")
