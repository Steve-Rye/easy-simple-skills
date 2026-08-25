"""check_review_brief.py 的标准库单元测试。"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


TESTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(TESTS_DIR.parent / "scripts"))
import check_review_brief  # noqa: E402


FIXTURES = TESTS_DIR / "fixtures"


class CheckReviewBriefTests(unittest.TestCase):
    def errors_for(self, filename: str) -> list[str]:
        return check_review_brief.validate_file(FIXTURES / filename)

    def test_accepts_compliant_review(self) -> None:
        self.assertEqual([], self.errors_for("valid_review.md"))

    def test_rejects_sections_in_wrong_order(self) -> None:
        errors = self.errors_for("invalid_section_order.md")
        self.assertTrue(any("二级章节" in error for error in errors))

    def test_rejects_visible_character_limit_over_200(self) -> None:
        errors = self.errors_for("invalid_too_long.md")
        self.assertTrue(any("超过 200" in error for error in errors))

    def test_rejects_non_list_results(self) -> None:
        errors = self.errors_for("invalid_results_not_list.md")
        self.assertTrue(any("本次任务做了什么" in error for error in errors))

    def test_rejects_unformatted_no_deviation_marker(self) -> None:
        errors = self.errors_for("invalid_no_deviation_format.md")
        self.assertTrue(any("第二节" in error for error in errors))

    def test_rejects_no_deviation_marker_mixed_with_a_deviation(self) -> None:
        content = """# 示例任务审查摘要

## 本次任务做了什么
- 新增校验器。

## 预期有所偏差的部分及影响
- 无
- 示例偏差。

## 更多信息
- 关联代办：`step01.01_示例任务.md`
"""
        errors = check_review_brief.validate_content(content)
        self.assertTrue(any("唯一内容" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
