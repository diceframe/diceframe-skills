---
name: diceframe-adventure-pack
description: 创作、修改与校验 DiceFrame 冒险包（内容包/Adventure Bundle）。当用户想写冒险剧情包、自制 adventure 内容模组、编辑 manifest.json / adventure.json / locales、把一段剧本整理成 diceframe:adventure-graph-v1 或 v2 包，或排查 "adventure package" 加载/校验报错时使用。凡是提到冒险包、内容包、剧情包、adventure bundle、adventure-graph-v2、encounter_catalog、world_policy、剧情模组，即使没说"包"字也应使用本技能。
---

# DiceFrame 冒险包（Adventure Bundle）创作

冒险包是**只含数据的剧情包**：一个目录就是一个包，校验以整包为原子单位，任何一处错误都会拒绝加载。权威契约是仓库里的 `src/adventures/bundle.py`、`src/adventures/graph_v2.py` 和 `docs/adventures/ADVENTURE_BUNDLE_CN.md`。本技能概括格式；遇到记不准的字段时读代码，**不要猜字段、不要发明新语义**——未知字段一律 fail closed。

## 第 0 步：先选包类型

| 目标 | manifest.format | required_runtime | 能做什么 |
|---|---|---|---|
| 通用剧情包（新包默认） | `diceframe:adventure-graph-v2` | `{"id": "core:adventure", "minimum_version": 1}` | 纯叙事图：场景/目标/决策/里程碑、世界与进度门槛。CoC、自定义规则、D&D 通用。**禁止**遭遇节点、`rules.*` 门槛、`item_reward` |
| D&D 5e 2024 专属包 | v1 或 v2 | `{"id": "core:dnd2024", "minimum_version": 1}` | 上述之外还可用遭遇与规则门槛：v1 包在包内 `encounter_catalog` 内联敌人数值；v2 包用节点 `encounter_ref: "encounter_profile:<id>"` 引用内容库遭遇（详见 [references/dnd2024-encounters.md](references/dnd2024-encounters.md)） |

通用 profile 拒绝的机制就明着不写，不要试图绕过（例如把数值藏进 reference 资料）——数值只能是 `automation_level: "reference"` 的惰性记录，字段白名单见下文。

## 包结构

```text
<directory_id>/                 # 目录名 ^[a-z0-9][a-z0-9_.-]*$，只是本地查找键
├─ manifest.json                # 包身份与兼容性（schema_version 恒为 1）
├─ adventure.json               # 唯一的 adventure 实体（剧情图）
├─ content/**/*.json            # 其它实体：scene / npc / map_location / encounter_catalog / item …
└─ locales/<locale>/**/*.json   # locale 覆盖（每个 supported_locale 必须有同名目录）
```

## manifest.json（字段即契约）

```json
{
  "schema_version": 1,
  "adventure_id": "user:my_quest",
  "version": "1.0.0",
  "format": "diceframe:adventure-graph-v2",
  "world_policy": "portable",
  "recommended_world_id": "my_world",
  "required_runtime": {"id": "core:adventure", "minimum_version": 1},
  "default_locale": "zh-CN",
  "supported_locales": ["zh-CN", "en"]
}
```

- `adventure_id`：canonical 身份，`^[a-z0-9][a-z0-9_.:-]*$`。**自定义包用 `user:` 前缀**（如 `user:my_quest`）——管理后台创建/导入的包会自动生成 `user:<目录名>` 身份；手写包也照此约定，避免与内置 `core:` 包冲突。全库唯一，重复即拒绝加载。
- `world_policy`：`fixed`（绑定 `recommended_world_id`，不匹配拒绝创建/重开，**必填**该字段）/ `portable`（可换世界但创建时提示适配）/ `agnostic`（不依赖具体世界）。这三个值只描述"能否组合"，不保证剧情合理。
- `supported_locales` 非空、无重复；`default_locale` 必须在其中。每个声明的 locale 都要有 `locales/<locale>/` 目录（可以为空目录，但不能缺）。
- `reference_policy: "adventure-local"`（可选）：所有 step/node 引用必须在包内自解析，禁止回退到外部世界书。

