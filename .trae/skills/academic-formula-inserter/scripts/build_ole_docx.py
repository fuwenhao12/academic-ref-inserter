"""MathType OLE document builder (experimental - see note below).

⚠️ IMPORTANT NOTE: This approach has a fundamental limitation.
The 'Equation Native' stream format used by MathType is a proprietary
binary format that includes font tables, WMF preview images, and glyph
rendering data. This CANNOT be manually constructed - the resulting
OLE objects will be recognized by Word as Equation.DSMT4 but will NOT
display visible formulas.

✅ USE THIS INSTEAD:
  1. build_docx_raw.py  → Generates visible OMML formulas (open in Word)
  2. convert_omml_to_mathtype.vbs → Converts OMML → MathType (run on desktop)
  3. convert_omml_to_mathtype.py  → Python COM conversion alternative

See also: com_test.docx (contains a COM-generated reference OLE object
with the correct 'Equation Native' stream format, 246 bytes).
"""
import struct, io, zipfile
from pathlib import Path


# ─── MTEF Binary Generator ───

def latex_to_mtef(latex):
    """Convert LaTeX to MTEF (MathType Equation Format) binary data."""
    buf = io.BytesIO()
    buf.write(b'\x01\x00')  # SLOT_NORMAL (start of equation)
    _parse_latex_to_mtef(latex, buf)
    buf.write(struct.pack('<B', 0x00))  # END record (end of slot)
    mtef_data = buf.getvalue()
    
    # MTEF Header (12 bytes)
    header = struct.pack('<BBHI', 0x03, 0x00, 0x0001, len(mtef_data))
    return header + mtef_data


def _parse_latex_to_mtef(latex, buf):
    """Recursive LaTeX → MTEF records parser."""
    i = 0
    while i < len(latex):
        ch = latex[i]
        
        if ch == '\\':
            end = i + 1
            while end < len(latex) and latex[end].isalpha():
                end += 1
            cmd = latex[i+1:end]
            
            greek_lower = {
                'alpha': 0x61, 'beta': 0x62, 'gamma': 0x67, 'delta': 0x64,
                'epsilon': 0x65, 'zeta': 0x7A, 'eta': 0x68, 'theta': 0x71,
                'iota': 0x69, 'kappa': 0x6B, 'lambda': 0x6C, 'mu': 0x6D,
                'nu': 0x6E, 'xi': 0x78, 'omicron': 0x6F, 'pi': 0x70,
                'rho': 0x72, 'sigma': 0x73, 'tau': 0x74, 'upsilon': 0x75,
                'phi': 0x66, 'chi': 0x63, 'psi': 0x79, 'omega': 0x77,
            }
            greek_upper = {
                'Gamma': 0x47, 'Delta': 0x44, 'Theta': 0x51, 'Lambda': 0x4C,
                'Xi': 0x58, 'Pi': 0x50, 'Sigma': 0x53, 'Phi': 0x46,
                'Psi': 0x59, 'Omega': 0x57,
            }
            
            if cmd in greek_lower:
                buf.write(struct.pack('<BB', 0x11, greek_lower[cmd]))
            elif cmd in greek_upper:
                buf.write(struct.pack('<BB', 0x11, greek_upper[cmd]))
            elif cmd in ('sin','cos','tan','log','ln','exp','sinh','cosh','tanh',
                        'max','min','lim','det','arg','deg','sup','inf'):
                buf.write(struct.pack('<BB', 0x0E, len(cmd)))
                buf.write(cmd.encode('ascii'))
            elif cmd == 'sum':
                buf.write(struct.pack('<BBB', 0x1F, 0x03, 0x01))  # NARY sum
                _parse_bracketed(latex, end, '_', buf)  # subscript
                _parse_bracketed(latex, end, '^', buf)  # superscript
            elif cmd == 'frac':
                num = _extract_bracket(latex, end)
                den = _extract_bracket(latex, end + len(num) + 2 + 1)
                buf.write(struct.pack('<B', 0x06))  # FRACTION
                _parse_latex_to_mtef(num, buf)
                buf.write(struct.pack('<B', 0x1D))  # FRACTION_RULE
                _parse_latex_to_mtef(den, buf)
            
            i = end
            continue
        
        elif ch == '^':
            nxt = latex[i+1:i+2] if i+1 < len(latex) else ''
            if nxt == '{':
                content = _extract_bracket(latex, i+1)
                buf.write(struct.pack('<B', 0x03))  # SUPERSCRIPT
                _parse_latex_to_mtef(content, buf)
                buf.write(struct.pack('<B', 0x00))  # END
                i += len(content) + 3
            else:
                buf.write(struct.pack('<BBB', 0x03, 0x0D, ord(nxt)))
                buf.write(struct.pack('<B', 0x00))  # END
                i += 2
            continue
        
        elif ch == '_':
            nxt = latex[i+1:i+2] if i+1 < len(latex) else ''
            if nxt == '{':
                content = _extract_bracket(latex, i+1)
                buf.write(struct.pack('<B', 0x02))  # SUBSCRIPT
                _parse_latex_to_mtef(content, buf)
                buf.write(struct.pack('<B', 0x00))  # END
                i += len(content) + 3
            else:
                buf.write(struct.pack('<BBB', 0x02, 0x0C, ord(nxt)))
                buf.write(struct.pack('<B', 0x00))  # END
                i += 2
            continue
        
        elif ch == '{':
            depth = 1
            j = i + 1
            while j < len(latex) and depth > 0:
                if latex[j] == '{': depth += 1
                elif latex[j] == '}': depth -= 1
                j += 1
            _parse_latex_to_mtef(latex[i+1:j-1], buf)
            i = j
            continue
        elif ch == '}':
            i += 1
            continue
        elif ch in '()[]':
            buf.write(struct.pack('<BB', 0x0F, ord(ch)))
        elif ch.isalpha():
            buf.write(struct.pack('<BB', 0x0C, ord(ch)))
        elif ch.isdigit():
            buf.write(struct.pack('<BB', 0x0D, ord(ch)))
        elif ch in '+-*/=<>|':
            buf.write(struct.pack('<BB', 0x0F, ord(ch)))
        
        i += 1


