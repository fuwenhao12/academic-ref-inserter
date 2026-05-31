"""Convert OMML formulas in a Word document to MathType OLE objects.

This script uses Word's COM API to convert OMML equations to MathType.
Requires: Microsoft Word, MathType, and pywin32 installed.

Usage:
    py convert_to_mathtype.py input.docx [output.docx]
    py convert_to_mathtype.py input.docx --check
"""
import sys, traceback
from pathlib import Path


def check_mathtype_installed():
    """Check if MathType is installed via registry."""
    import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"Equation.DSMT4")
        winreg.CloseKey(key)
        return True
    except:
        pass
    try:
        key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT,
                             r"CLSID\{0002CE03-0000-0000-C000-000000000046}")
        winreg.CloseKey(key)
        return True
    except:
        pass
    return False


def convert_to_mathtype(docx_path: str, output_path: str = None):
    """Convert all OMML formulas in a .docx to MathType OLE objects.

    Uses Word's COM API with MathType add-in commands.
    MathType for Word registers the MTCommand macro to convert equations.
    """
    try:
        import win32com.client
        import pythoncom
    except ImportError:
        print("pywin32 not installed. Run: pip install pywin32")
        return False

    if not check_mathtype_installed():
        print("MathType not detected on this machine")
        return False

    pythoncom.CoInitialize()

    abs_input = str(Path(docx_path).resolve())
    if output_path:
        abs_output = str(Path(output_path).resolve())
    else:
        abs_output = str(Path(docx_path).parent / (Path(docx_path).stem + "_mathtype.docx"))

    word = None
    try:
        word = win32com.client.Dispatch("Word.Application",
                                        clsctx=pythoncom.CLSCTX_LOCAL_SERVER)
        word.Visible = False
        word.DisplayAlerts = False
        print(f"Word started (v{word.Version})")

        doc = word.Documents.Open(abs_input)
        print(f"Opened: {Path(docx_path).name}")

        n_total = doc.OMaths.Count
        if n_total == 0:
            print("No OMML formulas found in document")
            doc.Close()
            return True

        converted = 0
        for i in range(1, n_total + 1):
            omath = doc.OMaths(i)
            omath.Range.Select()

            # Try MathType's MTCommand first
            cmd_tried = False
            for command in ["MTCommand", "MathTypeCommands.ConvertEquation",
                           "ConvertEquation"]:
                try:
                    word.Run(command, "ConvertEquation")
                    converted += 1
                    print(f"  [{converted}/{n_total}] Converted OMath #{i}")
                    cmd_tried = True
                    break
                except:
                    pass

            if not cmd_tried:
                # Try paste-special approach
                try:
                    omath.Range.Select()
                    word.Selection.Copy()
                    # Delete the OMML
                    omath.Range.Select()
                    word.Selection.TypeBackspace()
                    # Paste as MathType
                    word.Selection.Paste()
                    converted += 1
                    print(f"  [{converted}/{n_total}] Converted OMath #{i} (paste)")
                except Exception as e:
                    print(f"  [ {i} ] Convert failed: {e}")

        doc.SaveAs2(abs_output)
        print(f"\nSaved: {Path(abs_output).name}")
        print(f"Converted: {converted}/{n_total} equations")
        doc.Close()
        return True

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return False
    finally:
        if word:
            try:
                word.Quit()
            except:
                pass
            word = None
        pythoncom.CoUninitialize()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description="Convert OMML formulas to MathType equations")
    parser.add_argument("docx_path", help="Input .docx file path")
    parser.add_argument("output_path", nargs="?", default=None,
                        help="Output .docx file path (optional)")
    parser.add_argument("--check", action="store_true",
                        help="Only check if MathType is installed")

    args = parser.parse_args()

    if args.check:
        if check_mathtype_installed():
            print("MathType is installed on this machine")
        else:
            print("MathType not detected")
        sys.exit(0)

    convert_to_mathtype(args.docx_path, args.output_path)
