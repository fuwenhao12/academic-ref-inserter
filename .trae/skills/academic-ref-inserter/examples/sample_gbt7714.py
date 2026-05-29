"""GB/T 7714-2015 Example: Insert and format references for Chinese journal submission."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from insert_refs import cmd_analyze, cmd_reformat, cmd_reorder, cmd_hyperlink, cmd_validate


class Args:
    pass


def run_gbt7714_pipeline(docx_path: str):
    """Run full GB/T 7714 pipeline on a docx file."""
    print(f"\n{'='*60}")
    print(f"GB/T 7714-2015 Pipeline: {docx_path}")
    print(f"{'='*60}")

    # Step 1: Analyze
    args = Args()
    args.input = docx_path
    args.output = None
    args.json = False
    cmd_analyze(args)

    # Step 2: Reformat
    args = Args()
    args.input = docx_path
    args.output = None
    args.format = 'gbt7714'
    args.json = False
    cmd_reformat(args)

    # Step 3: Reorder
    args = Args()
    args.input = docx_path
    args.output = None
    args.json = False
    cmd_reorder(args)

    # Step 4: Hyperlink
    args = Args()
    args.input = docx_path
    args.output = None
    args.json = False
    cmd_hyperlink(args)

    # Step 5: Validate
    args = Args()
    args.input = docx_path
    args.output = None
    args.format = 'gbt7714'
    args.json = False
    cmd_validate(args)

    print(f"\nDone! Open {docx_path} and Ctrl+Click on [N] citations to jump to references.")


if __name__ == '__main__':
    print("Usage: python sample_gbt7714.py")
    print("Replace 'your_paper.docx' with the path to your paper.")
    print()

    import glob
    candidates = glob.glob("*.docx")
    if candidates:
        print(f"Found .docx files in current directory: {candidates}")
        print("Update the run_gbt7714_pipeline() call below with your file path.")
    else:
        print("No .docx files found in current directory. Please provide a path.")
