#!/usr/bin/env python3
"""
Academic Reference Inserter
Main entry point for inserting, formatting, and cross-referencing
academic references in Word documents.

Supports human-readable (default) and JSON (--json) output modes
for compatibility with AI coding assistants.

Usage:
    python insert_refs.py --version
    python insert_refs.py analyze --input paper.docx
    python insert_refs.py reformat --input paper.docx --format gbt7714
    python insert_refs.py reorder --input paper.docx
    python insert_refs.py hyperlink --input paper.docx
    python insert_refs.py validate --input paper.docx --format gbt7714
    python insert_refs.py fix --input paper.docx --format gbt7714 --json
"""

import os
import sys
import json
import re
import argparse

from formats.gbt7714 import GBT7714Format
from formats.ieee import IEEEFormat
from formats.apa7 import APA7Format
from formats.chicago import ChicagoFormat
from formats.mla import MLAFormat
from formats.harvard import HarvardFormat
from utils import docx_utils
from utils.parser import parse_ref, detect_type
from utils.validator import validate_all
from utils.doi_lookup import lookup_doi, lookup_by_title, format_from_doi
from utils.bibtex import parse_bibtex, export_bibtex

__version__ = "1.0.0"


FORMATS = {
    'gbt7714': GBT7714Format(),
    'ieee': IEEEFormat(),
    'apa7': APA7Format(),
    'chicago': ChicagoFormat(),
    'mla': MLAFormat(),
    'harvard': HarvardFormat(),
}


def _get_format(name):
    fmt = FORMATS.get(name.lower())
    if not fmt:
        raise ValueError(f"Unsupported format: {name}. Available: {', '.join(FORMATS.keys())}")
    return fmt


def _emit(result, args):
    """Output result: human-readable if no --json, JSON otherwise."""
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif 'message' in result:
        print(result['message'])


def _save_doc(doc, args):
    """Save document to --output if specified, otherwise overwrite --input."""
    target = args.output if args.output else args.input
    doc.save(target)
    return target


def _analysis_to_json(args, doc, ref_title_idx, ref_entries, citation_order):
    """Build structured analysis result."""
    ref_nums = {num for _, _, num in ref_entries}
    cited_nums = set(citation_order)
    max_ref = max(ref_nums) if ref_nums else (max(citation_order) if citation_order else 0)
    expected = list(range(1, max_ref + 1)) if max_ref > 0 else []
    orphan = sorted(ref_nums - cited_nums)
    missing = sorted(cited_nums - ref_nums)

    ref_list = []
    for idx, para, num in sorted(ref_entries, key=lambda x: x[2]):
        text = para.text.strip()
        ctx = docx_utils.extract_citation_context(doc, num)
        ref_list.append({
            'number': num,
            'type': detect_type(text),
            'text': text,
            'context_snippet': ctx,
        })

    return {
        'command': 'analyze',
        'input_file': args.input,
        'ref_section_paragraph': ref_title_idx,
        'total_refs': len(ref_entries),
        'citation_order': citation_order,
        'sequential_ok': citation_order == expected,
        'expected_sequential': expected,
        'references': ref_list,
        'orphan_refs': orphan,
        'missing_refs': missing,
        'has_orphan': len(orphan) > 0,
        'has_missing': len(missing) > 0,
        'file_ok': len(orphan) == 0 and len(missing) == 0,
    }


def cmd_analyze(args):
    """Analyze document: extract citations, references, and detect issues."""
    doc = docx_utils.open_docx(args.input)
    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)
    citation_order = docx_utils.extract_citations_from_text(doc)

    result = _analysis_to_json(args, doc, ref_title_idx, ref_entries, citation_order)
    result['message'] = (
        f"Document: {args.input}\n"
        f"Reference section at P{ref_title_idx}\n"
        f"Total refs: {len(ref_entries)}\n"
        f"Citation order: {' -> '.join(str(n) for n in citation_order)}\n"
        f"Sequential: {'OK' if result['sequential_ok'] else 'NEEDS REORDER'}\n"
        f"Orphan refs: {result['orphan_refs'] or 'none'}\n"
        f"Missing refs: {result['missing_refs'] or 'none'}"
    )
    _emit(result, args)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


