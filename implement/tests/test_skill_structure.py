"""不依赖外部工具的开放 Agent Skills 基础结构回退检查。"""

from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_NAMES = ("clarifier", "todos", "implement")
HOST_MIRROR_ROOTS = (ROOT / ".codex" / "skills", ROOT / ".claude" / "skills")
# 安装到单独的 skills 根目录时，仅校验该目录；在仓库根目录时再校验两套镜像。
SKILL_ROOTS = (ROOT, *HOST_MIRROR_ROOTS) if all(path.is_dir() for path in HOST_MIRROR_ROOTS) else (ROOT,)
FRONT_MATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
LINK_PATTERN = re.compile(r"\]\((?![a-z][a-z0-9+.-]*:|#)([^)]+)\)", re.IGNORECASE)
CROSS_SKILL_LINK_PATTERN = re.compile(r"\]\(\.\./[^)]+/SKILL\.md\)")


RUNTIME_FILES = {
    "clarifier": {Path("SKILL.md")},
    "todos": {Path("SKILL.md")},
    "implement": {Path("SKILL.md"), Path("scripts") / "check_review_brief.py"},
}


def installed_files(skill_directory: Path) -> set[Path]:
    """列出镜像目录中的文件，排除 Python 运行时生成物。"""
    return {
        path.relative_to(skill_directory)
        for path in skill_directory.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    }


class SkillStructureTests(unittest.TestCase):
    def test_directory_names_match_required_front_matter(self) -> None:
        for skill_root in SKILL_ROOTS:
            for skill_name in SKILL_NAMES:
                skill_file = skill_root / skill_name / "SKILL.md"
                content = skill_file.read_text(encoding="utf-8")
                match = FRONT_MATTER_PATTERN.match(content)
                self.assertIsNotNone(match, f"{skill_file} 缺少 YAML 前置元数据")
                front_matter = match.group(1)
                self.assertRegex(front_matter, rf"(?m)^name:\s*{re.escape(skill_name)}\s*$")
                for key in ("description",):
                    self.assertRegex(front_matter, rf"(?m)^{key}:\s*\S")

    def test_relative_markdown_links_resolve(self) -> None:
        for skill_root in SKILL_ROOTS:
            for skill_name in SKILL_NAMES:
                skill_file = skill_root / skill_name / "SKILL.md"
                for target in LINK_PATTERN.findall(skill_file.read_text(encoding="utf-8")):
                    target_path = target.split("#", maxsplit=1)[0]
                    self.assertTrue(
                        (skill_file.parent / target_path).is_file(),
                        f"{skill_file} 的相对引用不存在：{target}",
                    )

    def test_host_mirrors_match_public_sources(self) -> None:
        for mirror_root in SKILL_ROOTS[1:]:
            for skill_name in SKILL_NAMES:
                source_directory = ROOT / skill_name
                mirror_directory = mirror_root / skill_name
                source_files = RUNTIME_FILES[skill_name]
                mirror_files = installed_files(mirror_directory)
                self.assertSetEqual(
                    source_files,
                    mirror_files,
                    f"镜像文件集合与源文件不一致：{mirror_directory}",
                )
                for relative_path in source_files:
                    source = source_directory / relative_path
                    mirror = mirror_directory / relative_path
                    self.assertEqual(
                        source.read_bytes(),
                        mirror.read_bytes(),
                        f"镜像与源文件不一致：{mirror}",
                    )

    def test_cross_skill_references_do_not_use_relative_paths(self) -> None:
        for skill_root in SKILL_ROOTS:
            for skill_name in SKILL_NAMES:
                skill_file = skill_root / skill_name / "SKILL.md"
                self.assertNotRegex(
                    skill_file.read_text(encoding="utf-8"),
                    CROSS_SKILL_LINK_PATTERN,
                    f"跨 skill 引用应只使用名称：{skill_file}",
                )


if __name__ == "__main__":
    unittest.main()
