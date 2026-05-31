"""Check the OMML XML in generated docx files."""
import zipfile
import re
from pathlib import Path

scripts_dir = Path(__file__).parent

# Check our test doc vs the working restored doc
docs_to_check = [
    ("test_approach1.docx", "Approach 1: manual OMML"),
    ("test_approach2.docx", "Approach 2: our converter"),
    ("test_approach4.docx", "Approach 4: oMathPara direct"),
]

for fname, desc in docs_to_check:
    path = scripts_dir / fname
    if not path.exists():
        print(f"{desc}: file not found")
        continue
    with zipfile.ZipFile(path, 'r') as zf:
        doc_xml = zf.read('word/document.xml').decode('utf-8')
    
    namespaces = re.findall(r'xmlns[^=]*="[^"]+"', doc_xml)
    omml_start = doc_xml.find('<m:oMath')
    has_omathpara = '<m:oMathPara' in doc_xml
    
    omml_chunk = ""
    if omml_start > 0:
        end = doc_xml.find('>', omml_start + 200) + 1
        omml_chunk = doc_xml[omml_start:end]
    
    print(f"\n=== {desc} ===")
    print(f"  oMathPara: {has_omathpara}")
    print(f"  First 8 namespaces:")
    for ns in namespaces[:8]:
        print(f"    {ns}")
    print(f"  OMML: {omml_chunk[:250]}")