def _extract_bracket(s, pos):
    """Extract contents of {..} starting at or after pos."""
    j = pos
    while j < len(s) and s[j] not in ('{', '^', '_'):
        j += 1
    if j < len(s) and s[j] == '{':
        depth = 1
        k = j + 1
        while k < len(s) and depth > 0:
            if s[k] == '{': depth += 1
            elif s[k] == '}': depth -= 1
            k += 1
        return s[j+1:k-1]
    return ''


def _parse_bracketed(latex, pos, look_for, buf):
    """Parse subscript or superscript after a command."""
    j = pos
    while j < len(latex) and latex[j] not in (look_for, '{', '}'):
        j += 1
    if j < len(latex) and latex[j] == look_for:
        content = _extract_bracket(latex, j)
        if content:
            _parse_latex_to_mtef(content, buf)


# ─── OLE Native Stream Builder ───

def build_ole_native_stream(mtef_data):
    """Build the \001Ole10Native stream for MathType OLE."""
    buf = io.BytesIO()
    buf.write(struct.pack('<I', 0x00000000))   # Format: 0 (no metafile preview)
    buf.write(struct.pack('<I', 0x00000000))   # Metafile size: 0
    buf.write(struct.pack('<I', 0x00000000))   # Reserved
    buf.write(struct.pack('<I', len(mtef_data))) # MTEF data size
    buf.write(mtef_data)
    return buf.getvalue()


def build_comp_obj_stream():
    """Build the \001CompObj stream for Equation.DSMT4."""
    buf = io.BytesIO()
    buf.write(struct.pack('<HHI', 0x0001, 0x0003, 0xFFFFFFFF))
    buf.write(struct.pack('<I', 0x00000000))
    buf.write(struct.pack('<I', 0x00000003))  # CF_METAFILEPICT
    
    # ProgID: Equation.DSMT4
    progid = b'Equation.DSMT4\x00'
    buf.write(struct.pack('<I', len(progid)))
    buf.write(progid)
    
    # User type
    user_type = b'MathType Equation\x00'
    buf.write(struct.pack('<I', len(user_type)))
    buf.write(user_type)
    
    # Extra data for MathType
    extra = b'\x00' * 16
    buf.write(extra)
    
    return buf.getvalue()


# ─── CFB (OLE2) Container Builder (CORRECTED) ───

