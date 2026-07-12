# 智慧排班 Agent — API 接口文档

## 文档信息

| 字段 | 内容 |
| --- | --- |
| 产品名称 | 智慧排班 Agent |
| 文档版本 | v1.0 |
| API 基础路径 | `http://localhost:8000/api` |
| 数据格式 | JSON (Content-Type: application/json) |
| 字符编码 | UTF-8 |
| 文档状态 | 初稿 |
| 创建日期 | 2026-07-12 |

## 修订历史

| 版本 | 日期 | 修订内容 | 修订人 |
| --- | --- | --- | --- |
| v1.0 | 2026-07-12 | 初始版本 | — |

---

## 1. 接口总览

### 1.1 接口分组

| 分组 | 基础路径 | 说明 |
| --- | --- | --- |
| 排班管理 | `/api/schedule` | 排班生成、查询、修改、KPI、风险 |
| Agent 服务 | `/api/agent` | 对话、需求解释、候选人推荐 |
| Demo 管理 | `/api/demo` | 数据重置、源数据查看 |

### 1.2 接口速查表

| 方法 | 路径 | 说明 | 本页章节 |
| --- | --- | --- | --- |
| POST | `/api/schedule/generate` | 生成排班 | 2.1 |
| GET | `/api/schedule/{version_id}` | 获取排班版本 | 2.2 |
| PATCH | `/api/schedule/{version_id}/items/{item_id}` | 修改排班项 | 2.3 |
| GET | `/api/schedule/{version_id}/kpis` | 获取 KPI | 2.4 |
| GET | `/api/schedule/{version_id}/risks` | 获取风险列表 | 2.5 |
| POST | `/api/agent/message` | Agent 对话 | 3.1 |
| POST | `/api/agent/recommend-support` | 推荐支援候选人 | 3.2 |
| POST | `/api/agent/explain-demand` | 解释需求计算 | 3.3 |
| POST | `/api/demo/reset` | 重置样例数据 | 4.1 |
| GET | `/api/demo/source-data` | 查看历史数据摘要 | 4.2 |

---

## 2. 排班管理 API

### 2.1 生成排班

Agent 编排生成一周半混班排班。该接口依次执行：历史数据摘要 → 需求计算 → 排班生成 → 规则校验 → 风险检测 → KPI 计算 → 解释生成。

```
POST /api/schedule/generate
```

#### 请求参数

| 字段 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| store_id | string | 是 | — | 门店 ID，当前仅支持 `fresh_store_001` |
| week_start | string | 是 | — | 排班周起始日期，格式 `YYYY-MM-DD`，必须为周一 |
| instruction | string | 否 | `""` | 用户自定义排班指令，Agent 会参考该指令生成排班 |

#### 请求示例

```json
{
  "store_id": "fresh_store_001",
  "week_start": "2026-07-13",
  "instruction": "根据历史数据、天气和节假日生成下周半混班班表"
}
```

#### 响应参数

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| version_id | string | 排班版本 ID，格式 `sch_{uuid_short}` |
| agent_summary | string | Agent 总体说明 |
| agent_fallback | boolean | 是否使用了 LLM 降级模式 |
| demand_insights | array[DemandInsight] | 需求洞察摘要（用于前端展示） |
| demand_results | array[DemandResult] | 完整需求计算结果 |
| schedule_items | array[ScheduleItem] | 排班项列表 |
| kpis | KpiResult | KPI 计算结果 |
| risks | array[RiskItem] | 风险列表 |

#### 响应示例

