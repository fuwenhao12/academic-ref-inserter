---
name: "word-docx"
description: "Manipulate Word (.docx) documents — insert images, tables, format text, adjust page layout, add headers/footers. Invoke when user needs to insert pictures into Word, format docx files, or batch-process Word documents."
---

# Word Document Manipulation Skill

This skill handles all Word (.docx) document operations using Python's `python-docx` library and raw XML manipulation via `lxml`.

## Prerequisites

```bash
py -m pip install python-docx lxml
```

## Core Capabilities

### 1. Insert Images into Word

Use `python-docx` to insert images at specific positions, with optional sizing.

```python
from docx import Document
from docx.shared import Inches, Cm, Pt, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document("input.docx")

# Find a paragraph to insert after (e.g., searching by keyword)
target_idx = None
for i, para in enumerate(doc.paragraphs):
    if "关键词" in para.text or "Keywords" in para.text:
        target_idx = i
        break

# Insert image after target paragraph
if target_idx is not None:
    ref_element = doc.paragraphs[target_idx]._element
    from lxml import etree
    from docx.oxml.ns import qn
    
    new_p = etree.SubElement(ref_element.getparent(), qn('w:p'))
    # Add drawing element for image
    # ... (see detailed image insertion below)
    ref_element.addnext(new_p)

doc.save("output.docx")
```

### 2. Replace Images in Existing Document

To replace an image in an existing docx by extracting relationships and modifying the ZIP:

```python
import zipfile, os, shutil

def replace_image_in_docx(docx_path, old_image_name, new_image_path, output_path):
    """Replace an image inside a docx file by name"""
    with zipfile.ZipFile(docx_path, 'r') as zin:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename == f'word/media/{old_image_name}':
                    zout.write(new_image_path, item.filename)
                else:
                    zout.writestr(item, zin.read(item.filename))
```

### 3. Adjust Page Layout

```python
from docx.shared import Cm

for section in doc.sections:
    section.page_width = Cm(21.0)      # A4 width
    section.page_height = Cm(29.7)     # A4 height
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
```

### 4. Add Headers/Footers (with First-Page Different)

Use ZIP-level manipulation for reliable header/footer insertion:

```python
import zipfile
from lxml import etree

# Read docx as ZIP
with zipfile.ZipFile("input.docx", 'r') as zin:
    rels_xml = zin.read('word/_rels/document.xml.rels').decode('utf-8')
    doc_xml = zin.read('word/document.xml').decode('utf-8')
    # ... modify rels and doc_xml to add footer reference
    
    with zipfile.ZipFile("output.docx", 'w') as zout:
        # write modified files + new footer XML
```

### 5. Format Text & Paragraphs

```python
from docx.shared import Pt, RGBColor
from docx.oxml.ns import qn

# Set font size and family
run.font.size = Pt(10.5)  # 5号字
run.font.name = '宋体'
rPr = run._element.get_or_add_rPr()
rFonts = etree.SubElement(rPr, qn('w:rFonts'))
rFonts.set(qn('w:eastAsia'), '宋体')

# Set paragraph spacing
para.paragraph_format.line_spacing = 1.5
para.paragraph_format.space_before = Pt(0)
para.paragraph_format.space_after = Pt(0)
```

## Common Patterns

### Pattern A: Insert a PNG image from folder into Word

```python
from docx import Document
from docx.shared import Cm
from docx.oxml.ns import qn
import os

doc = Document("paper.docx")
images = ["fig1.png", "fig2.png", "fig3.png"]

for img_name in images:
    # Add centered image
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run()
    run.add_picture(img_name, width=Cm(14))  # 14cm wide
    
    # Add caption below
    cap = doc.add_paragraph("图X：标题")
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

doc.save("paper_with_images.docx")
```

### Pattern B: Batch-fix table formatting to three-line tables

```python
# Apply three-line table style (top rule, header rule, bottom rule)
from docx.oxml.ns import qn

for table in doc.tables:
    tbl = table._tbl
    tblPr = tbl.find(qn('w:tblPr'))
    if tblPr is None:
        tblPr = etree.SubElement(tbl, qn('w:tblPr'))
    # Set borders via tblBorders
```

## Key Notes

- **Word formula editor**: Formulas in `.docx` are stored as OMML (Office Math Markup Language) in `<m:oMath>` elements. Use lxml to inspect/modify.
- **Image resolution**: Images are stored in `word/media/` inside the ZIP. Keep PNG at 300+ DPI for print.
- **Chinese fonts**: Always set `w:eastAsia` font attribute for Chinese text in Word.
- **python-docx vs ZIP**: For complex operations (headers, footers, image replacement), prefer direct ZIP + XML manipulation.