def cmd_reformat(args):
    """Reformat all reference entries to the target citation style."""
    fmt = _get_format(args.format)
    doc = docx_utils.open_docx(args.input)
    backup_path = docx_utils.backup_docx(args.input)

    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)
    changes = []

    for idx, para, num in ref_entries:
        raw_text = para.text.strip()
        parsed = parse_ref(raw_text)
        new_ref = fmt.format(parsed)
        new_ref = f"[{num}] {new_ref}"

        if new_ref != raw_text:
            docx_utils.update_reference_text(para, new_ref)
            changes.append({'number': num, 'old': raw_text[:80], 'new': new_ref[:80]})

    _save_doc(doc, args)
    result = {
        'command': 'reformat',
        'input_file': args.input,
        'backup_file': backup_path,
        'format': args.format,
        'total_entries': len(ref_entries),
        'changes': len(changes),
        'messages': [f"[{c['number']}] reformatted" for c in changes],
    }
    result['message'] = f"Reformatted {len(changes)}/{len(ref_entries)} entries to {fmt.name}"
    _emit(result, args)


def cmd_reorder(args):
    """Reorder references to match first citation order in text."""
    doc = docx_utils.open_docx(args.input)
    backup_path = docx_utils.backup_docx(args.input)

    citation_order = docx_utils.extract_citations_from_text(doc)
    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)

    if not ref_entries:
        result = {'command': 'reorder', 'error': 'No references found'}
        _emit(result, args)
        return

    old_to_new = {}
    for new_num, old_num in enumerate(citation_order, 1):
        old_to_new[old_num] = new_num

    # Update bib entries
    bib_changes = 0
    for idx, para, old_num in ref_entries:
        new_num = old_to_new.get(old_num, old_num)
        raw_text = para.text.strip()
        new_text = re.sub(r'^\[\d+\]', f'[{new_num}]', raw_text)
        if new_text != raw_text:
            docx_utils.update_reference_text(para, new_text)
            bib_changes += 1

    # Update in-text citations
    text_changes = 0
    for para in doc.paragraphs:
        text = para.text
        for old_num, new_num in old_to_new.items():
            if old_num == new_num:
                continue
            if f'[{old_num}]' in text:
                for run in para.runs:
                    if f'[{old_num}]' in run.text:
                        run.text = run.text.replace(f'[{old_num}]', f'[{new_num}]')
                        text_changes += 1

    _save_doc(doc, args)

    mapping = {str(k): str(v) for k, v in old_to_new.items() if k != v}
    result = {
        'command': 'reorder',
        'input_file': args.input,
        'backup_file': backup_path,
        'bib_entries_updated': bib_changes,
        'in_text_updated': text_changes,
        'renumbering_mapping': mapping,
    }
    result['message'] = f"Updated {bib_changes} bib entries, {text_changes} in-text citations"
    _emit(result, args)


def cmd_hyperlink(args):
    """Add bookmarks and hyperlinks from citations to bibliography entries."""
    doc = docx_utils.open_docx(args.input)
    backup_path = docx_utils.backup_docx(args.input)

    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)

    bookmarks = 0
    for idx, para, num in ref_entries:
        if docx_utils.add_bookmark_to_paragraph(para, f"Ref_{num}"):
            bookmarks += 1

    hyperlinks = 0
    for para in doc.paragraphs:
        refs = re.findall(r'\[(\d+)\]', para.text)
        if not refs:
            continue
        for ref_num in sorted(set(int(r) for r in refs), reverse=True):
            if docx_utils.replace_citation_with_hyperlink(para, ref_num):
                hyperlinks += 1

    _save_doc(doc, args)
    result = {
        'command': 'hyperlink',
        'input_file': args.input,
        'backup_file': backup_path,
        'bookmarks_added': bookmarks,
        'hyperlinks_created': hyperlinks,
        'total_refs': len(ref_entries),
    }
    result['message'] = f"Bookmarks: {bookmarks}, Hyperlinks: {hyperlinks}"
    _emit(result, args)