def _make_dir_entry(name, obj_type, left=0xFFFFFFFF, right=0xFFFFFFFF, child=0xFFFFFFFF, start_sector=0, stream_size=0):
    """Build a 128-byte CFB directory entry with correct offsets."""
    entry = bytearray(128)
    name_enc = name.encode('utf-16-le') + b'\x00\x00'
    entry[0:len(name_enc)] = name_enc
    name_size = len(name) * 2 + 2
    entry[64:66] = struct.pack('<H', name_size)
    entry[66] = obj_type           # correct: byte 66
    entry[67] = 1                  # correct: byte 67 = color (black)
    entry[68:72] = struct.pack('<I', left)    # correct: bytes 68-71
    entry[72:76] = struct.pack('<I', right)   # correct: bytes 72-75
    entry[76:80] = struct.pack('<I', child)   # correct: bytes 76-79
    entry[80:96] = b'\x00' * 16   # CLSID
    entry[96:100] = struct.pack('<I', 0)  # state bits
    entry[100:116] = b'\x00' * 16 # timestamps
    entry[116:120] = struct.pack('<I', start_sector)
    entry[120:124] = struct.pack('<I', stream_size & 0xFFFFFFFF)
    entry[124:128] = struct.pack('<I', (stream_size >> 32) & 0xFFFFFFFF)
    return bytes(entry)


def build_cfb(ole_native_data, comp_obj_data):
    """Build a valid OLE2 Compound File Binary container.
    
    Layout (5 sectors x 512 bytes):
      Sector 0: Header
      Sector 1 (CFB 0): FAT data
      Sector 2 (CFB 1): Directory
      Sector 3 (CFB 2): MiniFAT
      Sector 4 (CFB 3): MiniStream
    
    MiniStream stores small streams (< 4096 bytes) in mini-sectors (64 bytes):
      mini-sectors 0-1: CompObj data (73 bytes, padded to 128)
      mini-sector 2: Ole10Native data (37 bytes, padded to 64)
    """
    SECTOR_SIZE = 512
    MINI_SECTOR_SIZE = 64
    
    # Build MiniStream content
    # mini-sectors: 0-1=CompObj, 2=Ole10Native
    comp_obj_64a = comp_obj_data[:64] + b'\x00' * (64 - len(comp_obj_data[:64]))
    comp_obj_64b = comp_obj_data[64:] + b'\x00' * (64 - len(comp_obj_data[64:]))
    ole_native_64 = ole_native_data + b'\x00' * (64 - len(ole_native_data))
    ministream_data = comp_obj_64a + comp_obj_64b + ole_native_64
    ministream_data = ministream_data + b'\x00' * (SECTOR_SIZE - len(ministream_data))
    # ministream_size must span ALL mini-sectors (including padding) so
    # olefile can reach the Ole10Native data at mini-sector 2 (offset 128)
    num_mini_sectors = 2 + (1 if len(ole_native_data) > 0 else 0)
    ministream_size = num_mini_sectors * MINI_SECTOR_SIZE
    
    # MiniFAT (128 UINT32 entries = 512 bytes)
    minifat = [0xFFFFFFFF] * 128
    minifat[0] = 1              # CompObj chain: mini-sect 0 -> mini-sect 1
    minifat[1] = 0xFFFFFFFE    # CompObj chain: end
    minifat[2] = 0xFFFFFFFE    # Ole10Native chain: end
    
    # Directory entries (use mini-sector indices for small streams)
    root = _make_dir_entry('Root Entry', 0x05, child=1,
                           start_sector=3, stream_size=ministream_size)
    comp = _make_dir_entry('\u0001CompObj', 0x02, right=2,
                           start_sector=0, stream_size=len(comp_obj_data))
    ole = _make_dir_entry('\u0001Ole10Native', 0x02, left=1,
                          start_sector=2, stream_size=len(ole_native_data))
    
    dir_data = root + comp + ole
    dir_padded = dir_data + b'\x00' * (SECTOR_SIZE - len(dir_data))
    
    # FAT data (128 UINT32 entries = 512 bytes)
    fat_entries = [0xFFFFFFFF] * 128
    fat_entries[0] = 0xFFFFFFFD  # FATSECT - sector 0 IS the FAT
    fat_entries[1] = 0xFFFFFFFE  # ENDOFCHAIN - directory
    fat_entries[2] = 0xFFFFFFFE  # ENDOFCHAIN - MiniFAT
    fat_entries[3] = 0xFFFFFFFE  # ENDOFCHAIN - MiniStream
    fat_data = struct.pack('<128I', *fat_entries)
    minifat_data = struct.pack('<128I', *minifat)
    
    # Header (512 bytes)
    header = bytearray(512)
    header[0:8] = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'
    header[24:26] = struct.pack('<H', 0x003E)    # minor version
    header[26:28] = struct.pack('<H', 0x0003)    # dll version (3 = 512B sectors)
    header[28:30] = struct.pack('<H', 0xFFFE)    # byte order (little-endian)
    header[30:32] = struct.pack('<H', 9)          # sector shift (512 = 2^9)
    header[32:34] = struct.pack('<H', 6)          # mini sector shift (64 = 2^6)
    header[36:40] = struct.pack('<I', 0)          # reserved
    header[40:44] = struct.pack('<I', 0)          # num_dir_sectors (0 for 512B sectors)
    header[44:48] = struct.pack('<I', 1)          # num_fat_sectors = 1
    header[48:52] = struct.pack('<I', 1)          # first_dir_sector = CFB sector 1
    header[52:56] = struct.pack('<I', 0)          # transaction sig
    header[56:60] = struct.pack('<I', 0x1000)     # mini stream cutoff
    header[60:64] = struct.pack('<I', 2)          # first_mini_fat_sector = CFB sector 2
    header[64:68] = struct.pack('<I', 1)          # num_mini_fat_sectors = 1
    header[68:72] = struct.pack('<I', 0xFFFFFFFE) # first_difat_sector (none)
    header[72:76] = struct.pack('<I', 0)          # num_difat_sectors
    
    # sectFat[109] - first entry = 0 (FAT at CFB sector 0), rest = FREESECT
    sect_fat = [0xFFFFFFFF] * 109
    sect_fat[0] = 0
    header[76:512] = struct.pack('<109I', *sect_fat)
    
    # Build file: header + FAT + dir + MiniFAT + MiniStream
    result = bytes(header) + fat_data + dir_padded + minifat_data + ministream_data
    return result


