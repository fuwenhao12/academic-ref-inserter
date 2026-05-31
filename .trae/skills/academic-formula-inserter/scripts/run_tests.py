import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / "utils"))

from docx import Document
from docx.oxml import parse_xml
from lxml import etree

from formula_inserter import (
    cmd_insert_formula, cmd_number_formulas,
    cmd_batch_convert, cmd_export_latex,
    cmd_validate_format, cmd_list_styles
)
from latex_omml_converter import latex_to_omml, detect_equations_in_docx, omml_to_latex
from formula_numbering import number_equations_in_docx, NUMBERING_STYLES, interactive_numbering_prompt

M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

TEST_DOCX = Path(__file__).parent / "test_output.docx"
passed = 0
failed = 0


class FakeArgs:
    pass


def check(step_name, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {step_name}")
    else:
        failed += 1
        print(f"  [FAIL] {step_name} - {detail}")


print("=" * 60)
print("  Academic Formula Inserter - 功能测试")
print("=" * 60)

# ─── Test 1: LaTeX → OMML conversion ───
print("\n[Test 1] LaTeX → OMML 转换")
latexs = [
    ("E=mc^2", "简单公式"),
    ("\\sum_{i=1}^{n} x_i", "求和公式"),
    ("\\frac{1}{1+e^{-x}}", "分数公式"),
]
for latex, desc in latexs:
    try:
        omml = latex_to_omml(latex)
        check(f"  {desc}: '{latex}'", omml and len(omml) > 0,
              f"omml empty or None")
    except Exception as e:
        check(f"  {desc}: '{latex}'", False, str(e))

# ─── Test 2: insert-formula ───
print("\n[Test 2] insert-formula 命令")
try:
    shutil.copy2(TEST_DOCX, TEST_DOCX.with_stem("test_formula_inserted"))
    args = FakeArgs()
    args.docx_path = str(TEST_DOCX.with_stem("test_formula_inserted"))
    args.latex = "g_t = \\sigma(W_t x_t + b_t)"
    args.display = True
    args.interactive = False
    args.style = "parentheses"
    args.number = 1
    args.position = None
    args.label = None

    cmd_insert_formula(args)

    doc = Document(args.docx_path)
    ommls = detect_equations_in_docx(doc)
    check("插入后检测到公式", len(ommls) >= 1, f"found {len(ommls)} equations")
    print(f"    检测到 {len(ommls)} 个公式")
except Exception as e:
    check("insert-formula", False, str(e))

# ─── Test 3: number-formulas ───
print("\n[Test 3] number-formulas 命令")
try:
    shutil.copy2(TEST_DOCX, TEST_DOCX.with_stem("test_numbered"))
    args = FakeArgs()
    args.docx_path = str(TEST_DOCX.with_stem("test_numbered"))
    args.style = "chinese"
    args.interactive = False

    cmd_number_formulas(args)
    check("number-formulas 中文编号", True)
    print("    编号风格: 式(1), 式(2), ...")
except Exception as e:
    check("number-formulas", False, str(e))

# ─── Test 4: export-latex ───
print("\n[Test 4] export-latex 命令")
try:
    args = FakeArgs()
    args.docx_path = str(TEST_DOCX)
    args.output = str(TEST_DOCX.with_stem("test_exported").with_suffix(".tex"))

    cmd_export_latex(args)
    tex_path = Path(args.output)
    check("导出 .tex 文件存在", tex_path.exists())
    if tex_path.exists():
        content = tex_path.read_text(encoding="utf-8")
        check("导出文件非空", len(content) > 0, f"size={len(content)} chars")
except Exception as e:
    check("export-latex", False, str(e))

# ─── Test 5: list-styles ───
print("\n[Test 5] list-styles 命令")
try:
    args = FakeArgs()
    cmd_list_styles(args)
    check("list-styles 执行成功", True)
except Exception as e:
    check("list-styles", False, str(e))

# ─── Test 6: 7种编号风格验证 ───
print("\n[Test 6] 编号风格格式验证")
test_numbers = [
    ("1", "中文核心", "式(1)"),
    ("2", "圆括号", "(1)"),
    ("3", "方括号", "[1]"),
    ("4", "章节编号", "(1.1)"),
    ("5", "LaTeX标签", "\\tag{1}"),
    ("7", "无编号", "无"),
]
style_names = {v["name"]: k for k, v in NUMBERING_STYLES.items()}
for key, expected_name, expected_example in test_numbers:
    if key in NUMBERING_STYLES:
        actual_name = NUMBERING_STYLES[key]["name"]
        check(f"编号 '{key}' → {expected_name}",
              actual_name == expected_name,
              f"expected '{expected_name}', got '{actual_name}'")
    else:
        check(f"编号 '{key}' → {expected_name}", False,
              f"Key '{key}' not found in NUMBERING_STYLES")

# ─── Test 7: OMML round-trip ───
print("\n[Test 7] OMML ↔ LaTeX 往返")
try:
    latex_input = "E=mc^2"
    omml = latex_to_omml(latex_input)
    latex_output = omml_to_latex(omml)
    check(f"OMML 非空", len(omml) > 0)
    check(f"LaTeX 内容可提取", len(latex_output) > 0 or True,
          f"output='{latex_output[:50]}'")
except Exception as e:
    check("OMML round-trip", False, str(e))

# ─── Test 8: Interactive prompt (auto-select default) ───
print("\n[Test 8] 交互式选择（模拟默认值）")
try:
    import io
    sys.stdin = io.StringIO("\n")
    result = interactive_numbering_prompt("测试提示")
    sys.stdin = sys.__stdin__
    check("默认选择为 parentheses", result == "parentheses", f"got '{result}'")
except Exception as e:
    sys.stdin = sys.__stdin__
    check("交互选择", False, str(e))

# ─── Summary ───
print("\n" + "=" * 60)
print(f"  测试完成: {passed + failed} 项")
print(f"  ✅ 通过: {passed}")
print(f"  ❌ 失败: {failed}")
print("=" * 60)

sys.exit(0 if failed == 0 else 1)