def cmd_validate(args):
    """Validate reference consistency and format."""
    fmt = _get_format(args.format) if args.format else None
    doc = docx_utils.open_docx(args.input)

    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)
    citation_order = docx_utils.extract_citations_from_text(doc)

    ref_texts = [para.text.strip() for _, para, _ in ref_entries]
    ref_nums = {num for _, _, num in ref_entries}
    cited_nums = set(citation_order)
    years = []

    for rt in ref_texts:
        parsed = parse_ref(rt)
        years.append(parsed.get('year', ''))

    style_name = fmt.name if fmt else 'gbt7714'
    report = validate_all(ref_texts, cited_nums, ref_nums, years, style=style_name)

    issues_detail = []
    for issue in report.get('issues', []):
        issues_detail.append({'severity': 'error', 'text': issue})
    for warning in report.get('warnings', []):
        issues_detail.append({'severity': 'warning', 'text': warning})

    result = {
        'command': 'validate',
        'input_file': args.input,
        'format': style_name,
        'total_refs': report['total_refs'],
        'passed': report['passed'],
        'issues': issues_detail,
        'recency': None,
    }

    if report.get('recency'):
        result['recency'] = {
            'recent_count': report['recency']['recent_count'],
            'total': report['recency']['total'],
            'ratio': round(report['recency']['ratio'], 2),
            'threshold_ok': report['recency']['ok'],
        }

    summary = f"Validation ({style_name}): {'PASSED' if report['passed'] else 'FAILED'}\n"
    for issue in issues_detail:
        summary += f"  [{issue['severity'].upper()}] {issue['text']}\n"
    result['message'] = summary.strip()
    _emit(result, args)

    if not report['passed'] and not args.json:
        sys.exit(1)
    elif not report['passed'] and args.json:
        result['exit_code'] = 1


def cmd_fix(args):
    """Full pipeline: analyze + reformat + reorder + hyperlink + validate."""
    fmt = _get_format(args.format)
    backup_path = docx_utils.backup_docx(args.input)

    steps = []

    # Step 1: Analyze
    doc = docx_utils.open_docx(args.input)
    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)
    citation_order = docx_utils.extract_citations_from_text(doc)
    analysis = _analysis_to_json(args, doc, ref_title_idx, ref_entries, citation_order)
    steps.append({'step': 'analyze', 'total_refs': analysis['total_refs']})

    # Step 2: Reformat
    for idx, para, num in ref_entries:
        raw_text = para.text.strip()
        parsed = parse_ref(raw_text)
        new_ref = fmt.format(parsed)
        new_ref = f"[{num}] {new_ref}"
        if new_ref != raw_text:
            docx_utils.update_reference_text(para, new_ref)
    _save_doc(doc, args)
    steps.append({'step': 'reformat', 'format': args.format})

    # Step 3: Reorder (if needed)
    if not analysis['sequential_ok']:
        old_to_new = {}
        for new_num, old_num in enumerate(citation_order, 1):
            old_to_new[old_num] = new_num
        doc = docx_utils.open_docx(args.input)
        for idx, para, old_num in ref_entries:
            new_num = old_to_new.get(old_num, old_num)
            raw_text = para.text.strip()
            new_text = re.sub(r'^\[\d+\]', f'[{new_num}]', raw_text)
            if new_text != raw_text:
                docx_utils.update_reference_text(para, new_text)
        for para in doc.paragraphs:
            for old_num, new_num in old_to_new.items():
                if old_num == new_num:
                    continue
                if f'[{old_num}]' in para.text:
                    for run in para.runs:
                        if f'[{old_num}]' in run.text:
                            run.text = run.text.replace(f'[{old_num}]', f'[{new_num}]')
        _save_doc(doc, args)
        steps.append({'step': 'reorder', 'mapping': {str(k): str(v) for k, v in old_to_new.items() if k != v}})

    # Step 4: Hyperlinks
    doc = docx_utils.open_docx(args.input)
    ref_title_idx, ref_entries = docx_utils.extract_reference_section(doc)
    for idx, para, num in ref_entries:
        docx_utils.add_bookmark_to_paragraph(para, f"Ref_{num}")
    hyperlinks = 0
    for para in doc.paragraphs:
        refs = re.findall(r'\[(\d+)\]', para.text)
        if not refs:
            continue
        for ref_num in sorted(set(int(r) for r in refs), reverse=True):
            if docx_utils.replace_citation_with_hyperlink(para, ref_num):
                hyperlinks += 1
    _save_doc(doc, args)
    steps.append({'step': 'hyperlink', 'hyperlinks_created': hyperlinks})

    # Step 5: Validate
    ref_texts = [para.text.strip() for _, para, _ in ref_entries]
    ref_nums = {num for _, _, num in ref_entries}
    years = []
    for rt in ref_texts:
        parsed = parse_ref(rt)
        years.append(parsed.get('year', ''))
    report = validate_all(ref_texts, ref_nums, set(citation_order), years, style=fmt.name)
    steps.append({'step': 'validate', 'passed': report['passed']})

    result = {
        'command': 'fix',
        'input_file': args.input,
        'backup_file': backup_path,
        'format': args.format,
        'format_name': fmt.name,
        'steps': steps,
        'passed': report['passed'],
        'validation': {
            'total_refs': report['total_refs'],
            'issues': [i for i in report.get('issues', [])],
            'warnings': [w for w in report.get('warnings', [])],
        },
    }

    summary_lines = [
        f"Academic Ref Inserter - Full Pipeline ({fmt.name})",
        f"  [1/5] Analyze: {analysis['total_refs']} refs found",
        f"  [2/5] Reformat: {args.format}",
        f"  [3/5] Reorder: {'done' if not analysis['sequential_ok'] else 'skipped (already sequential)'}",
        f"  [4/5] Hyperlinks: {hyperlinks} created",
        f"  [5/5] Validate: {'PASSED' if report['passed'] else 'FAILED'}",
        f"  Backup: {backup_path}",
    ]
    result['message'] = '\n'.join(summary_lines)
    _emit(result, args)

    if not report['passed'] and not args.json:
        sys.exit(1)