```json
{
  "version_id": "sch_001",
  "agent_summary": "已根据历史客流、周五晚高峰、降雨和周末因素生成下周半混班班表。老王和老陈锁定水产区保护时段，老张和老刘锁定肉类区保护时段；小唐支援周五晚高峰果蔬和收银缺口。",
  "agent_fallback": false,
  "demand_insights": [
    {
      "date": "2026-07-17",
      "weekday": "Friday",
      "slot": "17:00-19:00",
      "area_code": "produce",
      "area_name": "果蔬区",
      "required_count": 3,
      "demand_score": 86,
      "demand_factors": ["周五晚高峰", "历史客流高", "降雨"],
      "priority": "high",
      "confidence": "medium"
    },
    {
      "date": "2026-07-17",
      "weekday": "Friday",
      "slot": "17:00-19:00",
      "area_code": "cashier",
      "area_name": "收银/前场",
      "required_count": 3,
      "demand_score": 82,
      "demand_factors": ["周五晚高峰", "历史客流高", "线上订单增加"],
      "priority": "high",
      "confidence": "high"
    }
  ],
  "demand_results": [
    {
      "id": "dr_001",
      "date": "2026-07-13",
      "weekday": "Monday",
      "slot": "08:00-11:00",
      "area_code": "aquatic",
      "task_code": "fish_butcher",
      "required_count": 1,
      "demand_score": 75,
      "demand_factors": ["早高峰", "历史基线"],
      "priority": "high",
      "confidence": "high",
      "is_protected": true
    }
  ],
  "schedule_items": [
    {
      "id": "si_001",
      "date": "2026-07-13",
      "slot": "08:00-11:00",
      "area_code": "aquatic",
      "area_name": "水产区",
      "task_code": "fish_butcher",
      "task_name": "杀鱼",
      "employee_id": "emp_001",
      "employee_name": "老王",
      "assignment_type": "fixed",
      "assignment_type_label": "专业固定岗",
      "is_protected": true,
      "risk_level": "none",
      "explanation": "老王为水产区S级杀鱼师傅，08:00-11:00为水产保护时段，优先锁定水产区杀鱼岗位",
      "source": "system"
    }
  ],
  "kpis": {
    "professional_coverage_rate": 1.0,
    "baseline_achievement_rate": 0.95,
    "mixed_utilization_rate": 0.28,
    "peak_gap_count": 2,
    "intervention_rate": 0.0
  },
  "risks": [
    {
      "id": "risk_001",
      "type": "peak_gap",
      "level": "warning",
      "description": "周五17:00-19:00果蔬区补货岗位需求3人，当前仅排2人，缺口1人",
      "affected_item_ids": [],
      "suggestion": "可从混排池推荐小唐或小马支援"
    }
  ]
}
```

#### 错误码

| HTTP 状态码 | error_code | 说明 |
| --- | --- | --- |
| 400 | INVALID_REQUEST | week_start 不是周一或日期格式错误 |
| 400 | STORE_NOT_FOUND | store_id 不存在 |
| 422 | VALIDATION_ERROR | 请求体校验失败 |
| 503 | LLM_UNAVAILABLE | LLM 服务不可用，已使用规则兜底（agent_fallback=true） |

---

### 2.2 获取排班版本

获取指定版本的完整排班数据。

```
GET /api/schedule/{version_id}
```

#### 路径参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| version_id | string | 排班版本 ID |

#### 响应

同 `POST /api/schedule/generate` 的响应结构。

#### 错误码

| HTTP 状态码 | error_code | 说明 |
| --- | --- | --- |
| 404 | NOT_FOUND | 版本 ID 不存在 |

---

### 2.3 修改排班项

店长手动修改一条排班项，系统会校验风险并记录干预。

```
PATCH /api/schedule/{version_id}/items/{item_id}
```

#### 路径参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| version_id | string | 排班版本 ID |
| item_id | string | 排班项 ID |

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| after | object | 是 | 修改后的排班项内容（仅需传被修改的字段） |
| reason_code | string | 是 | 修改原因编码，见 2.3.1 |
| reason_text | string | 否 | 修改原因说明（reason_code 为 other 时必填） |
| force | boolean | 否 | 是否忽略严重风险强制修改，默认 false |

##### 2.3.1 reason_code 枚举

| 编码 | 说明 | 触发条件 |
| --- | --- | --- |
| employee_unavailable | 员工实际不可用 | 员工请假、无法到岗 |
| employee_not_fit | 员工不适合该区域 | 虽有技能但不熟练 |
| manager_experience | 店长经验调整 | 店长认为需要更强的人 |
| area_leader_request | 区域负责人要求 | 课组负责人要求留守 |
| operation_change | 临时经营变化 | 促销、到货、客流变化 |
| other | 其他 | 手动输入，reason_text 必填 |

#### 请求示例

