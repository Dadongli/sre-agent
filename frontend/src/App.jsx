import { Section } from './components/Section'
import { StatCard } from './components/StatCard'
import { dashboard, runbook } from './lib/mockData'

function App() {
  return (
    <main className="layout">
      <header className="hero">
        <div>
          <p className="eyebrow">SRE Agent Control Center</p>
          <h1>面向运维场景的一体化 AIOps Agent 与可视化管理平台</h1>
          <p className="hero__copy">
            围绕 Observability、Agent 监控与告警、根因分析、故障预测、自愈、Knowledge Base 和 ChatOps 构建统一控制面。
          </p>
        </div>
        <div className="hero__actions">
          <button>查看告警大盘</button>
          <button className="secondary">进入 ChatOps 控制台</button>
        </div>
      </header>

      <Section title="平台能力概览" subtitle="覆盖稳定性治理、知识检索与智能运维协同。">
        <div className="stats-grid">
          {dashboard.cards.map((card) => (
            <StatCard key={card.label} card={card} />
          ))}
        </div>
      </Section>

      <div className="two-column">
        <Section title="核心架构能力" subtitle="首期 MVP 聚焦 4 条业务主线。">
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

        <Section title="故障预测与自愈建议" subtitle="通过时序信号和知识库规则输出可执行操作。">
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

      <div className="two-column">
        <Section title="实时指标样例" subtitle="后续可接入 Prometheus、VictoriaMetrics 或云监控。">
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

        <Section title="ChatOps 指令示例" subtitle="适用于一线运维与管理人员的自然语言操作入口。">
          <ul className="command-list">
            {dashboard.chatopsExamples.map((command) => (
              <li key={command}>{command}</li>
            ))}
          </ul>
        </Section>
      </div>
    </main>
  )
}

export default App
