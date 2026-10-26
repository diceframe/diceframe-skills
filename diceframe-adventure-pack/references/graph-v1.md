# graph v1 存量格式（`diceframe:adventure-graph-v1`）

真值来源：`src/adventures/bundle.py` 的 `_validate_graph`。v1 是线性 steps/choices 模型，内置包 `templates/adventures/lanterns_of_greymoor` 是权威示例。新包默认用 v2；v1 继续由既有 loader 校验、长期兼容，旧 D&D 包不要"顺手"改标成 v2（不改标、不静默转换）。

## adventure 实体（v1）

```json
{
  "schema_version": 1,
  "kind": "adventure",
  "id": "my_quest",
  "source_ref": "diceframe-original:my-quest",
  "automation_level": "deterministic",
  "estimated_minutes": 90,
  "start_step_id": "step_opening",
  "chapters": [{"id": "act1", "step_ids": ["step_opening", "step_climax"]}],
  "steps": [
    {"id": "step_opening", "chapter_id": "act1",
     "scene_ref": "scene:my_scene", "requires": "none",
     "choice_ids": ["choice_go"]}
  ],
  "choices": [
    {"id": "choice_go", "step_id": "step_opening", "next_step_id": "step_climax",
     "outcomes": [{"entity_kind": "clue", "entity_id": "clue:ash", "visibility": "public"}]}
  ]
}
```

### 结构规则（全部双向强制）

- `start_step_id` 必须存在于 steps。
- **章节成员双向一致**：step 的 `chapter_id` 必须等于所属章节 id；每个 step 必须恰好列在一个章节的 `step_ids` 里；一个 step 不能出现在多个章节。
- **choice 双向一致**：`choice_ids` 列出的 choice 必须存在且其 `step_id` 指回本 step；每个 choice 必须被其 `step_id` 指向的 step 列出。
- `next_step_id` 为空字符串 = 结局出口；非空必须指向存在的 step。
- **结构可达性**：每个 step 必须从 `start_step_id` 沿 choices 可达（`requires` 条件门槛不算路径——这是为了抓编辑器里完全断连的孤儿节点）。
- step 可选 `encounter_preset_id`：必须指向某个 encounter_catalog preset 的 `id`。"战斗步骤必须有显式遭遇引用"是编辑器产品契约与 D&D 运行时的要求，loader 只在引用存在性上把关（不强制战斗步骤一定带遭遇）。
- step 可选 `requires`：`"none"`（默认）或 `"combat_ended"`——后者表示该步骤要等其声明的遭遇战斗结束才能推进。值由 D&D campaign engine 消费（`src/rulesets/dnd2024/campaign/engine.py`），loader 不校验值域。
- `scene_ref` 必须解析到包内 scene 实体；scene 的 `map_location_ref` / `npc_refs` 也必须解析。

### v1 实体形状（content/ 下）

- `scene`：`map_location_ref`?、`map_marker_id`?、`npc_refs`[]。
- `npc`：自由业务字段（如 `role`、`disposition`），展示文案在 locale。
- `map_location`：`region_id`?、`markers`[]。
- `encounter_catalog`：见 [dnd2024-encounters.md](dnd2024-encounters.md)。
- choice `outcomes[]`：`{entity_kind, entity_id, visibility, status?}`。`entity_kind` 是封闭词表 `task | clue | fact | item | relationship`（D&D campaign engine 的 `ENTITY_KINDS` 校验；bundle loader 本身不校验它）。选择被采纳时 campaign engine 生成 `dnd2024.campaign.entity_created` 事件——叙事实体产出，不是权威世界状态写入；实体的展示 `title`/`summary` 取自 tutorial `entities` 文案。`task` 可带 `status: "active" | "completed"`。

### tutorial locale 结构（v1 惯例）

`locales/<locale>/adventure.json` 的 `fields.tutorial`：

```json
{
  "name": "标题", "summary": "简介",
  "chapters": {"act1": {"name": "第一章"}},
  "steps": {"step_opening": {"title": "", "narration": "", "objective": "", "hint": ""}},
  "choices": {"choice_go": {"label": "", "description": ""}},
  "entities": {"clue:ash": {"title": "", "summary": ""}}
}
```

这些只是 Coach 展示层文案，不提交 Intent、不进公共时间线。