```json
{
  "after": {
    "employee_id": "emp_013",
    "employee_name": "小唐",
    "task_code": "restock",
    "slot": "17:00-19:00",
    "area_code": "produce"
  },
  "reason_code": "manager_experience",
  "reason_text": "小唐补货能力更强，适合周五晚高峰"
}
```

#### 响应参数

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| item | ScheduleItem | 修改后的排班项 |
| risks | array[RiskItem] | 修改后可能新增的风险 |
| kpis | KpiResult | 更新后的 KPI |
| intervention_record | InterventionRecord | 本次干预记录 |
| requires_confirmation | boolean | 是否有严重风险需要店长二次确认 |

#### 响应示例

```json
{
  "item": {
    "id": "si_015",
    "date": "2026-07-17",
    "slot": "17:00-19:00",
    "area_code": "produce",
    "area_name": "果蔬区",
    "task_code": "restock",
    "task_name": "补货",
    "employee_id": "emp_013",
    "employee_name": "小唐",
    "assignment_type": "mixed",
    "is_protected": false,
    "risk_level": "none",
    "explanation": "店长手动调整",
    "source": "manual"
  },
  "risks": [],
  "kpis": {
    "professional_coverage_rate": 1.0,
    "baseline_achievement_rate": 0.95,
    "mixed_utilization_rate": 0.30,
    "peak_gap_count": 1,
    "intervention_rate": 0.02
  },
  "intervention_record": {
    "id": "ir_001",
    "schedule_item_id": "si_015",
    "before": {
      "employee_id": "emp_012",
      "employee_name": "小孙",
      "area_code": "produce",
      "task_code": "restock"
    },
    "after": {
      "employee_id": "emp_013",
      "employee_name": "小唐",
      "area_code": "produce",
      "task_code": "restock"
    },
    "reason_code": "manager_experience",
    "reason_text": "小唐补货能力更强，适合周五晚高峰",
    "created_at": "2026-07-12T10:30:00Z"
  },
  "requires_confirmation": false
}
```

#### 错误码

| HTTP 状态码 | error_code | 说明 |
| --- | --- | --- |
| 400 | INVALID_REASON | 修改原因编码不合法 |
| 404 | NOT_FOUND | 版本 ID 或排班项 ID 不存在 |
| 409 | SCHEDULE_CONFLICT | 修改导致严重风险（如保底不足），requires_confirmation=true，需用户确认后重试 |
| 422 | VALIDATION_ERROR | 请求体校验失败 |

---

### 2.4 获取 KPI

获取指定排班版本的 KPI 数据。

```
GET /api/schedule/{version_id}/kpis
```

#### 路径参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| version_id | string | 排班版本 ID |

#### 响应

```json
{
  "professional_coverage_rate": 1.0,
  "baseline_achievement_rate": 0.95,
  "mixed_utilization_rate": 0.28,
  "peak_gap_count": 2,
  "intervention_rate": 0.02
}
```

| 字段 | 类型 | 说明 | 计算方式 |
| --- | --- | --- | --- |
| professional_coverage_rate | number (0-1) | 专业岗覆盖率 | 已由 S/A 人员覆盖的专业岗需求数 / 专业岗总需求数 |
| baseline_achievement_rate | number (0-1) | 区域保底达成率 | 达成保底的区域时段数 / 核心区域时段总数 |
| mixed_utilization_rate | number (0-1) | 混排利用率 | 混排支援工时 / 总排班工时 |
| peak_gap_count | number | 高峰缺口数 | 高峰时段未满足需求人数之和 |
| intervention_rate | number (0-1) | 人工干预率 | 被修改的排班项数 / 系统生成排班项总数 |

---

### 2.5 获取风险列表

获取指定排班版本的所有风险项。

```
GET /api/schedule/{version_id}/risks
```

#### 路径参数

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| version_id | string | 排班版本 ID |

#### 查询参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
| --- | --- | --- | --- | --- |
| level | string | 否 | 全部 | 风险等级过滤：critical / warning / info |

#### 响应

