# 智慧排班 Agent 半混班 Demo 技术选型文档（终版）

## 1. 文档信息

| 字段 | 内容 |
| --- | --- |
| 产品名称 | 智慧排班 Agent |
| 对应 PRD | `smart-scheduling-agent-semi-mixed-prd-final.md` |
| 文档版本 | v1.2 |
| 文档状态 | 研发交付终版 |
| 创建日期 | 2026-07-11 |
| 技术目标 | 面向单门店半混班场景，构建由 LLM Agent 编排、历史数据驱动、规则可解释的智能排班 Demo |

## 2. 技术栈总览

本项目采用轻量全栈架构：前端负责高信息密度工作台，后端负责数据计算、LLM Agent 编排、排班生成、规则校验和结果持久化。

| 分层 | 技术选型 | 用途 |
| --- | --- | --- |
| 前端框架 | React + TypeScript + Vite | 半混班排班工作台 |
| UI 体系 | Tailwind CSS + shadcn/ui | 页面布局、卡片、弹窗、标签、表格 |
| 图表可视化 | Apache ECharts | 需求热力图、缺口热力图、干预原因分布 |
| 前端请求状态 | TanStack Query | API 请求、缓存、加载态、错误态 |
| 后端框架 | FastAPI + Pydantic | API 服务、数据校验、结构化响应 |
| LLM Agent | LLM Provider Adapter + 工具调用 + 结构化输出 | 排班意图理解、需求推理、策略生成、解释输出 |
| 数据处理 | Python Pandas | 历史数据聚合、峰谷识别、影响因子计算 |
| 本地存储 | SQLite | 排班版本、需求结果、Agent 记录、干预记录 |
| 样例数据 | CSV / JSON | 历史销售、客流、订单、天气、节假日、员工、技能、区域规则 |
| 排班计算 | Python 规则引擎 + 候选人评分 | 专业岗锁定、区域保底、混排补位、风险生成 |
| 测试 | Pytest + Vitest | 后端规则/计算测试、前端组件测试 |
| 本地运行 | Vite Dev Server + FastAPI | 单机开发和演示 |

## 3. 技术方案概述

系统由四个核心能力组成：

1. 数据计算  
   使用 Pandas 读取历史销售、客流、订单、天气、节假日、促销等样例数据，生成分时段、分区域、分任务的用工需求。

2. LLM Agent 编排  
   Agent 理解店长指令，调用数据摘要、需求计算、排班生成、规则校验、补位推荐等工具，并生成可解释结论。

3. 半混班排班  
   Python 排班模块根据需求结果和半混班规则生成班表，确保专业岗稳定、区域保底、混排池补位和工时约束。

4. 工作台展示  
   React 工作台展示需求洞察、KPI、区域保底、周班表、缺口热力图、Agent 解释和人工干预记录。

## 4. 前端选型

### 4.1 React + TypeScript + Vite

前端采用 React 构建单页工作台，TypeScript 约束核心业务对象，Vite 提供本地开发和构建能力。

核心类型包括：

- `DemandSlot`
- `DemandFactor`
- `Employee`
- `ScheduleItem`
- `Candidate`
- `RiskItem`
- `AgentResponse`
- `InterventionRecord`

### 4.2 Tailwind CSS + shadcn/ui

UI 体系用于快速构建后台工作台，并通过统一视觉规则区分不同排班对象：

| 对象 | 视觉规则 |
| --- | --- |
| 专业固定岗 | 深色实线标签 |
| 区域普通岗 | 浅色标签 |
| 混排支援岗 | 虚线标签 |
| 严重风险 | 红色 |
| 警告风险 | 黄色 |
| Agent 推荐 | 蓝色 |
| 高需求时段 | 热力图深色 |

### 4.3 Apache ECharts

用于呈现：

- 区域 x 时段需求热力图。
- 区域 x 时段缺口热力图。
- 高峰/低峰需求强度。
- 干预原因分布。
- 需求因素贡献展示。

### 4.4 TanStack Query

用于管理服务端状态：

- 生成班表。
- 获取需求计算结果。
- 获取排班版本。
- 调用 Agent。
- 修改班次。
- 获取 KPI 和风险。

## 5. 后端选型

### 5.1 FastAPI + Pydantic

FastAPI 作为后端 API 层，负责接收前端请求并编排业务服务。Pydantic 用于请求、响应、LLM 结构化输出和领域对象校验。

后端核心职责：

- 加载样例数据。
- 生成需求计算结果。
- 调用 LLM Agent。
- 执行半混班排班。
- 校验排班风险。
- 保存排班版本和干预记录。
- 返回前端工作台所需数据。

### 5.2 SQLite + CSV/JSON

数据采用两类存储：

| 数据类型 | 存储方式 | 示例 |
| --- | --- | --- |
| 原始样例数据 | CSV / JSON | 历史销售、客流、订单、天气、节假日、员工、技能、区域规则 |
| 运行结果数据 | SQLite | 需求结果、排班版本、排班项、风险、候选人评分、Agent 记录、人工干预 |

SQLite 文件建议路径：

```text
backend/app/data/demo.sqlite
```

### 5.3 Pandas

Pandas 用于历史数据聚合和需求特征生成。

核心计算包括：

- 同星期同时间段客流均值。
- 同星期同时间段交易数均值。
- 区域销售压力。
- 线上订单压力。
- 高峰/低峰识别。
- 周末/节假日影响。
- 天气影响。
- 促销影响。
- 区域/任务级需求人数转换。

