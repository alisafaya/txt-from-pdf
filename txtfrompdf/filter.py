# -*- coding: utf-8 -*-
import logging
import re
from typing import Dict, List

from .fix_unicode import fix_unicode


logger = logging.getLogger(__name__)

# fmt: off
LONE_ACCENT_DICT: Dict[str, str] = {
    "a´": "á", "e´": "é", "i´": "í", "o´": "ó", "u´": "ú",
    "a¨": "ä", "e¨": "ë", "i¨": "ï", "o¨": "ö", "u¨": "ü",
    "a^": "â", "e^": "ê", "i^": "î", "o^": "ô", "u^": "û",
    "a`": "à", "e`": "è", "i`": "ì", "o`": "ò", "u`": "ù",
    "a~": "ã", "o~": "õ", "n~": "ñ",
}
# fmt: on

LONE_ACCENT_DICT.update({k.upper(): v.upper() for k, v in LONE_ACCENT_DICT.items()})

DATE_PATTERN = re.compile(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}")
COMBINING_DIACRITICS = re.compile(r"[\u0300-\u036F]")
OTHER_DIACRITICS = re.compile(r"(?:\xa8|[\u02C0-\u02DF])")
CID_PATTERN = re.compile(r"\(cid:[0-9]+\)")
DOUBLE_WHITESPACE = re.compile(r"\s\s+")
TAB_PATTERN = re.compile(r"\t")


def ditch_combining_diacritics(text: str) -> str:
    for orig, repl in LONE_ACCENT_DICT.items():
        text = text.replace(orig, repl)
    text = COMBINING_DIACRITICS.sub("", text)
    return OTHER_DIACRITICS.sub("", text)


def is_date(x: str) -> bool:
    return bool(DATE_PATTERN.match(x))


def header_footer_filter(page: str) -> str:
    if len(page) < 50:
        stripped = page.strip()
        if stripped.startswith("©"):
            return ""
        words = stripped.split()
        if (
            words
            and words[0] in ("r", "copyright")
            and len(words) >= 2
            and is_date(words[1])
        ):
            return ""
    return page


def replace_hyphenated(text: str) -> str:
    # Handle words split across lines, but not at the start of a line
    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)

    # Handle extra spaces after hyphens in the middle of a line, but not at the start
    text = re.sub(r"(\w+)-\s{2,}(\w+)", r"\1-\2", text)
    return text


def remove_cid(text: str) -> str:
    return CID_PATTERN.sub("", text)


def filter_double_whitespace(text: str) -> str:
    return DOUBLE_WHITESPACE.sub(" ", text)


def replace_tabs(text: str) -> str:
    tab_count = text.count("\t")
    space_count = text.count(" ")
    return TAB_PATTERN.sub(" ", text) if tab_count > space_count else text


def combine_paragraph_lines(text: str) -> str:
    lines = text.split("\n")
    combined_lines = []

    def is_list_item(line: str) -> bool:
        return bool(
            re.match(r"^\s*[\-\*•◦▪▫▹▸▻►▼▽◆◇○●]", line)
            or re.match(r"^\s*(\d+|[a-zA-Z])[.)\]]", line)
        )

    def should_merge(current: str, next: str) -> bool:
        current = current.strip()
        next = next.strip()
        return (
            current
            and next
            and not is_list_item(current)
            and not is_list_item(next)
            and not current.endswith(".")
        )

    i = 0
    while i < len(lines):
        current_line = lines[i].strip()

        # If the current line is empty or a list item, add it as is
        if not current_line or is_list_item(current_line):
            combined_lines.append(lines[i])
            i += 1
            continue

        # Look ahead to see if we need to merge lines
        merged_line = current_line
        while i + 1 < len(lines) and should_merge(merged_line, lines[i + 1]):
            merged_line += " " + lines[i + 1].strip()
            i += 1

        combined_lines.append(merged_line)
        i += 1

    return "\n".join(combined_lines)


def post_process(text: str) -> str:
    text = replace_hyphenated(text)
    paras = text.split("\n\n")
    out: List[str] = []

    for para in paras:
        para = combine_paragraph_lines(para)
        para = header_footer_filter(para)
        para = filter_double_whitespace(para)
        para = ditch_combining_diacritics(fix_unicode(remove_cid(para)))
        out.append(para)

    out = [para for para in out if para.strip()]
    return replace_tabs("\n\n".join(out)).strip()
