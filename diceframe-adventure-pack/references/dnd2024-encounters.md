# D&D 5e 2024（`core:dnd2024`）遭遇

真值来源：`src/rulesets/dnd2024/adventure_validation.py`（注册于 `core:dnd2024`）、`src/adventures/bundle.py`、`src/rulesets/dnd2024/play/contracts.py`。manifest 写 `"required_runtime": {"id": "core:dnd2024", "minimum_version": 1}` 的包在加载时会自动走 D&D 数值校验（runtime 未加载时 mechanics 校验为 unresolved，安装/运行侧决定是否阻断——不要赌它）。

D&D 遭遇有**两条不同的链路**，按图格式区分：

| | graph v1 | graph v2 |
|---|---|---|
| 声明位置 | step 的 `encounter_preset_id` 指向包内 `encounter_catalog` 实体的 preset | 节点的 `encounter_ref: "encounter_profile:<id>"` 指向 **D&D 内容模块/内容库**里的 encounter_profile |
| 敌人数值 | 内联在包内 catalog（hp/armor_class/attacks…） | 不在冒险包内；profile 经 content ref（`{"ref": {"source", "kind": "monster", "id"}, "count"}`）引用怪物档案 |
| 运行时 | `resolve_story_encounter_access`（v1 tutorial step 路径） | active 节点的 `encounter_ref` 推导遭遇访问（pending/active/resolved） |

## encounter_catalog 实体（graph v1 包内）

```json
{
  "schema_version": 1,
  "kind": "encounter_catalog",
  "id": "my_encounters",
  "source_ref": "diceframe-original:my-quest",
  "automation_level": "deterministic",
  "presets": [
    {
      "id": "first_skirmish",
      "difficulty": "standard",
      "enemies": [
        {
          "id": "goblin-minion-1",
          "profile_id": "goblin_minion",
          "hp": 7, "armor_class": 12, "speed": 30, "position": 25,
          "initiative_modifier": 2,
          "abilities": {"str": 8, "dex": 15, "con": 10, "int": 10, "wis": 8, "cha": 8},
          "saving_throws": {"str": -1, "dex": 2, "con": 0, "int": 0, "wis": -1, "cha": -1},
          "attacks": [
            {"id": "dagger", "attack_bonus": 4, "damage": "1d4+2",
             "damage_type": "piercing", "range": 5, "long_range": 60}
          ]
        }
      ]
    }
  ]
}
```

## preset 结构规则（仅 graph v1：`_validate_graph` 只在 v1 路径运行）

- `id`：`^[a-z0-9][a-z0-9_.-]*$`，catalog 内唯一；step 的 `encounter_preset_id`（v1）按这个 id 引用。
- `difficulty` ∈ `story | standard | challenging | lethal`。
- `enemies` 非空数组，每个 enemy 的 `id`、`profile_id` 必填。

## 敌人数值边界（D&D validator：包内任何 encounter_catalog 实体，v1/v2 格式都查）

| 字段 | 约束 |
|---|---|
| `hp` | **int**，1 – 100000 |
| `armor_class` | **int**，1 – 40 |
| `attacks` | 非空数组 |
| `attacks[].id` / `damage` | 非空字符串（damage 如 `"1d4+2"`） |
| `attacks[].attack_bonus` | **int**，−20 – 20 |

注意 `_bounded_int` 要求真正的 JSON 整数：`"hp": "7"`（字符串）或 `7.5`（浮点）都会被拒。数值要符合 5e 语义（HP/AC/加值与怪物 CR 大体匹配），但系统只做边界校验，不做平衡性校验——平衡由创作者负责。

## graph v2 包的遭遇（重要：不要把 catalog 塞进 v2 包）

v2 遭遇节点的 `encounter_ref` 用 **`encounter_profile:<id>`**，profile 定义在 D&D 内容模块里（`kind: "encounter_profile"`，含 `difficulty` 和 `enemies: [{"ref": {"source", "kind", "id"}, "count"}]`），怪物档案也来自内容库。遭遇的开启/结束由运行时根据当前 active 节点推导；节点声明了遭遇却没有可用的 canonical profile 时，运行时报"unprepared"，**不会**拿通用训练目录的预设顶上——所以引用的 profile 必须真实存在于已装载的内容源。

两个边界：

- generic loader 对 `encounter_ref` 默认只校验 `kind:id` 格式（不查 profile 存在性，它在包外）。
- 若 manifest 声明 `reference_policy: "adventure-local"`，loader 会要求 `encounter_ref` 是 `encounter_catalog:<包内id>`——这与 D&D v2 的 `encounter_profile:` 路径不兼容；adventure-local 是为自包含通用导入包设计的，v2 D&D 遭遇包不要声明它。