## 实体文件（adventure.json 与 content/**/*.json）

每个文件是一个 JSON object，**必填 envelope**：

```json
{
  "schema_version": 1,
  "kind": "scene",
  "id": "my_scene",
  "source_ref": "diceframe-original:my-quest/act1",
  "automation_level": "guided"
}
```

- `kind`/`id` 匹配 `^[a-z0-9][a-z0-9_.-]*$`；同 kind 内 `id` 不得重复。
- `automation_level`：`deterministic`（机械执行）/ `guided`（引导叙事）/ `reference`（纯资料）。
- `source_ref` 非空即可，标注出处。
- **全包递归禁止出现这些键**（任何大小写）：`python`、`javascript`、`script`、`code`、`eval`、`module`、`callable`。包括藏在嵌套对象和数组里——写文案时也别用这些词做键。

引用一律用 canonical ref `kind:id`（如 `scene:my_scene`、`npc:mira`），不允许用翻译后的 display name 做身份。

## graph v2 速查（推荐格式）

adventure 实体 = envelope + 图字段，**字段白名单严格**：图字段 `chapters / nodes / objectives / milestones / start_node_ids / visibility / world_seed`，外加展示字段 `name / summary / tutorial / estimated_minutes / recommended_level / player_count / world_policy / recommended_world_id` 和 `format`（值 `diceframe:adventure-graph-v2`）。多写一个字段整包被拒。

```json
{
  "chapters": [{"id": "ch1", "name": "第一章"}],
  "nodes": [
    {"id": "opening", "type": "scene", "chapter_id": "ch1",
     "scene_ref": "scene:my_scene", "npc_refs": ["npc:mira"],
     "transitions": [{"to": "climax"}],
     "on_complete": [{"type": "world_op", "op": {"op": "set_fact", "key": "lamp.lit", "value": true}}]}
  ],
  "objectives": [{"id": "obj_find", "name": "找回灯", "node_ids": ["opening"]}],
  "milestones": [{"id": "mile_end", "name": "点亮路灯", "node_ids": ["climax"]}],
  "start_node_ids": ["opening"]
}
```

要点（完整词表与上界见 [references/graph-v2.md](references/graph-v2.md)）：

- 节点 `type` ∈ `scene | objective | encounter | decision | milestone | reference`；`visibility` ∈ `public | gm`（玩家投影会过滤 gm 内容及其 transition）。public 节点不能挂在 gm 章节下。
- `transitions[].to` 必须指向存在节点；回流（环）合法；`conditions` ≤8 条且为 AND，类型封闭（`world.fact_equals`、`adventure.milestone`、`rules.party_level`…）。证据不足 = 不满足，所以门槛要写玩家能稳定满足的状态。
- **引用存在性分两档**：`transitions[].to`、`chapter_id`、objective/milestone 的 `node_ids` 强制存在；而节点的 `scene_ref` / `npc_refs` / `encounter_ref` 默认只校验 `kind:id` 格式（允许指向包外世界实体）。要包内自解析就声明 `"reference_policy": "adventure-local"`，悬空引用会整包被拒。
- `on_complete` 是 outcome 的**唯一**归属点，类型封闭：`world_op` / `item_reward` / `progress_event`。冒险不直接写权威状态，只声明提案。
- `world_seed`（可选）声明开局实体/关系/事实/进程，字段封闭、有上界。
- 上界：≤32 章节、≤256 节点、≤64 objectives/milestones、每节点 ≤16 transitions/outcomes、≤16 入口。

## locales（只覆盖展示字段）

`locales/<locale>/xxx.json`：

```json
{
  "locale_schema_version": 1,
  "locale": "zh-CN",
  "target": {"kind": "scene", "id": "my_scene"},
  "fields": {"name": "雾中小径", "description": "薄雾吞没了道路。"}
}
```