```json
[
  {
    "id": "risk_001",
    "type": "peak_gap",
    "level": "warning",
    "description": "周五17:00-19:00果蔬区补货岗位需求3人，当前仅排2人，缺口1人",
    "affected_item_ids": [],
    "suggestion": "可从混排池推荐小唐或小马支援",
    "created_at": "2026-07-12T10:00:00Z"
  },
  {
    "id": "risk_002",
    "type": "professional_gap",
    "level": "critical",
    "description": "水产区周六08:00-11:00杀鱼岗位无人覆盖",
    "affected_item_ids": ["si_042"],
    "suggestion": "当前无可用S/A级杀鱼师傅，请联系水产区域负责人",
    "created_at": "2026-07-12T10:00:00Z"
  }
]
```

#### RiskItem 字段说明

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | string | 风险唯一标识 |
| type | enum | professional_gap / baseline_shortage / peak_gap / skill_mismatch / overtime / mixed_overuse |
| level | enum | critical（红色）/ warning（黄色）/ info（灰色） |
| description | string | 风险描述 |
| affected_item_ids | array[string] | 受影响的排班项 ID 列表 |
| suggestion | string | 处理建议 |
| created_at | string | 创建时间 (ISO 8601) |

---

## 3. Agent 服务 API

### 3.1 Agent 对话

用户通过自然语言与 Agent 交互，支持需求解释、排班解释、候选人推荐、不可调解释等意图。

```
POST /api/agent/message
```

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| version_id | string | 否 | 当前排班版本 ID（第一次对话可为空） |
| message | string | 是 | 用户输入的自然语言消息 |
| context | object | 否 | 附加上下文，帮助 Agent 理解当前场景 |

##### context 字段

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| selected_date | string | 否 | 用户当前选中的日期 |
| selected_slot | string | 否 | 用户当前选中的时段 |
| selected_area | string | 否 | 用户当前选中的区域 |
| selected_employee | string | 否 | 用户当前选中的员工 ID |

#### 请求示例

```json
{
  "version_id": "sch_001",
  "message": "周五晚高峰果蔬缺人，谁能支援？",
  "context": {
    "selected_date": "2026-07-17",
    "selected_slot": "17:00-19:00"
  }
}
```

#### 响应参数

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| intent | string | 识别到的意图编码 |
| conclusion | string | 结论性文字 |
| reasons | array[string] | 原因列表，每条一句话 |
| candidates | array[CandidateInfo] | 候选人推荐列表（如有） |
| next_actions | array[string] | 下一步操作建议 |
| is_fallback | boolean | 是否因 LLM 不可用而使用了规则兜底 |

##### intent 枚举

| 编码 | 对应场景 |
| --- | --- |
| generate_schedule | 生成排班 |
| explain_demand | 解释需求原因 |
| explain_fixed | 解释固定岗原因 |
| recommend_support | 推荐支援候选人 |
| explain_blocked | 解释不可调原因 |
| list_risks | 列出风险 |
| reduce_intervention | 减少干预建议 |
| unknown | 未识别的意图 |

##### CandidateInfo

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| employee_name | string | 员工姓名 |
| skills | array[string] | 相关技能列表 |
| score | number (0-100) | 综合评分 |
| recommended | boolean | 是否为最优推荐 |
| reason | string | 推荐或不推荐的原因 |
| risks | array[string] | 该候选人存在的风险 |

#### 响应示例

```json
{
  "intent": "recommend_support",
  "conclusion": "建议优先安排小唐支援周五17:00-19:00果蔬区，可同时覆盖补货和称重需求",
  "reasons": [
    "小唐具备果蔬A、补货A、打包A技能，可独立完成该时段通用任务",
    "小唐当前周工时16小时，未超过32小时上限，剩余工时充足",
    "该安排不影响水产、肉类保护时段的专业岗保底"
  ],
  "candidates": [
    {
      "employee_name": "小唐",
      "skills": ["收银A", "补货A", "果蔬A", "打包A"],
      "score": 92,
      "recommended": true,
      "reason": "技能全面，工时充足，不影响任何区域保底，是当前最优选择",
      "risks": []
    },
    {
      "employee_name": "小马",
      "skills": ["称重B", "打包B", "基础补货B"],
      "score": 68,
      "recommended": false,
      "reason": "可做称重和打包，但不建议独立处理高峰补货任务",
      "risks": ["技能等级B，独立处理高峰能力不足"]
    },
    {
      "employee_name": "老王",
      "skills": ["杀鱼S", "水产处理S", "称重A"],
      "score": 45,
      "recommended": false,
      "reason": "老王为水产区S级杀鱼师傅，当前时段为水产保护时段，不能跨区抽调",
      "risks": ["保护时段不可抽调", "抽调会导致水产区保底不足"]
    }
  ],
  "next_actions": [
    "点击\"应用推荐\"安排小唐支援果蔬区",
    "查看小马的详细能力",
    "查看其他候选人的排班情况"
  ],
  "is_fallback": false
}
```

