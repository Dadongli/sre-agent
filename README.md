# SRE Agent Control Center

面向运维场景的 SRE Agent 初始 MVP，包含后端 API 与前端控制台原型，覆盖以下核心目标：

- **Observability**：统一查看指标、日志、链路与变更上下文。
- **Agent Ops**：监控 agent 自身状态、告警、根因分析、故障预测与自愈流程。
- **Knowledge Base**：检索 SOP、架构文档、复盘与 CMDB 元数据。
- **ChatOps**：让运维人员与管理人员通过自然语言发起查询、操作与状态汇报。

## 技术栈

- **Backend**：Python 3.12 + Django 5
- **Frontend**：React 18 + Vite 5
- **Data**：当前使用内置示例数据，后续可接入 Prometheus/Loki/OpenTelemetry/向量库

## 目录结构

```text
backend/   Django API 与领域服务
frontend/  React 控制台原型
```

## 后端能力

- `GET /api/dashboard/summary/`
  - 返回仪表盘统计卡片、时序指标、故障预测与 ChatOps 指令样例。
- `GET /api/agent/runbook/`
  - 返回四大能力域的 runbook / 产品能力说明。

## 前端页面能力

- 平台首页展示：
  - 核心能力概览
  - 故障预测与自愈建议
  - 指标样例面板
  - ChatOps 指令示例

## 本地启动

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

## 下一步建议

1. 接入 Prometheus / Loki / Tempo / OpenTelemetry 数据源。
2. 增加 Django REST Framework、认证鉴权与 RBAC。
3. 引入异步任务队列，编排根因分析、预测与自愈 workflow。
4. 将知识库检索与 ChatOps Agent 接入真实大模型与向量检索能力。
5. 增加告警策略管理、审计日志与多租户管理界面。