## 6. LLM Agent 选型

### 6.1 Agent 职责

LLM Agent 是排班编排层，负责：

- 理解用户自然语言指令。
- 汇总历史数据和影响因子。
- 生成需求判断和排班策略。
- 调用后端工具完成计算和校验。
- 输出排班解释、需求解释、不可调解释和补位建议。

### 6.2 工具调用模式

Agent 通过工具调用完成关键业务动作：

```text
用户输入
  -> Agent 理解意图
  -> get_historical_summary
  -> calculate_demand
  -> generate_schedule
  -> validate_schedule
  -> recommend_support
  -> generate_explanation
```

工具函数由 Python 实现，LLM 负责选择工具、组织推理过程和生成解释。

### 6.3 结构化输出

Agent 输出使用 Pydantic 结构校验，建议字段如下：

```json
{
  "intent": "generate_schedule",
  "summary": "已根据历史客流、周五晚高峰、天气和节假日因素生成下周半混班班表。",
  "demand_reasoning": [],
  "schedule_recommendations": [],
  "risks": [],
  "next_actions": []
}
```

## 7. 需求计算方案

### 7.1 输入数据

- 历史销售。
- 历史客流。
- 历史订单。
- 历史排班。
- 节假日/周末。
- 天气。
- 促销。
- 区域任务配置。

### 7.2 计算流程

1. Pandas 计算历史基线：
   - 同星期同时间段客流均值。
   - 同星期同时间段交易数均值。
   - 区域销售压力。
   - 线上订单压力。
2. 程序计算影响因子：
   - 周末/节假日上浮。
   - 天气影响。
   - 促销影响。
   - 高峰/低峰标记。
3. 生成初始需求人数：
   - 收银需求由客流和交易数驱动。
   - 果蔬/补货需求由销售、补货任务和高峰驱动。
   - 水产/肉类需求由专业任务和保护时段驱动。
4. Agent 读取计算结果和上下文：
   - 解释需求增减原因。
   - 识别异常需求。
   - 输出排班策略建议。

### 7.3 输出结构

```json
{
  "date": "2026-07-17",
  "slot": "17:00-19:00",
  "area_code": "produce",
  "task_code": "restock",
  "required_count": 3,
  "demand_score": 86,
  "confidence": "medium",
  "demand_factors": ["周五晚高峰", "历史客流高", "降雨导致线上订单增加"]
}
```

## 8. 排班计算方案

### 8.1 排班职责分工

| 能力 | 执行方 |
| --- | --- |
| 排班策略生成 | LLM Agent |
| 需求人数计算 | Pandas + Python |
| 专业岗锁定 | Python 规则模块 |
| 区域保底校验 | Python 规则模块 |
| 混排候选人筛选 | Python 排班模块 |
| 候选人评分 | Python 评分模块 |
| KPI 计算 | Python KPI 模块 |
| 解释生成 | LLM Agent |

### 8.2 候选人评分

```text
候选人得分 =
  技能匹配分 * 35
+ 区域熟悉度分 * 20
+ 剩余工时分 * 15
+ 高峰适配分 * 10
+ 主区域不受影响分 * 15
+ 员工偏好分 * 5
- 风险扣分
```

评分结果作为排班决策依据，并进入 Agent 解释上下文。

## 9. 测试方案

### 9.1 后端测试

后端测试使用 Pytest，覆盖：

- 历史数据聚合。
- 高峰/低峰识别。
- 节假日影响。
- 天气影响。
- 需求人数计算。
- 专业岗锁定。
- 区域保底校验。
- 混排候选人筛选。
- 候选人评分。
- Agent 结构化输出校验。
- 干预率计算。

### 9.2 前端测试

前端测试使用 Vitest，覆盖：

- 需求洞察区展示。
- 周班表展示。
- 热力图展示。
- Agent 响应展示。
- 修改原因必填。

## 10. 推荐代码结构

```text
scheduling-agent/
  frontend/
    src/
      components/
      pages/
      api/
      types/
      charts/
  backend/
    app/
      main.py
      schemas/
      services/
        demand_service.py
        schedule_service.py
        agent_service.py
        kpi_service.py
      agent/
        provider.py
        prompts.py
        structured_outputs.py
        tools.py
      scheduling/
        rules.py
        scorer.py
        generator.py
        risks.py
      data/
        seed_loader.py
        sqlite_store.py
        demo.sqlite
      seed/
        employees.json
        areas.json
        historical_sales.csv
        historical_traffic.csv
        online_orders.csv
        weather.csv
        holidays.csv
  docs/
```

## 11. 运行方式

本地运行包含两个进程：

```text
frontend: Vite Dev Server
backend: FastAPI
```

环境变量建议：

```text
LLM_PROVIDER=
LLM_API_KEY=
SQLITE_PATH=backend/app/data/demo.sqlite
SEED_DATA_PATH=backend/app/seed
```

## 12. 最终技术方案

本项目最终采用：

> React + FastAPI + SQLite + CSV/JSON + Pandas + LLM Agent + Python 半混班规则引擎。

其中，Pandas 负责历史数据和影响因子的数值计算，Python 排班工具负责规则校验和候选人评分，LLM Agent 负责编排预测排班流程、理解用户意图、生成排班策略和解释。