#### 错误码

| HTTP 状态码 | error_code | 说明 |
| --- | --- | --- |
| 400 | INVALID_REQUEST | 消息为空或格式错误 |
| 404 | VERSION_NOT_FOUND | 版本 ID 不存在 |
| 503 | LLM_UNAVAILABLE | LLM 服务不可用，使用规则兜底（is_fallback=true） |

---

### 3.2 推荐支援候选人

针对特定缺口，直接返回候选人列表（跳过 LLM 解释，用于前端快速获取数据）。

```
POST /api/agent/recommend-support
```

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| version_id | string | 是 | 排班版本 ID |
| date | string | 是 | 日期 YYYY-MM-DD |
| slot | string | 是 | 时段，如 `17:00-19:00` |
| area_code | string | 是 | 区域编码 |
| task_code | string | 是 | 任务编码 |
| exclude_employee_ids | array[string] | 否 | 需排除的员工 ID 列表 |

#### 请求示例

```json
{
  "version_id": "sch_001",
  "date": "2026-07-17",
  "slot": "17:00-19:00",
  "area_code": "produce",
  "task_code": "restock",
  "exclude_employee_ids": ["emp_012"]
}
```

#### 响应

```json
{
  "gap": {
    "date": "2026-07-17",
    "slot": "17:00-19:00",
    "area_code": "produce",
    "task_code": "restock",
    "required_count": 3,
    "current_count": 2,
    "gap_count": 1
  },
  "candidates": [
    {
      "employee_name": "小唐",
      "skills": ["收银A", "补货A", "果蔬A", "打包A"],
      "score": 92,
      "recommended": true,
      "reason": "技能全面，工时充足",
      "risks": []
    }
  ]
}
```

---

### 3.3 解释需求计算

针对特定时段和区域，解释需求计算的依据。

```
POST /api/agent/explain-demand
```

#### 请求参数

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| version_id | string | 是 | 排班版本 ID |
| date | string | 是 | 日期 YYYY-MM-DD |
| slot | string | 是 | 时段 |
| area_code | string | 是 | 区域编码 |
| question | string | 否 | 用户附加问题 |

#### 请求示例

```json
{
  "version_id": "sch_001",
  "date": "2026-07-17",
  "slot": "17:00-19:00",
  "area_code": "produce",
  "question": "说明这个时段果蔬区的人力需求依据"
}
```

#### 响应

```json
{
  "answer": "周五17:00-19:00是晚高峰时段，该时段历史客流均值比普通工作日高28%，果蔬销售高35%；同时当天预报有降雨，线上订单和打包任务预计增加15%。综合以上因素，果蔬区补货、称重和打包需求上升，建议配置3人。",
  "factors": [
    "周五晚高峰：历史客流高于均值28%",
    "果蔬销售高：历史销售高于均值35%",
    "降雨：线上订单预计增加15%，到店客流影响可忽略",
    "周末效应：周五为周末前夜，备货需求增加"
  ],
  "confidence": "medium",
  "data_summary": {
    "historical_avg_traffic": 312,
    "current_forecast_traffic": 399,
    "historical_avg_sales": 4520.00,
    "holiday_factor": 1.0,
    "weather_factor": 1.15,
    "promotion_factor": 1.0,
    "base_demand": 2,
    "final_demand": 3
  }
}
```

---

## 4. Demo 管理 API

### 4.1 重置样例数据

清空所有运行时数据（需求结果、排班版本、排班项、风险、干预记录、Agent 记录），重新从 CSV/JSON 加载静态配置数据。

