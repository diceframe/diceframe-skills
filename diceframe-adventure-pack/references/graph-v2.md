# graph v2 完整契约（`diceframe:adventure-graph-v2`）

真值来源：`src/adventures/graph_v2.py`、`src/adventures/gates.py`、`src/adventures/outcomes.py`。未知字段 / 未知类型一律 fail closed。

## adventure 实体字段白名单

```text
图字段        chapters, nodes, objectives, milestones, start_node_ids, visibility, world_seed
envelope      schema_version, kind, id, source_ref, automation_level
展示/元数据   format, name, summary, tutorial, estimated_minutes,
              recommended_level, player_count, world_policy, recommended_world_id
```

- `schema_version`：1 或 2（用 1 即可；schema 2 才允许节点带 `choice_mode`）。
- `format` 必须等于 `diceframe:adventure-graph-v2`。
- `visibility` ∈ `public | gm`；整个包为 `gm` 时玩家不可见（`available: false`）。

## chapters（≤32）

`{"id", "name"?, "visibility"?}`。成员关系由节点的 `chapter_id` 表达（不做 v1 式双向清单，节点可以不属于任何章节）。public 节点的 `chapter_id` 不能指向 gm 章节。

## nodes（≤256）

| 字段 | 说明 |
|---|---|
| `id` | 唯一，`^[a-z0-9][a-z0-9_.-]*$` |
| `type` | `scene \| objective \| encounter \| decision \| milestone \| reference` |
| `chapter_id`? | 必须指向存在的章节 |
| `visibility`? | 默认 `public`；玩家投影只保留 public 内容 |
| `optional`? | 可选节点（不影响结束判定时用） |
| `name`? / `description`? | 展示文案（canonical 包内文案；locale 再覆盖） |
| `transitions`? | ≤16 条，见下 |
| `on_complete`? | ≤16 条 outcome，见下 |
| `scene_ref`? | `scene:<id>`，格式 `^[a-z0-9][a-z0-9_.-]*:[a-z0-9][a-z0-9_.-]*$`。**默认只校验格式、不校验存在性**——可以指向包外世界实体；manifest 声明 `"reference_policy": "adventure-local"` 时改为强制包内解析，悬空即拒 |
| `npc_refs`? | ≤16 条 `npc:<id>`，存在性策略同 `scene_ref` |
| `encounter_ref`? | D&D v2 遭遇用 `encounter_profile:<id>` 指向**内容库**档案（不在包内，见 [dnd2024-encounters.md](dnd2024-encounters.md)）；generic loader 只校验 `kind:id` 格式；`core:adventure` profile 禁止任何 encounter_ref |
| `choice_mode`? | 仅 schema_version=2：`parallel`（默认）\| `exclusive` |

### transitions

```json
{"to": "next_node", "conditions": [{"type": "world.fact_equals", "key": "gate.open", "value": true}]}
```

- `to` 必须存在；回流合法（不要求 DAG，但遍历计算有 512 步上限）。
- `conditions` ≤8 条，AND 语义；空 = 恒开放。**证据不足 = 不满足**（rules adapter 缺席、世界读取失败都按 False），所以不要把唯一必经之路放在可能永远无法满足的门槛后。
- `choice_mode: "exclusive"` 时每条 transition 还要 `choice_id`（≤128 字符，节点内唯一）+ `choice_label`（1–256 字符）——排他分支的稳定身份，不要用索引或文案当身份。

### gate 词表（conditions 的类型封闭）

| type | 字段 | 含义 |
|---|---|---|
| `world.fact_equals` | `key`, `value` | 世界事实等于期望值 |
| `world.entity_status` | `id`, `value` | 世界实体状态 |
| `world.relation_status` | `id`, `value` | 世界关系状态 |
| `world.process_status` | `id`, `value` | 世界进程状态 |
| `adventure.milestone` | `id`, `value`? | 里程碑已完成（id 在 completed_milestones 中） |
| `adventure.objective_status` | `id`, `value` | 目标状态 `completed`/`active` |
| `rules.outcome` | `id`, `value` | 规则检定结果（需 runtime adapter；通用包禁止） |
| `rules.party_level` | `id`, `value` | 队伍等级（同上） |
| `rules.item_possession` | `id`, `value` | 持有物品（同上） |

