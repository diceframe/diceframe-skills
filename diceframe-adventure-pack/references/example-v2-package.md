# 完整最小 v2 通用包示例（已通过生产 loader 校验）

一个 `core:adventure` + graph v2 的最小但完整的包，5 个节点、门槛、world_op、progress_event、objective/milestone、locale 覆盖齐全。以下内容逐文件照抄即可加载。创作新包时以此骨架为起点，替换文案与图结构。

## 目录布局

```text
v2_lamp_quest/
├─ manifest.json
├─ adventure.json
├─ content/
│  ├─ scenes/foggy_crossing.json
│  ├─ npcs/lampkeeper.json
│  └─ map_locations/lamp_hill.json
└─ locales/zh-CN/
   ├─ adventure.json
   ├─ scenes/foggy_crossing.json
   ├─ npcs/lampkeeper.json
   └─ map_locations/lamp_hill.json
```

## manifest.json

```json
{
  "schema_version": 1,
  "adventure_id": "user:v2_lamp_quest",
  "version": "1.0.0",
  "format": "diceframe:adventure-graph-v2",
  "world_policy": "agnostic",
  "required_runtime": {"id": "core:adventure", "minimum_version": 1},
  "default_locale": "zh-CN",
  "supported_locales": ["zh-CN"]
}
```

`agnostic` 表示不依赖具体世界；如果剧情绑定某个世界的地点/NPC，用 `portable`（加 `recommended_world_id` 提示适配）或 `fixed`（强制世界匹配）。

## adventure.json（envelope + 图）

```json
{
  "schema_version": 1,
  "kind": "adventure",
  "id": "v2_lamp_quest",
  "format": "diceframe:adventure-graph-v2",
  "source_ref": "diceframe-original:examples/v2-lamp-quest",
  "automation_level": "guided",
  "estimated_minutes": 45,
  "world_policy": "agnostic",
  "name": "雾灯疑云",
  "summary": "一段 45 分钟的通用叙事短冒险：查明路口指路灯熄灭的原因，并决定如何了结。",
  "chapters": [
    {"id": "ch_arrival", "name": "抵达路口"},
    {"id": "ch_resolution", "name": "了结"}
  ],
  "nodes": [
    {
      "id": "arrive_crossing", "type": "scene", "chapter_id": "ch_arrival",
      "name": "雾中路口",
      "description": "入夜的山道岔口，指路灯已经熄灭，雾里传来脚步声。",
      "scene_ref": "scene:foggy_crossing",
      "npc_refs": ["npc:lampkeeper"],
      "transitions": [{"to": "hear_the_plea"}],
      "on_complete": [{"type": "progress_event", "kind": "node_completed", "id": "arrive_crossing"}]
    },
    {
      "id": "hear_the_plea", "type": "decision", "chapter_id": "ch_arrival",
      "name": "守灯人的请求",
      "description": "守灯人塔莎请求旅人代她登上灯塔回填灯油。",
      "transitions": [
        {"to": "climb_tower", "conditions": [{"type": "world.fact_equals", "key": "lamp.quest_accepted", "value": true}]},
        {"to": "leave_darkly"}
      ],
      "on_complete": [{"type": "world_op", "op": {"op": "set_fact", "key": "lamp.quest_accepted", "value": true}}]
    },
    {
      "id": "leave_darkly", "type": "scene", "chapter_id": "ch_arrival", "optional": true,
      "name": "婉拒离开",
      "description": "旅人绕开灯塔，继续赶路；雾灯依旧熄着。",
      "transitions": []
    },
    {
      "id": "climb_tower", "type": "scene", "chapter_id": "ch_resolution",
      "name": "登上灯塔",
      "description": "旋梯尽头的灯室积着冷灰，灯芯完好，只是油早已干涸。",
      "transitions": [{"to": "relight"}],
      "on_complete": [{"type": "progress_event", "kind": "objective_completed", "id": "obj_relight"}]
    },
    {
      "id": "relight", "type": "milestone", "chapter_id": "ch_resolution",
      "name": "重燃雾灯",
      "transitions": [],
      "on_complete": [
        {"type": "world_op", "op": {"op": "set_fact", "key": "lamp.relit", "value": true}},
        {"type": "progress_event", "kind": "milestone_reached", "id": "mile_relit"}
      ]
    }
  ],
  "objectives": [{"id": "obj_relight", "name": "重燃路口的雾灯", "node_ids": ["climb_tower", "relight"]}],
  "milestones": [{"id": "mile_relit", "name": "雾灯复明", "node_ids": ["relight"]}],
  "start_node_ids": ["arrive_crossing"]
}
```