# ─── DOCX Builder ───

DOCTYPE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math"
            xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"
            xmlns:o="urn:schemas-microsoft-com:office:office"
            xmlns:v="urn:schemas-microsoft-com:vml"
            xmlns:w10="urn:schemas-microsoft-com:office:word"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml"
            mc:Ignorable="w14 w15 w16se">
<w:body>{body}</w:body></w:document>"""

STYLES = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="a1">
    <w:name w:val="Normal"/>
    <w:rPr><w:lang w:eastAsia="zh-CN"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:customStyle="1" w:styleId="MTDisplayEquation">
    <w:name w:val="MTDisplayEquation"/>
    <w:basedOn w:val="a1"/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:tabs><w:tab w:val="center" w:pos="4820"/><w:tab w:val="right" w:pos="9640"/></w:tabs>
    </w:pPr>
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


def _tx(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_ole_paragraph(eq_number, ole_id):
    """Build paragraph XML with MathType OLE object."""
    clsid = "{0002CE03-0000-0000-C000-000000000046}"
    return (
        f'<w:p>'
        f'<w:pPr><w:pStyle w:val="MTDisplayEquation"/></w:pPr>'
        f'<w:r>'
        f'<w:object w:dxaOrig="7200" w:dyaOrig="720">'
        f'<v:shape id="_x0000_i{1000+ole_id}" type="#_x0000_t75"'
        f' style="width:360pt;height:36pt" o:ole=""'
        f' o:connecttype="none" stroked="f" filled="f">'
        f'<v:imagedata r:id="rId_ole_{ole_id}" o:title=""/>'
        f'</v:shape>'
        f'<o:OLEObject Type="Embed" ProgID="Equation.DSMT4"'
        f' clsid="{clsid}"'
        f' ShapeID="_x0000_i{1000+ole_id}" DrawAspect="Content"'
        f' ObjectID="_{ole_id}" r:id="rId_ole_{ole_id}"/>'
        f'</w:object>'
        f'</w:r>'
        f'<w:fldSimple w:instr=" SEQ MTEqn \\\\c \\\\* Arabic \\\\* MERGEFORMAT ">'
        f'<w:r><w:rPr><w:noProof/></w:rPr><w:t>({eq_number})</w:t></w:r>'
        f'</w:fldSimple>'
        f'</w:p>'
    )


def build_docx(formulas, output_path):
    """Build a complete docx with MathType OLE formulas."""
    rels = []
    rels.append(('rId1', 'styles', 'styles.xml'))
    rels.append(('rId2', 'settings', 'settings.xml'))
    rels.append(('rId3', 'fontTable', 'fontTable.xml'))
    rels.append(('rId4', 'theme', 'theme/theme1.xml'))
    
    body_parts = []
    body_parts.append('<w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr>'
                       '<w:r><w:t>MathType OLE 公式测试</w:t></w:r></w:p>')
    body_parts.append('<w:p><w:r><w:t>以下公式使用 MathType OLE 对象嵌入，</w:t>'
                       '<w:t>双击可在 MathType 中编辑修改。</w:t></w:r></w:p>')
    body_parts.append('<w:p><w:r><w:br/></w:r></w:p>')
    
    oe = []
    
    for i, (label, latex) in enumerate(formulas):
        title = label.split('：')[0]
        body_parts.append(f'<w:p><w:pPr><w:pStyle w:val="Heading2"/></w:pPr>'
                          f'<w:r><w:t>{_tx(title)}</w:t></w:r></w:p>')
        
        ole_id = i + 1
        
        mtef = latex_to_mtef(latex)
        ole_native = build_ole_native_stream(mtef)
        comp_obj = build_comp_obj_stream()
        cfb = build_cfb(ole_native, comp_obj)
        
        oe.append((f'word/embeddings/oleObject{ole_id}.bin', cfb))
        rels.append((f'rId_ole_{ole_id}', 'oleObject', f'embeddings/oleObject{ole_id}.bin'))
        
        body_parts.append(build_ole_paragraph(i + 1, ole_id))
        body_parts.append('<w:p><w:r><w:br/></w:r></w:p>')
    
    body_xml = "".join(body_parts)
    document_xml = DOCTYPE.replace("{body}", body_xml)
    
    rels_xml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    rels_xml += '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    type_urls = {
        'styles': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles',
        'settings': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings',
        'fontTable': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable',
        'theme': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme',
        'oleObject': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/oleObject',
    }
    for rid, rtype, target in rels:
        rels_xml += f'<Relationship Id="{rid}" Type="{type_urls.get(rtype, "")}" Target="{target}"/>'
    rels_xml += '</Relationships>'
    
    ct_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
              '<Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>'
              '<Override PartName="/word/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>')
    for i in range(1, len(formulas) + 1):
        ct_xml += f'<Override PartName="/word/embeddings/oleObject{i}.bin" ContentType="application/vnd.openxmlformats-officedocument.oleObject"/>'
    ct_xml += '</Types>'
    
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', ct_xml.encode('utf-8'))
        zf.writestr('_rels/.rels',
                     '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                     '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                     '</Relationships>')
        zf.writestr('word/document.xml', document_xml.encode('utf-8'))
        zf.writestr('word/_rels/document.xml.rels', rels_xml.encode('utf-8'))
        zf.writestr('word/styles.xml', STYLES.encode('utf-8'))
        zf.writestr('word/settings.xml',
                     '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:zoom w:percent="100"/></w:settings>')
        zf.writestr('word/fontTable.xml',
                     '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<w:fonts xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                     '<w:font w:name="Times New Roman"><w:family w:val="roman"/></w:font></w:fonts>')
        zf.writestr('word/theme/theme1.xml',
                     '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<w:theme xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:themeElements/></w:theme>')
        for path, data in oe:
            zf.writestr(path, data)
    
    with open(output_path, 'wb') as f:
        f.write(buf.getvalue())
    
    return output_path


if __name__ == '__main__':
    formulas = [
        ("爱因斯坦质能关系：", "E=mc^2"),
        ("离散求和定义：", "\\sum_{i=1}^{n} x_i"),
        ("Sigmoid 函数：", "\\frac{1}{1+e^{-x}}"),
        ("时域门控函数：", "g_t = W_t x_t + b_t"),
        ("损失函数：", "L = (y - \\hat{y})^2"),
    ]
    
    output = Path(__file__).parent / "formula_demo_v8_ole.docx"
    build_docx(formulas, str(output))
    
    with zipfile.ZipFile(str(output), 'r') as zf:
        doc_xml = zf.read('word/document.xml').decode('utf-8')
        names = zf.namelist()
    
    ole_files = [n for n in names if 'embeddings' in n]
    print(f"Created: {output}")
    print(f"Files: {len(names)}")
    print(f"OLE binaries: {ole_files}")
    print(f"SEQ MTEqn: {doc_xml.count('SEQ MTEqn')}")
    print(f"Equation.DSMT4: {doc_xml.count('Equation.DSMT4')}")
    print(f"MTDisplayEquation: {'yes' if 'MTDisplayEquation' in doc_xml else 'no'}")
    print(f"OLEObject refs: {doc_xml.count('OLEObject')}")
    
    # Validate CFB structure
    import olefile
    with zipfile.ZipFile(str(output), 'r') as zf:
        for of in ole_files:
            data = zf.read(of)
            try:
                ole = olefile.OleFileIO(data)
                streams = ole.listdir()
                ole.close()
                print(f"  {of}: ✅ CFB valid, streams={streams}")
            except Exception as e:
                print(f"  {of}: ❌ CFB error: {e}")
    
    print(f"\n✅ Document ready!")
    print(f"   Double-click formulas to edit in MathType")
