# 智慧排班 Agent — 半混班智能排班系统

面向生鲜商超的半混班智能排班助手。正式工固定部门排班（早班 8:00–16:00 / 晚班 14:00–22:00 / 两头班 8:00–12:00+17:00–21:00），专业岗（杀鱼、切肉）由 S/A 级师傅稳定覆盖；临时工跨部门混排补位（工作日 18:00–21:00，周末灵活），不从事专业任务。高峰缺口由系统自动推荐补人，店长的人工修改会被记录并统计。当前门店 **90 人（正式工 80 / 临时工 10）**，5 个区域（水产 / 肉类 / 果蔬 / 收银 / 补货）。

## 项目状态

已完成可运行 Demo：后端 FastAPI + SQLite + 确定性排班引擎，前端 React + TypeScript 工作台。当前支持生成 2026-07-13 起一周半混班班表、Agent 解释/候选推荐、人工干预记录、KPI/风险展示和 HC 优化建议。

## 技术栈

| 分层 | 选型 |
| --- | --- |
| 前端 | React 18 + TypeScript + Vite |
| 样式 | 自定义 CSS，高信息密度工作台布局 |
| 状态管理 | React hooks |
| 后端 | Python FastAPI + Pydantic v2 |
| 数据处理 | Python 标准库确定性聚合 |
| 数据库 | SQLite（Demo 阶段，零运维） |
| Agent | 规则兜底解释 + 工具化候选推荐，可替换为 LLM Provider |
| 测试 | unittest（后端核心），可扩展 pytest / Vitest |

## 目录结构

```
scheduling-agent/
├── specs/                      # 规格文档（见下方「文档导航」）
├── backend/
│   ├── app/api/                # schedule / agent / demo / hc API
│   ├── app/data/               # SQLite store + seed loader
│   ├── app/engine/             # 排班生成、候选评分、风险/KPI
│   ├── app/services/           # 需求、排班、Agent、HC 服务
│   ├── app/seed/               # 种子数据（CSV/JSON）
│   └── tests/                  # 后端核心测试
└── frontend/                   # React 工作台
```

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload   # http://localhost:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

API 文档自动生成：`http://localhost:8000/docs`

## 测试

```bash
PYTHONPATH=backend python -m unittest discover -s backend/tests -v
cd frontend && npm run build
```

## 核心机制

排班由**确定性 Python 引擎**算出（需求计算 → 正式工锁定 → 区域保底校验 → 临时工补位 → 候选评分 → 风险检测），LLM 只负责**理解用户意图与生成自然语言解释**，不参与排班决策、且可降级（LLM 不可用时返回模板解释，`is_fallback=true`）。

- 架构与运行时流程：`specs/ARCHITECTURE.md`
- 需求计算与排班算法：`specs/SPEC.md` §7、§8
- Agent 设计（意图 / 工具 / 输出 Schema / 兜底）：`specs/SPEC.md` §6
- HC 优化引擎：`specs/SPEC.md` §11

## 主要接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/schedule/generate` | 生成一周排班 |
| GET | `/api/schedule/{version_id}` | 查询排班版本 |
| PATCH | `/api/schedule/{version_id}/items/{item_id}` | 修改排班并记录干预 |
| POST | `/api/agent/chat` | Agent 对话 |
| POST | `/api/agent/recommend-support` | 推荐临时工支援候选人 |
| POST | `/api/hc/optimize` | 生成 HC 优化建议 |
| POST | `/api/demo/reset` | 重置 Demo 数据 |

## 文档导航

| 文档 | 职责 |
| --- | --- |
| PRD.md | 产品需求（背景、功能需求、业务规则、验收标准） |
| SPEC.md | 技术规格权威（数据契约、算法、Agent、配置） |
| API.md | 接口契约（端点、请求/响应） |
| 数据库表结构设计.md | 存储权威（表结构、DDL、种子） |
| ARCHITECTURE.md | 架构与运行时流程（C4、序列图） |

## 后续增强建议

1. 接入 OpenAI-compatible Provider，将当前模板解释升级为工具调用 Agent。
2. 前端接入图表库，增强缺口热力图和干预原因分布。
3. 为 FastAPI 路由补集成测试，为前端补组件测试。
