import { Section } from './components/Section'
import { StatCard } from './components/StatCard'
import {
  capabilityHighlights,
  dashboard,
  navigation,
  quickActions,
  runbook,
  serviceHealth,
  workbenchTabs,
} from './lib/mockData'

function App() {
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
          subtitle="把常用操作入口先沉淀为统一控制台动作区，后续可以直接接真实 API。"
        >
          <div className="quick-actions">
            {quickActions.map((action) => (
              <button key={action} className="action-chip" type="button">
                {action}
              </button>
            ))}
          </div>
        </Section>
      </aside>

      <main className="main-panel">
        <header className="hero panel panel--hero" id="overview">
          <div>
            <p className="eyebrow">SRE Agent Control Center</p>
            <h2>把可观测、告警、自愈、知识检索与 ChatOps 汇聚到一个前端基础控制面</h2>
            <p className="hero__copy">
              当前先完成前端基础骨架、信息分区、卡片体系、状态视图与样例数据联调结构，后续可直接对接后端 API、权限系统与实时流式数据。
            </p>
          </div>
          <div className="hero__meta">
            <div className="status-pill status-pill--healthy">系统基线稳定</div>
            <div className="hero__actions">
              <button type="button">查看告警大盘</button>
              <button className="secondary" type="button">
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
            subtitle="作为值班运维的核心工作台入口，先搭建信息架构与交互样式。"
          >
            <div className="tab-row" role="tablist" aria-label="Workbench tabs">
              {workbenchTabs.map((tab, index) => (
                <button
                  key={tab.label}
                  className={`tab-chip${index === 0 ? ' tab-chip--active' : ''}`}
                  type="button"
                  role="tab"
                  aria-selected={index === 0}
                >
                  <span>{tab.label}</span>
                  <small>{tab.value}</small>
                </button>
              ))}
            </div>

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

          <Section title="服务健康状态" subtitle="首页直接看到服务、负责人、风险与最近动作，形成值班第一视角。">
            <div className="service-list">
              {serviceHealth.map((service) => (
                <article key={service.name} className="service-row">
                  <div>
                    <div className="service-row__title">
                      <h3>{service.name}</h3>
                      <span className={`status-pill status-pill--${service.statusTone}`}>{service.status}</span>
                    </div>
                    <p>{service.owner}</p>
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

          <Section title="故障预测与自愈建议" subtitle="通过时序信号和知识规则输出可执行操作，形成自动化闭环基础视图。" id="incidents">
            <div className="prediction-list">
              {dashboard.predictions.map((item) => (
                <article key={item.service} className="prediction-card">
                  <div className="prediction-card__header">
                    <h3>{item.service}</h3>
                    <span>{Math.round(item.score * 100)}% risk</span>
                  </div>
                  <p>{item.horizon}</p>
                  <p>{item.recommendedAction}</p>
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

          <Section title="ChatOps 指令示例" subtitle="适用于一线运维与管理人员的自然语言操作入口。" id="chatops">
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
