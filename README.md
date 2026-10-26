# diceframe-skills

DiceFrame 的 AI 协作技能（agent skills）集合。每个顶层目录是一个独立 skill，供开发与内容创作时使用。

## 技能列表

| Skill | 用途 |
|---|---|
| [`diceframe-adventure-pack/`](diceframe-adventure-pack/) | 创作、修改与校验冒险包（Adventure Bundle / 内容包）：graph v1 / v2 格式、manifest 与 locale 契约、D&D 遭遇两条链路、生产 loader 校验脚本 |

## 安装

把对应 skill 目录复制（或符号链接）到用户或项目技能目录：

```bash
# 用户级（所有项目可用）
cp -r diceframe-adventure-pack ~/.zcode/skills/

# 或项目级（仅当前仓库生效）
cp -r diceframe-adventure-pack <repo>/.zcode/skills/
```

新会话生效。`validate_pack.py` 校验脚本需要能访问 diceframe 检出（脚本会自动向上查找 `src/adventures/bundle.py`，或用 `--repo` 显式指定）；D&D 数值校验需用带依赖的 diceframe venv Python 运行。

## 维护约定

- 冒险包格式的**事实来源**是主仓库的 `src/adventures/bundle.py`、`src/adventures/graph_v2.py`、`src/adventures/gates.py`、`src/adventures/outcomes.py` 与 `docs/adventures/`。主仓库格式契约变更时，同步更新对应 skill 并在 PR 中一起评审。
- skill 内容经过真实 `AdventureBundleLoader` 校验（示例包可加载、错误路径可复现）。修改后请保持这一验证方式。
