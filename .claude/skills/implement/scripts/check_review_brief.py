#!/usr/bin/env python3
"""校验 implement 生成的 Markdown 审查摘要。

用途：检查审查摘要的标题、三个二级章节、列表格式和前两个章节的可见字符上限。
输入：一个 UTF-8 编码的 Markdown 审查摘要文件路径；文件应包含恰好三个规定的二级章节。
输出：合规时输出成功信息并以 0 退出；不合规时逐项输出错误并以 1 退出。
依赖：Python 3 标准库。
示例：python3 implement/scripts/check_review_brief.py implement/tests/fixtures/valid_review.md
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_SECTIONS = (
    "本次任务做了什么",
    "预期有所偏差的部分及影响",
    "更多信息",
)
TITLE_PATTERN = re.compile(r"^#\s+\S.*审查摘要\s*$")
SECOND_LEVEL_PATTERN = re.compile(r"^##\s+(.+?)\s*$")
UNORDERED_LIST_PATTERN = re.compile(r"^\s*[-*+]\s+\S")
LINK_PATTERN = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")


def visible_character_count(lines: list[str]) -> int:
    """返回 Markdown 内容的可见字符数，忽略空白与常见格式标记。"""
    visible = 0
    for line in lines:
        text = re.sub(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", line)
        text = LINK_PATTERN.sub(r"\1", text)
        text = text.replace("```", "").replace("`", "")
        text = re.sub(r"(?<!\\)[*_~]", "", text)
        visible += sum(not character.isspace() for character in text)
    return visible


def split_sections(content: str) -> tuple[str, list[str], dict[str, list[str]]]:
    """按二级章节切分文档，保留标题前内容用于标题校验。"""
    before_sections: list[str] = []
    headings: list[str] = []
    sections: dict[str, list[str]] = {}
    current_heading: str | None = None

    for line in content.splitlines():
        match = SECOND_LEVEL_PATTERN.match(line)
        if match:
            current_heading = match.group(1)
            headings.append(current_heading)
            sections.setdefault(current_heading, [])
            continue
        if current_heading is None:
            before_sections.append(line)
        else:
            sections[current_heading].append(line)

    return "\n".join(before_sections), headings, sections


def validate_content(content: str) -> list[str]:
    """返回全部格式错误；空列表表示摘要合规。"""
    errors: list[str] = []
    before_sections, headings, sections = split_sections(content)
    title_lines = [line for line in before_sections.splitlines() if line.strip()]

    if len(title_lines) != 1 or not TITLE_PATTERN.match(title_lines[0]):
        errors.append("标题必须是唯一的一级标题，且以“审查摘要”结尾。")

    if headings != list(REQUIRED_SECTIONS):
        errors.append("二级章节必须恰好按规定顺序为：" + "、".join(REQUIRED_SECTIONS) + "。")
        return errors

    results_lines = [line for line in sections[REQUIRED_SECTIONS[0]] if line.strip()]
    if not results_lines or not all(UNORDERED_LIST_PATTERN.match(line) for line in results_lines):
        errors.append("“本次任务做了什么”必须为非空无序列表。")

    deviation_lines = [line for line in sections[REQUIRED_SECTIONS[1]] if line.strip()]
    if deviation_lines == ["- 无"]:
        pass
    elif "- 无" in deviation_lines:
        errors.append("“- 无”只能作为第二节唯一内容；有偏差时请列出具体偏差。")
    elif not deviation_lines or not all(UNORDERED_LIST_PATTERN.match(line) for line in deviation_lines):
        errors.append("没有交付偏差时，第二节必须精确使用“- 无”；有偏差时必须使用无序列表。")

    first_two_count = visible_character_count(
        sections[REQUIRED_SECTIONS[0]] + sections[REQUIRED_SECTIONS[1]]
    )
    if first_two_count > 200:
        errors.append(f"前两个章节的可见字符数为 {first_two_count}，超过 200。")

    return errors


def validate_file(path: Path) -> list[str]:
    """读取并校验文件；读取失败也以可报告的校验错误返回。"""
    try:
        return validate_content(path.read_text(encoding="utf-8"))
    except OSError as error:
        return [f"无法读取 {path}：{error}"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="校验 implement 审查摘要格式")
    parser.add_argument("review", type=Path, help="待校验的 UTF-8 Markdown 审查摘要路径")
    args = parser.parse_args(argv)

    errors = validate_file(args.review)
    if errors:
        for error in errors:
            print(f"错误：{error}", file=sys.stderr)
        return 1

    print(f"审查摘要格式合规：{args.review}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
