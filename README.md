# Easy Simple Skills

一组以简体中文编写、采用开放 Agent Skills 目录格式的轻量技能。它们可整体安装到支持该格式的代理中，也可单独阅读和使用；完整工作流依赖三个同级目录共同存在。

## 收录内容

- `clarifier/`：将模糊需求澄清为结构化、可落地的 Markdown 任务文档。
- `todos/`：以纯 Markdown 文件和目录位置管理任务状态。
- `implement/`：按照已就绪的任务文档实施、验证，并生成精简审查摘要。

协作顺序通常为：`clarifier` 澄清任务 -> `todos` 管理任务文件 -> `implement` 实施和验证。`implement` 会在 `todo/reviews/` 中生成审查摘要，但不会改变任务状态；状态仍仅由 `pending/`、`done/`、`abandon/` 决定。

## 目录结构

```text
easy-simple-skills/
  clarifier/
    SKILL.md
  todos/
    SKILL.md
  implement/
    SKILL.md
    scripts/
      check_review_brief.py
    tests/
      fixtures/
      test_check_review_brief.py
      test_skill_structure.py
  .codex/skills/
    clarifier/ todos/ implement/  # Codex 本地 skill 镜像
  .claude/skills/
    clarifier/ todos/ implement/  # Claude Code 本地 skill 镜像
  todo/
    pending/     # 待处理任务
    done/        # 已完成任务
    abandon/     # 已放弃任务
    reviews/     # 非状态审查摘要，文件名与原任务一致
```

## 本地 Skill 镜像

根目录的 `clarifier/`、`todos/`、`implement/` 是公开发布的唯一源文件。`.codex/skills/` 与 `.claude/skills/` 保留同一组三个 skill 的运行时镜像，供两种宿主的项目级发现机制直接使用；其中 `implement` 只同步运行所需的校验器脚本。测试 fixture 和单元测试只保留在根目录的 `implement/tests/`。

修改公开 skill 后，必须同步更新两套运行时镜像。`test_skill_structure.py` 会比较运行时文件，并验证三处的目录名、必要前置元数据和相对引用。

## 安装与调用

对于其他支持开放 Agent Skills 格式的代理，将根目录的 `clarifier/`、`todos/`、`implement/` 三个目录保持同级复制到其 skills 根目录，再依该代理的安装机制启用。缺少协作 skill 时，需要自行承担缺失的澄清、任务状态或审查摘要流程。

示例任务文件为 `todo/pending/step01.01_示例任务.md`。安装后可显式调用：

```text
# Codex
$implement 使用 todo/pending/step01.01_示例任务.md 开始实施

# Claude Code
/implement 使用 todo/pending/step01.01_示例任务.md 开始实施
```

自然语言触发的支持程度因代理而异。需要确定行为时，请使用显式调用。

## 前置条件与本地验证

本仓库的校验器和测试只需要 Python 3 标准库，无网络、密钥或模型服务依赖。请在仓库根目录运行：

```sh
python3 -m unittest discover -s implement/tests -p 'test_*.py'
python3 implement/scripts/check_review_brief.py implement/tests/fixtures/valid_review.md
python3 implement/scripts/check_review_brief.py implement/tests/fixtures/invalid_section_order.md; test $? -ne 0
```

最后一条命令预期校验器以非零状态退出，用于确认不合规摘要会被拒绝。`test_skill_structure.py` 是无外部格式校验工具时的本地回退检查：验证三个目录名、必要前置元数据与 Markdown 相对引用。

## 许可证

本项目采用 [MIT License](LICENSE)。