def cmd_generate(args):
    """Generate a formatted reference from DOI, title search, or BibTeX input."""
    if args.doi:
        doi = args.doi.strip()
        formatted = format_from_doi(doi, args.format)
        if formatted:
            result = {'command': 'generate', 'source': 'doi', 'doi': doi, 'formatted': formatted}
            result['message'] = formatted
            _emit(result, args)
        else:
            err = {'error': f'Failed to look up DOI: {doi}'}
            print(json.dumps(err) if args.json else err['error'])
            sys.exit(1)
    elif args.search:
        results = lookup_by_title(args.search, max_results=5)
        if results:
            fmt = _get_format(args.format)
            formatted_list = []
            for r in results:
                formatted_list.append({
                    'doi': r.get('doi', ''),
                    'title': r.get('title', '')[:80],
                    'authors': ', '.join(r.get('authors', [])[:3]),
                    'year': r.get('year', ''),
                    'formatted': fmt.format(r),
                })
            result = {
                'command': 'generate',
                'source': 'search',
                'query': args.search,
                'results': formatted_list,
            }
            msg = '\n'.join(f"  [{i+1}] {r['formatted']}" for i, r in enumerate(formatted_list))
            result['message'] = f"Search: {args.search}\n{msg}"
            _emit(result, args)
        else:
            err = {'error': f'No results for: {args.search}'}
            print(json.dumps(err) if args.json else err['error'])
            sys.exit(1)
    else:
        err = {'error': 'Specify --doi or --search'}
        print(json.dumps(err) if args.json else err['error'])
        sys.exit(1)