字段白名单（超出即拒）：adventure → `name/summary/tutorial`；scene → `name/description`；npc → `name/description/summary`；map_location → `name/description`；encounter_catalog → `name/labels`。locale 只改文案，永远不能改引用、门槛、遭遇等机制。`tutorial` 是自由结构对象，v1 包惯例含 `chapters/steps/choices/entities` 的展示文案（参考 `templates/adventures/lanterns_of_greymoor/locales/zh-CN/adventure.json`）。

## 验证（写完必须跑）

用本技能自带的脚本按生产 loader 校验：

```bash
python ~/.zcode/skills/diceframe-adventure-pack/scripts/validate_pack.py <包目录路径>
```

脚本会自动定位 diceframe 仓库（也可 `--repo` 显式指定），整包加载校验（结构/引用/locale/禁词/digest），并按 `required_runtime` 触发对应 validator。D&D 数值校验需要能导入 dnd2024 runtime 的环境——用仓库 venv（如 `.venv/Scripts/python.exe`）运行即可，否则会提示 skipped。任何报错都按报错修，直到通过。也可以手动：

```python
import sys; sys.path.insert(0, "<repo>")
from src.adventures.bundle import AdventureBundleLoader
bundle = AdventureBundleLoader("<包的父目录>").load("<目录名>")
print(bundle.manifest, bundle.content_digest)
```

## 安装与生命周期（改包前必读）

- 运行时目录是应用数据下的 `data/templates/adventures/`。内置包启动时从安装模板同步并保持只读（带 `.diceframe-builtin` 标记）；不要编辑内置包。
- 自定义包可放运行时目录（用 `user:` 身份），或通过管理后台 JSON 编辑 / ZIP 导入，或作为 content-pack 模块分发（plugin 来源只暴露 `plugin.json` 声明的包）。
- **一旦任何存档绑定了某个 `adventure_id`，该包即事实只读**：存档按 `content_digest` 重开校验，内容改动、版本不符、fixed 世界不匹配都会 fail closed。要继续创作就发新 `version` + 新目录或复制成新 identity，不要原地改已发布内容。
- locale 不是身份：不要把翻译后的名字当 canonical id 用。

## 常见拒绝原因速查

| 报错关键词 | 原因 |
|---|---|
| `unknown field` | 实体/节点/gate/outcome/seed 用了白名单外字段 |
| `executable content key is forbidden` | JSON 里出现了 `code`/`script` 等禁词键 |
| `unresolved local reference` | 声明了 `reference_policy: "adventure-local"` 但节点的 `scene_ref`/`npc_refs`/`encounter_ref` 解析不到包内实体 |
| `is missing`（v1） | v1 包的 step `scene_ref`、`encounter_preset_id`、scene 的 `map_location_ref`/`npc_refs` 引用不存在 |
| `does not exist` / `references unknown` | v2 的 `transitions[].to`、`chapter_id`、objective/milestone `node_ids` 指向不存在的对象 |
| `unreachable from start` | v1 节点从 `start_step_id` 结构上不可达（条件门槛不算路径） |
| `locale directory is missing` | manifest 声明的 locale 没有 `locales/<locale>/` 目录 |
| `cannot override` | locale fields 写了白名单外字段 |
| `duplicate` | id 重复（实体/章节/节点/目标/遭遇 preset） |
| `core:adventure narrative profile` | 通用包里写了遭遇、rules.* 门槛、item_reward 或机械实体 |
| `must be between` / `must be an integer` | D&D 遭遇数值越界或类型错误（如 hp 写成字符串） |
| `duplicated`（adventure package） | 同一 `adventure_id` 出现在多个来源/目录 |

## 深入阅读

- graph v2 完整契约（节点/gate/outcome/world_seed 词表与上界）：[references/graph-v2.md](references/graph-v2.md)
- graph v1 存量格式（steps/choices，仍在维护）：[references/graph-v1.md](references/graph-v1.md)
- D&D 遭遇两条链路（v1 encounter_catalog / v2 encounter_profile）与数值校验：[references/dnd2024-encounters.md](references/dnd2024-encounters.md)
- 可直接通过 loader 的完整最小 v2 包示例：[references/example-v2-package.md](references/example-v2-package.md)
