export function StatCard({ card }) {
  return (
    <article className={`stat-card stat-card--${card.status}`}>
      <div className="stat-card__header">
        <p className="stat-card__label">{card.label}</p>
        <span className={`status-pill status-pill--${card.statusTone}`}>{card.badge}</span>
      </div>
      <h3>{card.value}</h3>
      <p className="stat-card__trend">Trend: {card.trend}</p>
      <p className="stat-card__meta">{card.meta}</p>
    </article>
  )
}
