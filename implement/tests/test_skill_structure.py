"""不依赖外部工具的开放 Agent Skills 基础结构回退检查。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_NAMES = ("clarifier", "todos", "implement")
FRONT_MATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK_PATTERN = re.compile(r"\]\((?![a-z][a-z0-9+.-]*:|#)([^)]+)\)", re.IGNORECASE)


class SkillStructureTests(unittest.TestCase):
    def test_directory_names_match_required_front_matter(self) -> None:
        for skill_name in SKILL_NAMES:
            skill_file = ROOT / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            match = FRONT_MATTER_PATTERN.match(content)
            self.assertIsNotNone(match, f"{skill_file} 缺少 YAML 前置元数据")
            front_matter = match.group(1)
            self.assertRegex(front_matter, rf"(?m)^name:\s*{re.escape(skill_name)}\s*$")
            for key in ("description", "license", "compatibility"):
                self.assertRegex(front_matter, rf"(?m)^{key}:\s*\S")

    def test_relative_markdown_links_resolve(self) -> None:
        for skill_name in SKILL_NAMES:
            skill_file = ROOT / skill_name / "SKILL.md"
            for target in LINK_PATTERN.findall(skill_file.read_text(encoding="utf-8")):
                target_path = target.split("#", maxsplit=1)[0]
                self.assertTrue(
                    (skill_file.parent / target_path).is_file(),
                    f"{skill_file} 的相对引用不存在：{target}",
                )


if __name__ == "__main__":
    unittest.main()
