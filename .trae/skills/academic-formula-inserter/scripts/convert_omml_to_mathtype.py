"""Convert OMML equations in a .docx to MathType OLE objects via COM automation.

This script uses Microsoft Word's COM API (with MathType installed) to convert
OMML (Office Math Markup Language) equations into MathType OLE objects.

Requirements:
  - Microsoft Word (2010 or later)
  - MathType (6.x or 7.x) installed as a Word add-in
  - pywin32 (pip install pywin32)

Usage:
  # Convert all equations in a document
  py convert_omml_to_mathtype.py input.docx [output.docx]

  # Generate visible OMML document first, then convert
  py build_docx_raw.py
  py convert_omml_to_mathtype.py formula_demo_visible.docx
"""
import sys, os, traceback, time
from pathlib import Path


def check_mathtype_installed():
    """Check if MathType is registered on this machine."""
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                            r"CLSID\{0002CE03-0000-0000-C000-000000000046}"):
            pass
        return True
    except OSError:
        pass
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Equation.DSMT4"):
            pass
        return True
    except OSError:
        pass
    return False


def convert_to_mathtype(input_path, output_path=None):
    """Convert all OMML equations in a document to MathType OLE objects.

    Uses multiple methods in order of reliability:
    1. SendKeys (Alt+\) - needs visible Word window
    2. MTCommand via Word.Run
    3. Copy/Paste as OLE object

    Returns (success_count, total_count).
    """
    import pythoncom
    import win32com.client
    import win32api
    import win32con
    import win32gui

    pythoncom.CoInitialize()

    abs_input = str(Path(input_path).resolve())
    if output_path:
        abs_output = str(Path(output_path).resolve())
    else:
        abs_output = str(Path(input_path).parent /
                        (Path(input_path).stem + "_mathtype.docx"))

    word = None
    try:
        word = win32com.client.Dispatch("Word.Application",
                                        clsctx=pythoncom.CLSCTX_LOCAL_SERVER)
        word.Visible = True
        word.DisplayAlerts = 0
        print(f"Word v{word.Version} started")

        doc = word.Documents.Open(abs_input)
        n_total = doc.OMaths.Count
        print(f"Document opened: {Path(input_path).name}")
        print(f"OMML equations found: {n_total}")

        if n_total == 0:
            doc.SaveAs2(abs_output)
            doc.Close()
            print("No equations to convert. Saved as-is.")
            return (0, 0)

        converted = 0
        failed = 0

        for i in range(1, n_total + 1):
            print(f"\nEquation #{i}/{n_total}:")
            omath = doc.OMaths(i)

            success = False

            # Method A: SendKeys Alt+\
            try:
                omath.Range.Select()
                time.sleep(0.3)
                word.Selection.Copy()
                time.sleep(0.2)
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys("%\\\\")
                time.sleep(2.0)
                shell.SendKeys("{ENTER}")
                time.sleep(0.5)
                print(f"  [A] SendKeys Alt+\\ sent")
                success = True
                converted += 1
            except Exception as e:
                print(f"  [A] SendKeys failed: {e}")

            # Method B: Word.Run MTCommand
            if not success:
                try:
                    omath.Range.Select()
                    word.Run("MTCommand", "ConvertEquation")
                    time.sleep(0.5)
                    print(f"  [B] MTCommand sent")
                    success = True
                    converted += 1
                except Exception as e:
                    print(f"  [B] MTCommand failed: {e}")

            # Method C: Copy/Paste as OLE
            if not success:
                try:
                    omath.Range.Select()
                    word.Selection.Copy()
                    time.sleep(0.2)
                    omath.Range.Select()
                    word.Selection.TypeBackspace()
                    time.sleep(0.2)
                    word.Selection.Paste()
                    time.sleep(0.5)
                    print(f"  [C] Paste succeeded")
                    if doc.OMaths.Count < n_total - i + 1:
                        print(f"      (OMML count decreased)")
                    success = True
                    converted += 1
                except Exception as e:
                    print(f"  [C] Paste failed: {e}")

            if not success:
                failed += 1
                print(f"  ❌ All methods failed")

        print(f"\n{'='*40}")
        print(f"Conversion complete:")
        print(f"  Total:  {n_total}")
        print(f"  OK:     {converted}")
        print(f"  Failed: {failed}")
        print(f"  Remaining OMaths: {doc.OMaths.Count}")

        doc.SaveAs2(abs_output)
        print(f"\nSaved: {Path(abs_output).name}")

        doc.Close()
        return (converted, n_total)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return (0, 0)
    finally:
        if word:
            try:
                word.Quit()
            except Exception:
                pass
        pythoncom.CoUninitialize()


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Convert OMML equations to MathType OLE objects")
    parser.add_argument("input", nargs="?", default="formula_demo_visible.docx",
                        help="Input .docx file (default: formula_demo_visible.docx)")
    parser.add_argument("output", nargs="?", default=None,
                        help="Output .docx file (optional)")
    parser.add_argument("--check", action="store_true",
                        help="Only check if MathType is installed")

    args = parser.parse_args()

    if args.check:
        if check_mathtype_installed():
            print("MathType is installed")
        else:
            print("MathType not detected")
        return

    if not os.path.exists(args.input):
        print(f"File not found: {args.input}")
        print("Tip: Run 'py build_docx_raw.py' first to generate a demo document.")
        return

    convert_to_mathtype(args.input, args.output)


if __name__ == "__main__":
    main()
