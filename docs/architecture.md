# SRE Agent MVP Architecture

## 1. Product Scope

本项目首期目标是提供一个 **SRE Agent Control Center**，支持以下典型运维工作流：

1. **Observability**：统一采集与展示指标、日志、链路、事件与变更。
2. **Agent Ops**：监控 agent 本身的健康度、告警、根因分析、故障预测与自愈执行闭环。
3. **Knowledge Base**：支持 SOP、复盘、CMDB、架构文档等知识检索与引用。
4. **ChatOps**：通过对话式交互完成指标查询、日志定位、故障诊断、执行 runbook 和生成管理汇报。

## 2. Technical Architecture

### Frontend

- React + Vite 控制台
- 能力模块：
  - 总览仪表盘
  - 告警中心
  - 故障预测与自愈编排
  - 知识库检索中心
  - ChatOps 对话台

### Backend

- Django 项目承载：
  - API 网关层
  - 领域服务层
  - 后续可扩展为 Django REST Framework
- 领域拆分建议：
  - `observability`
  - `incident`
  - `automation`
  - `knowledge`
  - `chatops`
  - `governance`

## 3. Agent Workflow

1. **Signal Ingestion**：采集 Prometheus / Loki / Tempo / 云监控 / CMDB / 发布事件。
2. **Context Builder**：构建服务拓扑、依赖链路、异常上下文。
3. **Diagnosis Agent**：产出根因分析假设与置信度。
4. **Prediction Agent**：根据时序与历史事件预测故障风险。
5. **Action Agent**：执行受控自愈动作，写回审计日志。
6. **ChatOps Agent**：提供面向运维和管理层的自然语言交互入口。

## 4. Milestones

### Phase 1: MVP

- 控制台首页与核心能力展示
- 基础 API
- 示例时序数据 / 故障预测数据 / ChatOps 示例命令

### Phase 2: Operationalization

- 接入真实可观测数据源
- 告警策略与通知渠道
- 基于知识库的 RAG 检索
- 自愈审批流与操作审计

### Phase 3: Intelligence

- 多 agent 协同
- 历史事件学习
- 变更风险评估
- 管理层日报/周报自动生成
