"""Compare XML structure between restored working doc and our generated doc."""
import zipfile, re
from pathlib import Path

p_restored = Path('论文_面向多尺度时序预测的时域门控混合模型_终版_完全修复.docx')
p_our = Path('.trae/skills/academic-formula-inserter/scripts/formula_demo_v2.docx')

# Restored doc
with zipfile.ZipFile(p_restored, 'r') as zf:
    doc_xml = zf.read('word/document.xml').decode('utf-8')
    rels = zf.read('word/_rels/document.xml.rels').decode('utf-8')

root_m = re.search(r'<w:document[^>]*>', doc_xml)
print("=== RESTORED document root ===")
if root_m: print(root_m.group()[:500])

print("\nRESTORED rels (math-related):")
for line in rels.split('<'):
    if 'math' in line.lower():
        print(f'  <{line}')

# Our doc
with zipfile.ZipFile(p_our, 'r') as zf:
    doc_xml2 = zf.read('word/document.xml').decode('utf-8')

root_m2 = re.search(r'<w:document[^>]*>', doc_xml2)
print("\n=== OUR document root ===")
if root_m2: print(root_m2.group()[:500])