def cmd_bib(args):
    """Import from or export to BibTeX format."""
    if args.import_file:
        with open(args.import_file, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        entries = parse_bibtex(bib_content)
        fmt = _get_format(args.format)
        formatted = []
        for entry in entries:
            formatted.append(fmt.format(entry))
        result = {
            'command': 'bib',
            'action': 'import',
            'source': args.import_file,
            'total_entries': len(entries),
            'formatted': formatted,
        }
        msg = '\n'.join(f"[{i+1}] {r}" for i, r in enumerate(formatted))
        result['message'] = f"Imported {len(entries)} entries from {args.import_file}:\n{msg}"
        _emit(result, args)
    elif args.export_input:
        doc = docx_utils.open_docx(args.export_input)
        _, ref_entries = docx_utils.extract_reference_section(doc)
        refs = []
        for _, para, num in ref_entries:
            parsed = parse_ref(para.text.strip())
            parsed['key'] = f"ref{num}"
            refs.append(parsed)
        bib_output = export_bibtex(refs)
        if args.export_output:
            with open(args.export_output, 'w', encoding='utf-8') as f:
                f.write(bib_output)
        result = {
            'command': 'bib',
            'action': 'export',
            'source': args.export_input,
            'total_entries': len(refs),
            'bibtex': bib_output,
        }
        result['message'] = bib_output if not args.json else f"Exported {len(refs)} entries"
        _emit(result, args)
    else:
        err = {'error': 'Specify --import or --export-input'}
        print(json.dumps(err) if args.json else err['error'])
        sys.exit(1)


def cmd_interactive(args):
    """Interactive reference management console."""
    print(f"\nAcademic Ref Inserter v{__version__} - Interactive Mode")
    print("=" * 50)
    print("Commands: analyze | fix | generate | bib | formats | validate | help | quit")
    print("")

    while True:
        try:
            cmd_line = input("ref> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not cmd_line:
            continue
        if cmd_line.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        if cmd_line.lower() in ('help', 'h', '?'):
            _print_interactive_help()
            continue
        if cmd_line.lower() in ('formats', 'fmts'):
            _print_formats()
            continue

        _handle_interactive_command(cmd_line)


def _print_interactive_help():
    print("""
Interactive Commands:
  analyze <file.docx>        Analyze citation structure
  fix <file.docx> <format>   Full pipeline (analysis -> reformat -> reorder -> hyperlink -> validate)
  validate <file.docx> [fmt] Validate references
  generate doi <DOI> <fmt>   Generate reference from DOI
  generate search <title> <fmt>  Search by title
  bib import <file.bib> <fmt>    Import from BibTeX
  bib export <file.docx> [out]  Export to BibTeX
  formats                    List available formats
  help                       Show this help
  quit                       Exit

Examples:
  ref> analyze paper.docx
  ref> fix paper.docx gbt7714
  ref> generate doi 10.1038/nature14539 ieee
  ref> formats
""")


def _print_formats():
    print("\nAvailable formats:")
    for key, fmt in FORMATS.items():
        print(f"  {key:12} {fmt.name:20} ordering: {fmt.ordering}")
    print("")


def _handle_interactive_command(cmd_line):
    parts = cmd_line.split()
    cmd = parts[0].lower()

    if cmd == 'analyze' and len(parts) >= 2:
        class A:
            pass
        a = A()
        a.input = parts[1]
        a.output = None
        a.json = False
        a.format = 'gbt7714'
        try:
            cmd_analyze(a)
        except Exception as e:
            print(f"Error: {e}")
    elif cmd == 'fix' and len(parts) >= 3:
        class A:
            pass
        a = A()
        a.input = parts[1]
        a.output = None
        a.json = False
        a.format = parts[2]
        try:
            cmd_fix(a)
        except Exception as e:
            print(f"Error: {e}")
    elif cmd == 'validate' and len(parts) >= 2:
        class A:
            pass
        a = A()
        a.input = parts[1]
        a.output = None
        a.json = False
        a.format = parts[2] if len(parts) >= 3 else 'gbt7714'
        try:
            cmd_validate(a)
        except Exception as e:
            print(f"Error: {e}")
    elif cmd == 'generate' and len(parts) >= 4:
        if parts[1] == 'doi':
            class A:
                pass
            a = A()
            a.doi = parts[2]
            a.format = parts[3]
            a.search = None
            a.json = False
            try:
                cmd_generate(a)
            except Exception as e:
                print(f"Error: {e}")
        elif parts[1] == 'search':
            class A:
                pass
            a = A()
            a.doi = None
            a.search = ' '.join(parts[2:])
            a.format = 'gbt7714'
            a.json = False
            try:
                cmd_generate(a)
            except Exception as e:
                print(f"Error: {e}")
    elif cmd == 'bib' and len(parts) >= 3:
        class A:
            pass
        a = A()
        a.json = False
        a.format = 'gbt7714'
        if parts[1] == 'import' and len(parts) >= 4:
            a.import_file = parts[2]
            a.format = parts[3]
            a.export_input = None
            a.export_output = None
            try:
                cmd_bib(a)
            except Exception as e:
                print(f"Error: {e}")
        elif parts[1] == 'export' and len(parts) >= 3:
            a.import_file = None
            a.export_input = parts[2]
            a.export_output = parts[3] if len(parts) >= 4 else None
            try:
                cmd_bib(a)
            except Exception as e:
                print(f"Error: {e}")
    else:
        print(f"Unknown command: {cmd}. Type 'help' for available commands.")


def main():
    parser = argparse.ArgumentParser(
        description='Academic Reference Inserter - format, reorder, and hyperlink references'
    )
    parser.add_argument('--version', '-V', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument('--input', '-i', required=True, help='Input .docx file')
    parser.add_argument('--output', '-o', help='Output .docx file (default: overwrite input, safe with --output)')
    parser.add_argument('--format', '-f', choices=list(FORMATS.keys()), help='Citation format')
    parser.add_argument('--json', action='store_true', help='Output JSON for AI agent consumption')

    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('analyze', help='Analyze citation structure')
    sub.add_parser('reformat', help='Reformat references to target style')
    sub.add_parser('reorder', help='Reorder references to match citation order')
    sub.add_parser('hyperlink', help='Add cross-reference hyperlinks')
    sub.add_parser('validate', help='Validate references')
    sub.add_parser('fix', help='Full pipeline: all steps')
    sub_gen = sub.add_parser('generate', help='Generate reference from DOI or title search')
    sub_gen.add_argument('--doi', help='DOI string to look up')
    sub_gen.add_argument('--search', help='Search by title')
    sub_bib = sub.add_parser('bib', help='Import/export BibTeX')
    sub_bib.add_argument('--import', dest='import_file', help='Import from .bib file')
    sub_bib.add_argument('--export-input', help='Export from .docx to BibTeX')
    sub_bib.add_argument('--export-output', help='Output .bib file path')
    sub.add_parser('interactive', help='Interactive reference management console')

    args = parser.parse_args()

    if args.command in ('generate', 'bib', 'interactive'):
        try:
            commands = {
                'generate': cmd_generate,
                'bib': cmd_bib,
                'interactive': cmd_interactive,
            }
            commands[args.command](args)
        except Exception as e:
            err = {'error': str(e)}
            print(json.dumps(err, ensure_ascii=False) if args.json else str(e))
            sys.exit(1)
        return

    if not os.path.exists(args.input):
        err = {'error': f'File not found: {args.input}'}
        print(json.dumps(err) if args.json else err['error'])
        sys.exit(1)

    if not args.input.lower().endswith('.docx'):
        err = {'error': f'File must be .docx format: {args.input}'}
        print(json.dumps(err) if args.json else err['error'])
        sys.exit(1)

    try:
        commands = {
            'analyze': cmd_analyze,
            'reformat': cmd_reformat,
            'reorder': cmd_reorder,
            'hyperlink': cmd_hyperlink,
            'validate': cmd_validate,
            'fix': cmd_fix,
            'generate': cmd_generate,
            'bib': cmd_bib,
        }
        commands[args.command](args)
    except ValueError as e:
        err = {'error': str(e)}
        print(json.dumps(err, ensure_ascii=False) if args.json else str(e))
        sys.exit(1)
    except Exception as e:
        err = {
            'error': str(e),
            'hint': 'Ensure the file is a valid .docx document and try again.'
        }
        print(json.dumps(err, ensure_ascii=False) if args.json else str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