图语义：接下请求（`hear_the_plea` 完成）会写 `lamp.quest_accepted=true`，从而打开通往 `climb_tower` 的门槛；婉拒则走可选支线 `leave_darkly`（无出口，支线结局）。同一节点完成后门槛才满足，这是 v2 的标准"完成节点 → 评估 gate → 开放后继"节奏。

## content 实体

`content/scenes/foggy_crossing.json`：

```json
{
  "schema_version": 1,
  "kind": "scene",
  "id": "foggy_crossing",
  "source_ref": "diceframe-original:examples/v2-lamp-quest",
  "automation_level": "guided",
  "map_location_ref": "map_location:lamp_hill",
  "npc_refs": []
}
```

`content/npcs/lampkeeper.json`：

```json
{
  "schema_version": 1,
  "kind": "npc",
  "id": "lampkeeper",
  "source_ref": "diceframe-original:examples/v2-lamp-quest",
  "automation_level": "guided",
  "role": "keeper",
  "disposition": "anxious_ally"
}
```

`content/map_locations/lamp_hill.json`：

```json
{
  "schema_version": 1,
  "kind": "map_location",
  "id": "lamp_hill",
  "source_ref": "diceframe-original:examples/v2-lamp-quest",
  "automation_level": "reference",
  "region_id": "mist_valley",
  "markers": ["foggy_crossing", "lamp_tower"]
}
```

实体文件只放结构字段；名称与描述全部走 locale 层。

## locales/zh-CN/

`locales/zh-CN/adventure.json`（`tutorial` 是自由结构的展示文案对象）：

```json
{
  "locale_schema_version": 1,
  "locale": "zh-CN",
  "target": {"kind": "adventure", "id": "v2_lamp_quest"},
  "fields": {
    "tutorial": {
      "chapters": {
        "ch_arrival": {"name": "第一章：抵达路口"},
        "ch_resolution": {"name": "第二章：了结"}
      }
    }
  }
}
```

`locales/zh-CN/scenes/foggy_crossing.json`：

```json
{
  "locale_schema_version": 1,
  "locale": "zh-CN",
  "target": {"kind": "scene", "id": "foggy_crossing"},
  "fields": {"name": "雾中岔口", "description": "山道在此分岔，熄灭的指路灯柱立在雾里。"}
}
```

`locales/zh-CN/npcs/lampkeeper.json`：

```json
{
  "locale_schema_version": 1,
  "locale": "zh-CN",
  "target": {"kind": "npc", "id": "lampkeeper"},
  "fields": {"name": "塔莎", "description": "年轻的山道守灯人，为自己的腿伤无法登塔而焦急。"}
}
```

`locales/zh-CN/map_locations/lamp_hill.json`：

```json
{
  "locale_schema_version": 1,
  "locale": "zh-CN",
  "target": {"kind": "map_location", "id": "lamp_hill"},
  "fields": {"name": "灯丘", "description": "岔口与灯塔所在的山丘。"}
}
```

注意 manifest 声明的每个 locale 都必须有 `locales/<locale>/` 目录（哪怕只放 adventure.json 一个文件，甚至为空目录）。

## 加载预期

用 `scripts/validate_pack.py` 校验应输出：4 个实体（adventure/scene/npc/map_location 各 1）、`runtime=core:adventure>=1`、一个 `sha256:...` 的 content_digest。若在 manifest 加回 `"reference_policy": "adventure-local"`，本包所有引用均在包内，仍应通过；把 `scene_ref` 改成不存在的 id 则报 `unresolved local reference: scene:...`。
