import { useMemo, useState } from 'react'
import { Section } from './components/Section'
import { StatCard } from './components/StatCard'
import {
  capabilityHighlights,
  chatopsPresets,
  dashboard,
  knowledgeDocuments,
  navigation,
  quickActions,
  runbook,
  serviceHealth,
  workbenchTabs,
} from './lib/mockData'

function App() {
  const [activeTab, setActiveTab] = useState(workbenchTabs[0].key)
  const [serviceFilter, setServiceFilter] = useState('all')
  const [selectedAction, setSelectedAction] = useState(quickActions[0].title)
  const [chatInput, setChatInput] = useState(chatopsPresets[0].prompt)
  const [chatHistory, setChatHistory] = useState([
    {
      role: 'assistant',
      text: '已加载今日值班上下文：2 个高风险服务、7 条活跃告警、1 条待确认自愈动作。',
    },
  ])
  const [knowledgeQuery, setKnowledgeQuery] = useState('runbook')

  const filteredServices = useMemo(() => {
    if (serviceFilter === 'all') {
      return serviceHealth
    }

    return serviceHealth.filter((service) => service.statusTone === serviceFilter)
  }, [serviceFilter])

  const activeWorkbench = useMemo(
    () => workbenchTabs.find((tab) => tab.key === activeTab) ?? workbenchTabs[0],
    [activeTab],
  )

  const quickActionDetail = useMemo(
    () => quickActions.find((action) => action.title === selectedAction) ?? quickActions[0],
    [selectedAction],
  )

  const filteredKnowledgeDocs = useMemo(() => {
    const query = knowledgeQuery.trim().toLowerCase()

    if (!query) {
      return knowledgeDocuments
    }

    return knowledgeDocuments.filter((doc) => {
      const searchable = `${doc.title} ${doc.summary} ${doc.tags.join(' ')}`.toLowerCase()
      return searchable.includes(query)
    })
  }, [knowledgeQuery])

  const serviceOverview = useMemo(() => {
    const healthy = serviceHealth.filter((service) => service.statusTone === 'healthy').length
    const warning = serviceHealth.filter((service) => service.statusTone === 'warning').length
    const improving = serviceHealth.filter((service) => service.statusTone === 'improving').length

    return {
      total: serviceHealth.length,
      healthy,
      warning,
      improving,
    }
  }, [])

  const averageRiskScore = useMemo(() => {
    const scores = dashboard.predictions.map((item) => item.score)
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length
    return Math.round(average * 100)
  }, [])

  const handleQuickAction = (action) => {
    setSelectedAction(action.title)
    setChatHistory((history) => [
      ...history,
      { role: 'user', text: `执行快捷动作：${action.title}` },
      { role: 'assistant', text: action.outcome },
    ])
  }

  const handleChatSubmit = (event) => {
    event.preventDefault()

    const prompt = chatInput.trim()
    if (!prompt) {
      return
    }

    const serviceMatch = serviceHealth.find((service) =>
      prompt.toLowerCase().includes(service.name.toLowerCase()),
    )
    const relatedPrediction = serviceMatch
      ? dashboard.predictions.find((item) => item.service === serviceMatch.name)
      : dashboard.predictions[0]

    const assistantReply = serviceMatch
      ? `${serviceMatch.name} 当前状态为 ${serviceMatch.status}，SLO 为 ${serviceMatch.slo}；建议优先执行：${relatedPrediction?.recommendedAction ?? '检查最新 runbook。'}`
      : `已基于当前值班上下文生成建议：优先关注 ${dashboard.predictions[0].service}，并结合知识库中相关 runbook 做人工确认。`

    setChatHistory((history) => [...history, { role: 'user', text: prompt }, { role: 'assistant', text: assistantReply }])
    setChatInput('')
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-card">
          <p className="brand-card__eyebrow">Control Plane</p>
          <h1>SRE Agent</h1>
          <p className="brand-card__copy">面向稳定性治理、智能运维与知识协同的一体化前端控制台基础框架。</p>
        </div>

        <nav className="nav-card" aria-label="Primary navigation">
          <p className="nav-card__title">导航</p>
          <ul className="nav-list">
            {navigation.map((item) => (
              <li key={item.label}>
                <a className={`nav-link${item.active ? ' nav-link--active' : ''}`} href={item.href}>
                  <span>{item.label}</span>
                  <small>{item.description}</small>
                </a>
              </li>
            ))}
          </ul>
        </nav>

        <Section
          title="Quick Actions"
          subtitle="聚合常用操作入口，并把动作结果同步回值班工作台与 ChatOps 上下文。"
        >
          <div className="quick-actions quick-actions--stacked">
            {quickActions.map((action) => (
              <button
                key={action.title}
                className={`action-chip${selectedAction === action.title ? ' action-chip--active' : ''}`}
                type="button"
                onClick={() => handleQuickAction(action)}
              >
                {action.title}
              </button>
            ))}
          </div>

          <article className="action-detail-card">
            <div className="action-detail-card__header">
              <strong>{quickActionDetail.title}</strong>
              <span className={`status-pill status-pill--${quickActionDetail.tone}`}>{quickActionDetail.status}</span>
            </div>
            <p>{quickActionDetail.description}</p>
            <small>{quickActionDetail.outcome}</small>
          </article>
        </Section>
      </aside>

      <main className="main-panel">
        <header className="hero panel panel--hero" id="overview">
          <div>
            <p className="eyebrow">SRE Agent Control Center</p>
            <h2>把可观测、告警、自愈、知识检索与 ChatOps 汇聚到一个前端基础控制面</h2>
            <p className="hero__copy">
              当前版本重点完善了工作台切换、风险服务筛选、快捷动作反馈、知识检索与 ChatOps 交互，已经具备“值班控制台”核心骨架。
            </p>
          </div>
          <div className="hero__meta">
            <div className="status-pill status-pill--healthy">系统基线稳定</div>
            <div className="hero-kpi-grid">
              <article className="hero-kpi-card">
                <span>服务总数</span>
                <strong>{serviceOverview.total}</strong>
              </article>
              <article className="hero-kpi-card">
                <span>需关注</span>
                <strong>{serviceOverview.warning}</strong>
              </article>
              <article className="hero-kpi-card">
                <span>平均风险</span>
                <strong>{averageRiskScore}%</strong>
              </article>
            </div>
            <div className="hero__actions">
              <button type="button" onClick={() => setServiceFilter('warning')}>
                查看高风险服务
              </button>
              <button className="secondary" type="button" onClick={() => setActiveTab('command')}>
                进入 ChatOps 控制台
              </button>
            </div>
          </div>
        </header>

        <Section title="平台能力概览" subtitle="统一沉淀首页卡片、趋势字段与状态语义，便于后续接接口复用。">
          <div className="stats-grid">
            {dashboard.cards.map((card) => (
              <StatCard key={card.label} card={card} />
            ))}
          </div>
        </Section>

        <div className="dashboard-grid">
          <Section
            title="Operator Workbench"
            subtitle="支持值班 / 平台 / 管理 / ChatOps 视角切换，并暴露本视角下的关键目标与待办。"
          >
            <div className="tab-row" role="tablist" aria-label="Workbench tabs">
              {workbenchTabs.map((tab) => (
                <button
                  key={tab.key}
                  className={`tab-chip${tab.key === activeTab ? ' tab-chip--active' : ''}`}
                  type="button"
                  role="tab"
                  aria-selected={tab.key === activeTab}
                  onClick={() => setActiveTab(tab.key)}
                >
                  <span>{tab.label}</span>
                  <small>{tab.value}</small>
                </button>
              ))}
            </div>

            <article className="workbench-card">
              <div className="workbench-card__header">
                <div>
                  <p className="eyebrow">{activeWorkbench.value}</p>
                  <h3>{activeWorkbench.headline}</h3>
                </div>
                <span className={`status-pill status-pill--${activeWorkbench.tone}`}>{activeWorkbench.kpi}</span>
              </div>
              <p className="workbench-card__copy">{activeWorkbench.description}</p>
              <div className="checklist-grid">
                {activeWorkbench.tasks.map((task) => (
                  <article key={task.title} className="checklist-item">
                    <div className="checklist-item__header">
                      <strong>{task.title}</strong>
                      <span className={`status-pill status-pill--${task.tone}`}>{task.status}</span>
                    </div>
                    <p>{task.detail}</p>
                  </article>
                ))}
              </div>
            </article>

            <div className="highlight-grid">
              {capabilityHighlights.map((item) => (
                <article key={item.title} className="highlight-card">
                  <p className="highlight-card__tag">{item.tag}</p>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </article>
              ))}
            </div>
          </Section>

          <Section title="服务健康状态" subtitle="支持按状态筛选服务，首页直接看到负责人、风险与最近动作。">
            <div className="service-overview-row">
              <span>Healthy {serviceOverview.healthy}</span>
              <span>Degraded {serviceOverview.warning}</span>
              <span>Protected {serviceOverview.improving}</span>
            </div>
            <div className="filter-row" role="toolbar" aria-label="Service health filters">
              {[
                { key: 'all', label: '全部服务' },
                { key: 'healthy', label: 'Healthy' },
                { key: 'warning', label: 'Degraded' },
                { key: 'improving', label: 'Protected' },
              ].map((filter) => (
                <button
                  key={filter.key}
                  type="button"
                  className={`filter-chip${serviceFilter === filter.key ? ' filter-chip--active' : ''}`}
                  onClick={() => setServiceFilter(filter.key)}
                >
                  {filter.label}
                </button>
              ))}
            </div>

            <div className="service-list">
              {filteredServices.map((service) => (
                <article key={service.name} className="service-row">
                  <div>
                    <div className="service-row__title">
                      <h3>{service.name}</h3>
                      <span className={`status-pill status-pill--${service.statusTone}`}>{service.status}</span>
                    </div>
                    <p>{service.owner}</p>
                    <small className="service-row__summary">{service.summary}</small>
                  </div>
                  <div className="service-row__meta">
                    <strong>{service.slo}</strong>
                    <small>{service.lastEvent}</small>
                  </div>
                </article>
              ))}
            </div>
          </Section>
        </div>

        <div className="dashboard-grid">
          <Section title="核心架构能力" subtitle="首期 MVP 聚焦 4 条业务主线，并预留继续扩展能力域。" id="capabilities">
            <div className="capability-grid">
              <article>
                <h3>Observability</h3>
                <ul>
                  {runbook.observability.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article>
                <h3>Agent Ops</h3>
                <ul>
                  {runbook.agentOperations.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article>
                <h3>Knowledge Base</h3>
                <ul>
                  {runbook.knowledgeBase.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
              <article>
                <h3>ChatOps</h3>
                <ul>
                  {runbook.chatops.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </article>
            </div>
          </Section>

          <Section title="故障预测与自愈建议" subtitle="支持预测风险、执行建议与人工确认状态，一页内形成闭环。" id="incidents">
            <div className="prediction-list">
              {dashboard.predictions.map((item) => (
                <article key={item.service} className="prediction-card">
                  <div className="prediction-card__header">
                    <h3>{item.service}</h3>
                    <span>{Math.round(item.score * 100)}% risk</span>
                  </div>
                  <p>{item.horizon}</p>
                  <p>{item.recommendedAction}</p>
                  <div className="prediction-progress">
                    <div className="prediction-progress__track">
                      <span style={{ width: `${Math.round(item.score * 100)}%` }} />
                    </div>
                  </div>
                  <div className="prediction-card__footer">
                    <span className={`status-pill status-pill--${item.tone}`}>{item.status}</span>
                    <small>{item.owner}</small>
                  </div>
                </article>
              ))}
            </div>
          </Section>
        </div>

        <div className="dashboard-grid dashboard-grid--bottom">
          <Section title="实时指标样例" subtitle="后续可接入 Prometheus、VictoriaMetrics 或云监控时序接口。" id="observability">
            <table className="metrics-table">
              <thead>
                <tr>
                  <th>Time</th>
                  <th>Latency</th>
                  <th>Error Rate</th>
                  <th>CPU</th>
                </tr>
              </thead>
              <tbody>
                {dashboard.timeline.map((row) => (
                  <tr key={row.time}>
                    <td>{row.time}</td>
                    <td>{row.latency} ms</td>
                    <td>{row.errorRate}%</td>
                    <td>{row.cpu}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Section>

          <Section title="Knowledge Hub" subtitle="在首页直接搜索 SOP、复盘与架构文档，形成诊断与执行支撑。" id="knowledge">
            <label className="search-field">
              <span>搜索知识库</span>
              <input
                type="search"
                value={knowledgeQuery}
                placeholder="搜索 runbook / postmortem / CMDB"
                onChange={(event) => setKnowledgeQuery(event.target.value)}
              />
            </label>
            <div className="knowledge-list">
              {filteredKnowledgeDocs.length ? (
                filteredKnowledgeDocs.map((doc) => (
                  <article key={doc.title} className="knowledge-card">
                    <div className="knowledge-card__header">
                      <h3>{doc.title}</h3>
                      <span className={`status-pill status-pill--${doc.tone}`}>{doc.type}</span>
                    </div>
                    <p>{doc.summary}</p>
                    <div className="knowledge-card__tags">
                      {doc.tags.map((tag) => (
                        <span key={tag}>{tag}</span>
                      ))}
                    </div>
                  </article>
                ))
              ) : (
                <article className="knowledge-empty">
                  <strong>没有匹配文档</strong>
                  <p>可尝试关键词：runbook / kafka / payment / topology。</p>
                  <button type="button" className="secondary" onClick={() => setKnowledgeQuery('')}>
                    清空搜索
                  </button>
                </article>
              )}
            </div>
          </Section>
        </div>

        <div className="dashboard-grid dashboard-grid--bottom">
          <Section title="ChatOps 控制台" subtitle="可直接套用预设提示词，并将交互结果沉淀为值班会话上下文。" id="chatops">
            <div className="prompt-row">
              {chatopsPresets.map((preset) => (
                <button key={preset.label} type="button" className="prompt-chip" onClick={() => setChatInput(preset.prompt)}>
                  {preset.label}
                </button>
              ))}
            </div>
            <div className="chat-shell">
              <div className="chat-history" aria-live="polite">
                {chatHistory.map((message, index) => (
                  <article
                    key={`${message.role}-${index}`}
                    className={`chat-message chat-message--${message.role}`}
                  >
                    <strong>{message.role === 'assistant' ? 'Agent' : 'Operator'}</strong>
                    <p>{message.text}</p>
                  </article>
                ))}
              </div>

              <form className="chat-form" onSubmit={handleChatSubmit}>
                <label>
                  <span>输入自然语言指令</span>
                  <textarea
                    rows="4"
                    value={chatInput}
                    placeholder="例如：汇总 payment-gateway 最近 1 小时异常与建议动作"
                    onChange={(event) => setChatInput(event.target.value)}
                  />
                </label>
                <button type="submit">发送指令</button>
              </form>
            </div>
          </Section>

          <Section title="ChatOps 指令示例" subtitle="适用于一线运维与管理人员的自然语言操作入口。">
            <ul className="command-list">
              {dashboard.chatopsExamples.map((command) => (
                <li key={command}>{command}</li>
              ))}
            </ul>
          </Section>
        </div>
      </main>
    </div>
  )
}

export default App