gate 只允许 `type` + `key`/`id`（按类型二选一）+ `value`，没有表达式、没有嵌套——不是 DSL，刻意不做成 DSL。

## on_complete outcome 词表（唯一效果归属点）

| type | 字段 | 说明 |
|---|---|---|
| `world_op` | `op: {op: <op名>, ...}` | 提案世界操作；op 词表即 `world_state.OP_KINDS`：`set_fact`/`remove_fact`/`advance_time`/`schedule_event`/`cancel_event`/`register_entity`/`retire_entity`/`add_relation`/`set_relation_status`/`remove_relation`/`start_process`/`complete_process`/`cancel_process`/`fail_process`（另有 `complete_event` 仅由服务端结算写入，**创作者不要写它**）。载荷在物化时由 `apply_world_ops` fail closed 校验 |
| `item_reward` | `ref`, `recipient_uid`? | 奖励提案（D&D reward 桥执行）；`core:adventure` profile 禁止 |
| `progress_event` | `kind` ∈ `node_completed\|objective_completed\|milestone_reached`, `id` | 进度事件 |

没有 on_enter / on_leave / transition effects——效果只发生在节点完成时，这是防止 scope 爆炸的刻意约束。

## objectives / milestones（各 ≤64）

`{"id", "name"?, "visibility"?, "node_ids": [...]}`。可并行；`node_ids` 必须存在；public 目标不能引用 gm 节点；id 重复拒绝。

## start_node_ids（1–16）

多入口；必须都存在。

## world_seed（可选，开局世界种子）

```json
{
  "entities":   [{"entity_id": "npc:mira", "kind": "npc", "visibility": "public", "source_ref": "..."}],
  "relations":  [{"relation_id": "rel:1", "kind": "<RELATION_KINDS 之一>", "from_ref": "...", "to_ref": "..."}],
  "facts":      [{"key": "lamp.lit", "value": false, "visibility": "public"}],
  "processes":  [{"process_id": "proc:1", "kind": "ritual", "participants": [], "location": "", "due_at": ""}]
}
```

上界 128/128/128/32；字段封闭（如上，多余字段拒绝）；`kind` 用词表参考 `src/engine/world/contracts.py` 的 `ENTITY_KINDS` / `RELATION_KINDS`。种子只是结构声明，最终合法性在物化时由 `apply_world_ops` 把关。

## core:adventure 通用叙事 profile 的额外禁令

（`src/adventures/narrative_validation.py`，manifest `required_runtime.id = "core:adventure"` 时强制）

- 必须 graph v2。
- 不得有 `type: "encounter"` 节点或任何 `encounter_ref`。
- 不得有 `rules.*` gate。
- 不得有 `item_reward` outcome。
- `encounter / encounter_catalog / item / reward` 实体只能 `automation_level: "reference"`，且字段 ⊆ `{schema_version, kind, id, source_ref, automation_level, visibility, name, description, source_record}`（外来数值资料作惰性证据保存，`source_record` 放原始 JSON 字符串）。

## 玩家投影语义（设计时要知道）

`project_graph_v2` 对玩家：只保留 public 节点/目标/里程碑/章节；指向隐藏节点的 transition 一并丢弃；节点投影**剥掉** `on_complete`、`npc_refs`、`encounter_ref`（id 本身就是剧透）。所以 GM 秘密写在 gm 可见性 + on_complete 里是安全的，写在 public 节点的 description 里不安全。

## 与 v1 校验的差异（容易踩的坑）

- v1 会强制检查 step `scene_ref`、`encounter_preset_id` 以及 scene 实体的 `map_location_ref`/`npc_refs` 存在；v2 的 generic loader **不检查** scene 实体自身的 `map_location_ref`/`npc_refs`。写 v2 包时保持这些引用有效（指向包内实体或已知世界实体），不要依赖 loader 兜底。
- v1 要求全图从 `start_step_id` 可达；v2 没有可达性检查，回流合法。孤儿节点要靠创作者自查（管理后台校验会报不可达/无出口步骤）。
- v1 章节成员双向强制清单；v2 只看节点 `chapter_id`，节点可以不属于任何章节。
