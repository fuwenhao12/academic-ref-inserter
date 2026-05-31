JOURNAL_PROFILES = {
    "chinese-core": {
        "name": "中文核心期刊",
        "numbering_style": "chinese",
        "numbering_format": "式({num})",
        "font": "宋体",
        "font_size_pt": 10.5,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": True,
    },
    "ieee": {
        "name": "IEEE Transactions",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 10,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "apa": {
        "name": "APA 7th Edition",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 12,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "nature": {
        "name": "Nature",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 9,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "science": {
        "name": "Science",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 9,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "springer": {
        "name": "Springer Lecture Notes",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 10,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "elsevier": {
        "name": "Elsevier",
        "numbering_style": "parentheses",
        "numbering_format": "({num})",
        "font": "Times New Roman",
        "font_size_pt": 11,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": False,
    },
    "thesis": {
        "name": "学位论文 (Thesis)",
        "numbering_style": "section",
        "numbering_format": "({chapter}.{num})",
        "font": "宋体",
        "font_size_pt": 12,
        "display_align": "center",
        "number_align": "right",
        "inline_parent": True,
    },
}


def get_profile(journal_key):
    if journal_key in JOURNAL_PROFILES:
        return JOURNAL_PROFILES[journal_key]
    for key, profile in JOURNAL_PROFILES.items():
        if journal_key.lower() in key.lower():
            return profile
        if journal_key.lower() in profile["name"].lower():
            return profile
    return None


def list_journals():
    lines = ["Supported journal formats:"]
    for key, profile in JOURNAL_PROFILES.items():
        lines.append(f"  {key:20s}  {profile['numbering_format']:15s}  {profile['name']}")
    return "\n".join(lines)
