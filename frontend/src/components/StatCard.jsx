export function StatCard({ card }) {
  return (
    <article className={`stat-card stat-card--${card.status}`}>
      <p className="stat-card__label">{card.label}</p>
      <h3>{card.value}</h3>
      <p className="stat-card__trend">Trend: {card.trend}</p>
    </article>
  )
}
