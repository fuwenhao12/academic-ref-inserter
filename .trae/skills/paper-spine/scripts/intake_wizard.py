#!/usr/bin/env python3
"""Create PaperSpine configuration from an interactive terminal wizard."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import textwrap
from dataclasses import asdict, dataclass
from pathlib import Path


WORKFLOWS = ("rewrite_existing", "build_from_materials")
SCENES = ("journal", "conference", "report_review", "competition")
TIERS = ("flash", "pro")
LANGUAGES = ("en", "zh")
UI_LANGUAGES = ("zh", "en")
WORD_OUTPUTS = ("none", "docx")
TRANSLATION_PACKAGES = ("none", "zh")
GLOBAL_CONFIG_ENV = "PAPERSPINE_CONFIG_HOME"

CHOICE_FIELDS = {
    "workflow": WORKFLOWS,
    "scene": SCENES,
    "tier": TIERS,
    "output_language": LANGUAGES,
    "word_output": WORD_OUTPUTS,
    "translation_package": TRANSLATION_PACKAGES,
    "ui_language": UI_LANGUAGES,
}

FIELD_ORDER = (
    "workflow",
    "scene",
    "tier",
    "output_language",
    "word_output",
    "translation_package",
    "target_name",
    "draft_path",
    "materials_dir",
    "user_motivation",
    "official_urls",
    "special_requirements",
    "ui_language",
)

CHOICE_HELP = {
    "workflow": {
        "rewrite_existing": ("改进已有初稿", "Improve an existing draft"),
        "build_from_materials": ("从素材文件夹从零构筑", "Build from a materials folder"),
    },
    "scene": {
        "journal": ("期刊论文", "Journal paper"),
        "conference": ("会议论文", "Conference paper"),
        "report_review": ("课程报告、技术报告或综述", "Report, technical report, or review"),
        "competition": ("竞赛论文或竞赛报告", "Competition paper or report"),
    },
    "tier": {
        "flash": ("轻量调研：3+3 篇样例加官方要求", "Light research: 3+3 examples plus official requirements"),
        "pro": ("深度调研：6+6 篇样例加官方要求", "Deep research: 6+6 examples plus official requirements"),
    },
    "output_language": {
        "en": ("英文最终稿", "English final output"),
        "zh": ("中文最终稿", "Chinese final output"),
    },
    "word_output": {
        "none": ("不额外生成 Word", "Do not generate Word"),
        "docx": ("生成并检查 Word 文件", "Generate and check DOCX"),
    },
    "translation_package": {
        "none": ("不翻译", "Do not translate"),
        "zh": ("生成完整中文翻译包", "Generate complete Chinese translation package"),
    },
    "ui_language": {
        "zh": ("中文界面", "Chinese interface"),
        "en": ("English UI", "English interface"),
    },
}

LABELS = {
    "zh": {
        "banner": "PaperSpine 配置向导",
        "welcome": "Welcome back!",
        "tagline": "动机驱动的论文/报告 Skill Suite",
        "flowline": "先学习目标场景，再确认动机，最后构筑可审计的 LaTeX 成果",
        "why_1": "我们做 PaperSpine，是为了让 AI 先学习，再写作。",
        "why_2": "不是把论文润色得更长，而是把动机、证据与结构连成一条清晰主线。",
        "why_3": "它面向论文、报告与竞赛写作：调研目标场景，学习优秀样例，再逐段生成。",
        "continue": "按任意键进入配置",
        "workflow": "工作流",
        "scene": "目标场景",
        "tier": "调研深度",
        "output_language": "最终输出语言",
        "word_output": "Word 版本",
        "translation_package": "生成英文产物后是否翻译",
        "ui_language": "界面语言",
        "target_name": "目标名称",
        "draft_path": "初稿路径",
        "materials_dir": "素材文件夹路径",
        "user_motivation": "初始动机假设",
        "official_urls": "官方链接",
        "special_requirements": "特殊要求",
        "review": "检查配置",
        "confirm": "确认写入配置",
        "edit": "输入要修改的字段编号，或直接回车完成",
        "invalid": "输入无效，请重新选择。",
        "wrote": "已写入",
        "keyboard_help": "←/→ 切换选项；↑/↓ 切换字段；Enter 编辑/确认；S 保存；Q 退出",
        "text_help": "输入新内容。列表字段可用分号分隔。直接回车保留当前值。",
        "save": "保存并退出",
        "quit": "退出但不保存",
        "auto": "自动读取",
        "enter_edit": "Enter 修改",
        "empty": "空",
    },
    "en": {
        "banner": "PaperSpine Configuration Wizard",
        "welcome": "Welcome back!",
        "tagline": "Motivation-driven paper/report skill suite",
        "flowline": "Learn the target scene, confirm motivation, then build auditable LaTeX",
        "why_1": "PaperSpine exists so AI learns before it writes.",
        "why_2": "It does not make papers longer; it connects motivation, evidence, and structure.",
        "why_3": "For papers, reports, and competitions: research the scene, learn strong examples, then draft unit by unit.",
        "continue": "Press any key to configure",
        "workflow": "Workflow",
        "scene": "Target scene",
        "tier": "Research tier",
        "output_language": "Final output language",
        "word_output": "Word output",
        "translation_package": "Translate after English output",
        "ui_language": "UI language",
        "target_name": "Target name",
        "draft_path": "Draft path",
        "materials_dir": "Materials directory",
        "user_motivation": "Initial motivation hypothesis",
        "official_urls": "Official URLs",
        "special_requirements": "Special requirements",
        "review": "Review configuration",
        "confirm": "Write config",
        "edit": "Enter field number to edit, or press Enter to finish",
        "invalid": "Invalid input. Please choose again.",
        "wrote": "Wrote",
        "keyboard_help": "Left/Right: option; Up/Down: field; Enter: edit/confirm; S: save; Q: quit",
        "text_help": "Enter a new value. Separate list fields with semicolons. Press Enter to keep current.",
        "save": "Save and exit",
        "quit": "Exit without saving",
        "auto": "Auto-read",
        "enter_edit": "Enter to edit",
        "empty": "empty",
    },
}


@dataclass
class PaperSpineConfig:
    workflow: str
    scene: str
    tier: str
    output_language: str
    target_name: str
    materials_dir: str
    draft_path: str
    user_motivation: str
    official_urls: list[str]
    special_requirements: list[str]
    word_output: str
    translation_package: str
    ui_language: str


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
URL_RE = re.compile(r"https?://[^\s)>\]]+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create PaperSpine config files.")
    parser.add_argument("--output-dir", default="paper_rewriting_output")
    parser.add_argument("--workflow", choices=WORKFLOWS)
    parser.add_argument("--scene", choices=SCENES)
    parser.add_argument("--tier", choices=TIERS)
    parser.add_argument("--output-language", choices=LANGUAGES)
    parser.add_argument("--ui-language", choices=UI_LANGUAGES)
    parser.add_argument("--word-output", choices=WORD_OUTPUTS, default="none")
    parser.add_argument("--translation-package", choices=TRANSLATION_PACKAGES, default="none")
    parser.add_argument("--target-name", default="")
    parser.add_argument("--materials-dir", default="")
    parser.add_argument("--draft-path", default="")
    parser.add_argument("--user-motivation", default="")
    parser.add_argument("--official-url", action="append", default=[])
    parser.add_argument("--special-requirement", action="append", default=[])
    parser.add_argument("--setup-global", action="store_true", help="Choose and save global PaperSpine UI preferences.")
    parser.add_argument("--no-interactive", action="store_true")
    parser.add_argument("--keyboard-ui", action="store_true", help="Use arrow-key terminal UI when a real Windows terminal is available.")
    parser.add_argument("--classic-input", action="store_true", help="Force numbered prompt input.")
    return parser.parse_args()


def global_config_path() -> Path:
    base = os.environ.get(GLOBAL_CONFIG_ENV)
    if base:
        return Path(base) / "config.json"
    return Path.home() / ".paperspine" / "config.json"


def load_global_config() -> dict[str, str]:
    path = global_config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_global_config(data: dict[str, str]) -> None:
    path = global_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def tr(ui_language: str, key: str) -> str:
    return LABELS.get(ui_language, LABELS["zh"]).get(key, key)


def configure_windows_console() -> None:
    if os.name != "nt" or not sys.stdout.isatty():
        return
    try:
        os.system("chcp 65001 > nul")
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def help_text(key: str, value: str, ui_language: str) -> str:
    zh_help, en_help = CHOICE_HELP.get(key, {}).get(value, ("", ""))
    return zh_help if ui_language == "zh" else en_help


def ansi(text: str, code: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"


def visible_len(text: str) -> int:
    return len(ANSI_RE.sub("", text))


def crop_plain(text: str, width: int) -> str:
    if width <= 1:
        return ""
    return text if len(text) <= width else text[: max(0, width - 1)] + "…"


def pad_ansi(text: str, width: int, align: str = "center") -> str:
    length = visible_len(text)
    if length > width:
        plain = ANSI_RE.sub("", text)
        text = crop_plain(plain, width)
        length = visible_len(text)
    gap = max(0, width - length)
    if align == "left":
        return text + " " * gap
    if align == "right":
        return " " * gap + text
    left = gap // 2
    return " " * left + text + " " * (gap - left)


def term_width(default: int = 118) -> int:
    return max(96, shutil.get_terminal_size((default, 36)).columns)


def safe_input(prompt: str = "> ") -> str:
    try:
        return input(prompt).strip()
    except EOFError:
        return ""


def read_key() -> str:
    import msvcrt

    ch = msvcrt.getwch()
    if ch in ("\x00", "\xe0"):
        code = msvcrt.getwch()
        return {"H": "up", "P": "down", "K": "left", "M": "right"}.get(code, "")
    if ch in ("\r", "\n"):
        return "enter"
    if ch in ("s", "S"):
        return "save"
    if ch in ("q", "Q", "\x1b"):
        return "quit"
    return ch


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(ui_language: str) -> None:
    title = tr(ui_language, "banner")
    line = "=" * max(48, len(title) + 8)
    print(f"\n{line}\n  {title}\n{line}")


def print_centered_box(lines: list[str], width: int, accent: str = "38;5;208") -> None:
    print(ansi("╭" + "─" * (width - 2) + "╮", accent))
    for line in lines:
        print(ansi("│", accent) + pad_ansi(line, width - 2) + ansi("│", accent))
    print(ansi("╰" + "─" * (width - 2) + "╯", accent))


def print_welcome_screen(ui_language: str, wait: bool = False) -> None:
    if not sys.stdout.isatty():
        print("PaperSpine v2")
        print(tr(ui_language, "welcome"))
        print(tr(ui_language, "flowline"))
        return
    if wait:
        clear_screen()
    width = min(term_width(), 122)
    accent = "38;5;208"
    white = "1;97"
    muted = "90"
    mountain = [
        "                 /\\                         /\\                 ",
        "        /\\      /  \\        /\\      /\\     /  \\       /\\       ",
        "   /\\  /  \\    /    \\  /\\  /  \\    /  \\   /    \\  /\\  /  \\     ",
        "__/  \\/    \\__/      \\/  \\/    \\__/    \\_/      \\/  \\/    \\__",
    ]
    title = [
        "██████╗  █████╗ ██████╗ ███████╗██████╗ ███████╗██████╗ ██╗███╗   ██╗███████╗",
        "██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔════╝██╔══██╗██║████╗  ██║██╔════╝",
        "██████╔╝███████║██████╔╝█████╗  ██████╔╝███████╗██████╔╝██║██╔██╗ ██║█████╗  ",
        "██╔═══╝ ██╔══██║██╔═══╝ ██╔══╝  ██╔══██╗╚════██║██╔═══╝ ██║██║╚██╗██║██╔══╝  ",
        "██║     ██║  ██║██║     ███████╗██║  ██║███████║██║     ██║██║ ╚████║███████╗",
        "╚═╝     ╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝",
    ]
    lines: list[str] = [
        ansi("PaperSpine v2", accent),
        "",
        ansi(tr(ui_language, "welcome"), white),
        "",
    ]
    lines.extend(ansi(line, white) for line in mountain)
    lines.append("")
    lines.extend(ansi(line, white) for line in title)
    lines.extend(
        [
            "",
            ansi(tr(ui_language, "tagline"), white),
            ansi(tr(ui_language, "flowline"), muted),
            "",
            tr(ui_language, "why_1"),
            tr(ui_language, "why_2"),
            tr(ui_language, "why_3"),
            "",
            ansi("𝕏  X: Wbingo353332", muted),
            ansi("♪  抖音: 91362158854", muted),
            ansi("▣  小红书: 4770513150", muted),
        ]
    )
    print_centered_box(lines, width, accent=accent)
    if wait:
        print()
        print(pad_ansi(ansi(tr(ui_language, "continue"), muted), width))
        read_key()


def choose(key: str, values: tuple[str, ...], ui_language: str, default: str | None = None) -> str:
    default = default or values[0]
    print(f"\n{tr(ui_language, key)}")
    for index, value in enumerate(values, start=1):
        suffix = " [default]" if value == default else ""
        description = help_text(key, value, ui_language)
        description = f" - {description}" if description else ""
        print(f"  {index}. {value}{suffix}{description}")
    while True:
        answer = safe_input("> ")
        if not answer:
            return default
        if answer.isdigit():
            idx = int(answer)
            if 1 <= idx <= len(values):
                return values[idx - 1]
        if answer in values:
            return answer
        print(tr(ui_language, "invalid"))


def ask_text(key: str, ui_language: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = safe_input(f"{tr(ui_language, key)}{suffix}: ")
    return answer or default


def split_items(value: str) -> list[str]:
    if not value:
        return []
    raw = value.replace("\n", ";").replace(",", ";").split(";")
    return [item.strip() for item in raw if item.strip()]


def default_language(scene: str) -> str:
    if scene in {"journal", "conference"}:
        return "en"
    return "zh"


def display_config(config: PaperSpineConfig) -> list[str]:
    data = asdict(config)
    keys = list(data)
    print("\n" + "-" * 72)
    for index, key in enumerate(keys, start=1):
        value = data[key]
        rendered = ", ".join(value) if isinstance(value, list) else value
        print(f"{index:>2}. {key}: {rendered}")
    print("-" * 72)
    return keys


def edit_config(config: PaperSpineConfig) -> PaperSpineConfig:
    while True:
        print(f"\n{tr(config.ui_language, 'review')}")
        keys = display_config(config)
        answer = safe_input(f"{tr(config.ui_language, 'confirm')} [Y/n]: ").lower()
        if answer in {"", "y", "yes"}:
            return config
        field = safe_input(f"{tr(config.ui_language, 'edit')}: ")
        if not field:
            return config
        if not field.isdigit() or not 1 <= int(field) <= len(keys):
            print(tr(config.ui_language, "invalid"))
            continue
        edit_field(config, keys[int(field) - 1], classic=True)


def can_use_keyboard_ui(force: bool = False) -> bool:
    if os.name != "nt":
        return False
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return False
    try:
        import msvcrt  # noqa: F401
    except ImportError:
        return False
    return True


def rendered_value(config: PaperSpineConfig, field: str) -> str:
    value = getattr(config, field)
    if isinstance(value, list):
        return "; ".join(value)
    return str(value)


def option_triplet(config: PaperSpineConfig, field: str) -> tuple[str, str, str] | None:
    if field not in CHOICE_FIELDS:
        return None
    options = CHOICE_FIELDS[field]
    current = getattr(config, field)
    index = options.index(current) if current in options else 0
    return options[(index - 1) % len(options)], options[index], options[(index + 1) % len(options)]


def set_choice_value(config: PaperSpineConfig, field: str, direction: int) -> None:
    options = CHOICE_FIELDS[field]
    current = getattr(config, field)
    index = options.index(current) if current in options else 0
    setattr(config, field, options[(index + direction) % len(options)])
    normalize_config(config)


def edit_field(config: PaperSpineConfig, field: str, classic: bool = False) -> None:
    if field in CHOICE_FIELDS:
        if classic:
            setattr(config, field, choose(field, CHOICE_FIELDS[field], config.ui_language, getattr(config, field)))
            normalize_config(config)
        return
    clear_screen()
    print_banner(config.ui_language)
    print(f"{tr(config.ui_language, field)}")
    print(tr(config.ui_language, "text_help"))
    current = rendered_value(config, field)
    if current:
        print(f"\nCurrent: {current}")
    answer = safe_input("> ")
    if not answer:
        return
    if field in {"official_urls", "special_requirements"}:
        setattr(config, field, split_items(answer))
    else:
        setattr(config, field, answer)
    normalize_config(config)


def normalize_config(config: PaperSpineConfig) -> None:
    if config.output_language != "en":
        config.translation_package = "none"
    if config.workflow == "rewrite_existing":
        config.materials_dir = config.materials_dir or ""
    else:
        config.draft_path = config.draft_path or ""


def find_first_existing_dir(names: tuple[str, ...]) -> str:
    cwd = Path.cwd()
    for name in names:
        if (cwd / name).is_dir():
            return name
    for path in cwd.iterdir():
        if path.is_dir() and path.name not in {"paper_rewriting_output", ".git", ".vscode"}:
            has_materials = any(path.glob(pattern) for pattern in ("*.md", "*.txt", "*.csv", "*.png", "*.jpg", "*.pdf", "*.docx"))
            if has_materials:
                return path.name
    return ""


def find_candidate_draft() -> str:
    cwd = Path.cwd()
    candidates: list[Path] = []
    for pattern in ("*.tex", "*.md", "*.docx", "*.pdf"):
        candidates.extend(path for path in cwd.glob(pattern) if path.is_file())
    candidates = [path for path in candidates if not path.name.lower().startswith("readme")]
    if not candidates:
        return ""
    preferred = ("draft", "manuscript", "paper", "main", "初稿", "论文")
    candidates.sort(key=lambda p: (0 if any(token in p.name.lower() for token in preferred) else 1, len(p.name)))
    return candidates[0].name


def read_small_text_files(root: Path, limit: int = 8) -> str:
    chunks: list[str] = []
    for path in root.rglob("*"):
        if len(chunks) >= limit:
            break
        if not path.is_file() or path.suffix.lower() not in {".md", ".txt"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        chunks.append(text[:2000])
    return "\n".join(chunks)


def infer_motivation(text: str, ui_language: str) -> str:
    markers = ("核心想法", "核心动机", "motivation", "Motivation", "主线", "创新点")
    for line in text.splitlines():
        clean = line.strip(" #：:*-")
        if any(marker in line for marker in markers) and 12 <= len(clean) <= 180:
            return clean
    if ui_language == "zh":
        return "请先调研目标场景和优秀样例，再生成候选动机并由用户确认。"
    return "Research the target scene and strong examples first, then propose motivation options for user confirmation."


def infer_urls(text: str) -> list[str]:
    seen: list[str] = []
    for match in URL_RE.findall(text):
        url = match.rstrip(".,;，。；")
        if url not in seen:
            seen.append(url)
    return seen[:6]


def auto_config_project(config: PaperSpineConfig, args: argparse.Namespace) -> None:
    cwd = Path.cwd()
    materials_dir = find_first_existing_dir(("materials", "素材", "source_materials", "data"))
    draft_path = find_candidate_draft()
    if not args.workflow:
        if materials_dir and not draft_path:
            config.workflow = "build_from_materials"
        elif draft_path:
            config.workflow = "rewrite_existing"
    if not args.materials_dir and materials_dir:
        config.materials_dir = materials_dir
    if not args.draft_path and draft_path:
        config.draft_path = draft_path
    if not args.target_name:
        config.target_name = cwd.name.replace("_", " ").replace("-", " ")
    material_root = cwd / config.materials_dir if config.materials_dir else cwd
    text = read_small_text_files(material_root if material_root.exists() else cwd)
    if not args.user_motivation:
        config.user_motivation = infer_motivation(text, config.ui_language)
    if not args.official_url:
        config.official_urls = infer_urls(text)
    if not args.special_requirement:
        requirements = [
            "必须输出 final_paper/main.tex；如果本机有 LaTeX 编译器则编译 paper.pdf。",
            "必须生成详细 writing_rationale_matrix.md，逐段解释写作逻辑。",
        ]
        figures_dir = material_root / "figures"
        if figures_dir.exists() and any(figures_dir.glob("*.*")):
            requirements.append("复制并引用素材图片到最终 LaTeX 项目的 figures/。")
        if config.workflow == "build_from_materials":
            requirements.append("从素材从零构筑，不把技术说明当成初稿润色。")
        config.special_requirements = requirements
    normalize_config(config)


def field_label(config: PaperSpineConfig, field: str, index: int, selected: bool, width: int) -> str:
    label = f"{index:02d}. {tr(config.ui_language, field)}"
    color = "1;97" if selected else "90"
    return pad_ansi(ansi(label, color), width)


def value_display(config: PaperSpineConfig, field: str, width: int) -> str:
    gray = "90"
    white = "1;97"
    triplet = option_triplet(config, field)
    if triplet:
        prev, current, nxt = triplet
        left = ansi(help_text(field, prev, config.ui_language) or prev, gray)
        mid = ansi(help_text(field, current, config.ui_language) or current, white)
        right = ansi(help_text(field, nxt, config.ui_language) or nxt, gray)
        slot = max(12, (width - 6) // 3)
        return (
            pad_ansi(left, slot)
            + "   "
            + pad_ansi(mid, slot)
            + "   "
            + pad_ansi(right, slot)
        )[: width + 30]
    current = rendered_value(config, field) or tr(config.ui_language, "empty")
    left = ansi(tr(config.ui_language, "auto"), gray)
    mid = ansi(crop_plain(current, max(10, width // 2)), white)
    right = ansi(tr(config.ui_language, "enter_edit"), gray)
    slot = max(12, (width - 6) // 3)
    return pad_ansi(left, slot) + "   " + pad_ansi(mid, slot) + "   " + pad_ansi(right, slot)


def keyboard_editor(config: PaperSpineConfig) -> PaperSpineConfig:
    fields = list(FIELD_ORDER) + ["save"]
    index = 0
    while True:
        normalize_config(config)
        field = fields[index]
        width = term_width()
        left_w = max(28, int(width * 0.30))
        right_w = max(58, width - left_w - 5)
        clear_screen()
        print(ansi("╭" + "─" * (width - 2) + "╮", "38;5;208"))
        print(ansi("│", "38;5;208") + pad_ansi(ansi("PaperSpine", "1;97") + "  " + tr(config.ui_language, "banner"), width - 2) + ansi("│", "38;5;208"))
        print(ansi("├" + "─" * left_w + "┬" + "─" * (width - left_w - 3) + "┤", "38;5;208"))
        print(ansi("│", "38;5;208") + pad_ansi(ansi("Fields", "90"), left_w) + ansi("│", "38;5;208") + pad_ansi(ansi(tr(config.ui_language, "keyboard_help"), "90"), width - left_w - 3) + ansi("│", "38;5;208"))
        print(ansi("├" + "─" * left_w + "┼" + "─" * (width - left_w - 3) + "┤", "38;5;208"))
        for row, item in enumerate(fields):
            selected = row == index
            if item == "save":
                left = pad_ansi(ansi("S. " + tr(config.ui_language, "save"), "38;5;208" if selected else "90"), left_w)
                right = pad_ansi(ansi(tr(config.ui_language, "confirm"), "1;97" if selected else "90"), width - left_w - 3)
            else:
                left = field_label(config, item, row + 1, selected, left_w)
                right = pad_ansi(value_display(config, item, right_w), width - left_w - 3)
            print(ansi("│", "38;5;208") + left + ansi("│", "38;5;208") + right + ansi("│", "38;5;208"))
        print(ansi("╰" + "─" * left_w + "┴" + "─" * (width - left_w - 3) + "╯", "38;5;208"))
        key = read_key()
        if key == "up":
            index = (index - 1) % len(fields)
        elif key == "down":
            index = (index + 1) % len(fields)
        elif key == "left" and field in CHOICE_FIELDS:
            set_choice_value(config, field, -1)
        elif key == "right" and field in CHOICE_FIELDS:
            set_choice_value(config, field, 1)
        elif key == "enter":
            if field == "save":
                return config
            if field in CHOICE_FIELDS:
                index = (index + 1) % len(fields)
            else:
                edit_field(config, field)
        elif key == "save":
            return config
        elif key == "quit":
            raise KeyboardInterrupt(tr(config.ui_language, "quit"))


def base_config_from_args(args: argparse.Namespace, ui_language: str) -> PaperSpineConfig:
    workflow = args.workflow or "rewrite_existing"
    scene = args.scene or "journal"
    output_language = args.output_language or default_language(scene)
    translation_package = args.translation_package
    if output_language != "en":
        translation_package = "none"
    config = PaperSpineConfig(
        workflow=workflow,
        scene=scene,
        tier=args.tier or "flash",
        output_language=output_language,
        target_name=args.target_name,
        materials_dir=args.materials_dir,
        draft_path=args.draft_path,
        user_motivation=args.user_motivation,
        official_urls=list(args.official_url),
        special_requirements=list(args.special_requirement),
        word_output=args.word_output,
        translation_package=translation_package,
        ui_language=ui_language,
    )
    if not args.no_interactive:
        auto_config_project(config, args)
    return config


def build_config(args: argparse.Namespace) -> PaperSpineConfig:
    global_config = load_global_config()
    ui_language = args.ui_language or global_config.get("ui_language", "zh")
    use_keyboard = (
        not args.classic_input
        and not args.no_interactive
        and (args.keyboard_ui or sys.stdin.isatty())
        and can_use_keyboard_ui(force=args.keyboard_ui)
    )

    if args.setup_global and not args.no_interactive:
        if use_keyboard:
            config = base_config_from_args(args, ui_language)
            print_welcome_screen(config.ui_language, wait=True)
            fields = ("ui_language", "save")
            index = 0
            while True:
                clear_screen()
                print_banner(config.ui_language)
                print(tr(config.ui_language, "keyboard_help"))
                for idx, field in enumerate(fields):
                    marker = ">" if idx == index else " "
                    label = tr(config.ui_language, field) if field != "save" else tr(config.ui_language, "save")
                    value = config.ui_language if field == "ui_language" else ""
                    print(f"{marker} {label:<18} {value}")
                key = read_key()
                if key in {"up", "down"}:
                    index = (index + 1) % len(fields)
                elif key in {"left", "right"} and fields[index] == "ui_language":
                    set_choice_value(config, "ui_language", 1 if key == "right" else -1)
                elif key in {"enter", "save"}:
                    break
                elif key == "quit":
                    raise KeyboardInterrupt(tr(config.ui_language, "quit"))
            ui_language = config.ui_language
        else:
            print_banner(ui_language)
            ui_language = choose("ui_language", UI_LANGUAGES, ui_language, default=ui_language)
        save_global_config({"ui_language": ui_language})
    elif args.setup_global:
        save_global_config({"ui_language": ui_language})

    config = base_config_from_args(args, ui_language)
    if args.no_interactive:
        return config

    if use_keyboard:
        print_welcome_screen(config.ui_language, wait=True)
        return keyboard_editor(config)

    print_welcome_screen(ui_language, wait=False)
    print_banner(ui_language)
    config.workflow = args.workflow or choose("workflow", WORKFLOWS, ui_language)
    config.scene = args.scene or choose("scene", SCENES, ui_language)
    config.tier = args.tier or choose("tier", TIERS, ui_language, default=config.tier)
    config.output_language = args.output_language or choose(
        "output_language", LANGUAGES, ui_language, default=config.output_language
    )
    config.word_output = choose("word_output", WORD_OUTPUTS, ui_language, default=config.word_output)
    if config.output_language == "en":
        config.translation_package = choose(
            "translation_package", TRANSLATION_PACKAGES, ui_language, default=config.translation_package
        )
    config.target_name = ask_text("target_name", ui_language, config.target_name)
    if config.workflow == "rewrite_existing":
        config.draft_path = ask_text("draft_path", ui_language, config.draft_path)
    else:
        config.materials_dir = ask_text("materials_dir", ui_language, config.materials_dir)
    config.user_motivation = ask_text("user_motivation", ui_language, config.user_motivation)
    config.official_urls.extend(split_items(ask_text("official_urls", ui_language)))
    config.special_requirements.extend(split_items(ask_text("special_requirements", ui_language)))
    normalize_config(config)
    return edit_config(config)


def markdown_config(config: PaperSpineConfig) -> str:
    data = asdict(config)
    lines = ["# PaperSpine Config", ""]
    for key, value in data.items():
        rendered = ", ".join(value) if isinstance(value, list) else value
        lines.append(f"- **{key}**: {rendered}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    configure_windows_console()
    args = parse_args()
    config = build_config(args)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "paper_spine_config.json"
    md_path = output_dir / "paper_spine_config.md"
    json_path.write_text(json.dumps(asdict(config), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(markdown_config(config), encoding="utf-8")
    print(f"{tr(config.ui_language, 'wrote')} {json_path}")
    print(f"{tr(config.ui_language, 'wrote')} {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