```
POST /api/demo/reset
```

#### 请求参数

无

#### 响应

```json
{
  "status": "ok",
  "message": "样例数据已重置",
  "loaded_tables": [
    "employees",
    "areas",
    "area_tasks",
    "skill_definitions",
    "employee_skills",
    "modified_reasons"
  ],
  "cleared_tables": [
    "demand_results",
    "schedule_versions",
    "schedule_items",
    "candidate_scores",
    "risk_items",
    "intervention_records",
    "agent_messages"
  ],
  "timestamp": "2026-07-12T10:00:00Z"
}
```

---

### 4.2 查看历史数据摘要

查看当前加载的样例数据摘要信息。

```
GET /api/demo/source-data
```

#### 查询参数

无

#### 响应

```json
{
  "store": {
    "store_id": "fresh_store_001",
    "store_name": "鲜生活超市-望京店",
    "address": "北京市朝阳区望京街道XX号"
  },
  "employees_count": 14,
  "employee_types": {
    "professional": 4,
    "regional": 2,
    "mixed": 6,
    "floating": 2
  },
  "areas": [
    {"code": "aquatic", "name": "水产区", "tasks_count": 4},
    {"code": "meat", "name": "肉类区", "tasks_count": 3},
    {"code": "produce", "name": "果蔬区", "tasks_count": 3},
    {"code": "cashier", "name": "收银/前场", "tasks_count": 2},
    {"code": "replenishment", "name": "补货区", "tasks_count": 2}
  ],
  "historical_data_range": {
    "sales_start": "2026-01-01",
    "sales_end": "2026-06-30",
    "total_records": 5430
  },
  "holidays_count": 12,
  "promotions_count": 8,
  "last_reset": "2026-07-12T10:00:00Z"
}
```

---

---

## 6. 错误处理

### 6.1 统一错误响应格式

所有错误响应使用统一格式：

```json
{
  "error_code": "ERROR_CODE",
  "message": "人类可读的错误描述",
  "details": {
    "field": "具体错误字段",
    "constraint": "违反的约束"
  },
  "request_id": "req_uuid"
}
```

| 字段 | 类型 | 必填 | 说明 |
| --- | --- | --- | --- |
| error_code | string | 是 | 机器可读的错误编码 |
| message | string | 是 | 人类可读的错误描述 |
| details | object | 否 | 错误详情，可用于前端定位 |
| request_id | string | 否 | 请求追踪 ID |

### 6.2 错误码全集

| HTTP 状态码 | error_code | 说明 | 触发场景 |
| --- | --- | --- | --- |
| 400 | INVALID_REQUEST | 请求参数错误 | 日期格式错误、编码不合法 |
| 400 | STORE_NOT_FOUND | 门店不存在 | store_id 无效 |
| 400 | INVALID_REASON | 修改原因不合法 | reason_code 不存在 |
| 404 | NOT_FOUND | 资源不存在 | 版本 ID/排班项 ID 无效 |
| 404 | VERSION_NOT_FOUND | 版本 ID 不存在 | Agent 请求中的 version_id 无效 |
| 409 | SCHEDULE_CONFLICT | 排班冲突 | 修改导致保底不足/专业岗缺失 |
| 422 | VALIDATION_ERROR | 请求体验证失败 | Pydantic 校验失败 |
| 500 | INTERNAL_ERROR | 内部错误 | 未预期的异常 |
| 503 | LLM_UNAVAILABLE | LLM 服务不可用 | LLM 调用失败，已降级 |

### 6.3 校验错误详情格式

422 VALIDATION_ERROR 的 details 格式：

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "请求参数校验失败",
  "details": {
    "errors": [
      {
        "field": "week_start",
        "message": "week_start 必须为周一 (YYYY-MM-DD)",
        "received": "2026-07-12"
      },
      {
        "field": "store_id",
        "message": "store_id 不能为空",
        "received": ""
      }
    ]
  },
  "request_id": "req_abc123"
}
```

---

---

## 8. 调用限制

| 限制项 | 值 |
| --- | --- |
| 请求体大小上限 | 1MB |
| 响应超时 | 30s (生成排班) / 10s (其他) |

---


