export function Section({ title, subtitle, children, id }) {
  return (
    <section className="panel" id={id}>
      <div className="panel__header">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
      </div>
      {children}
    </section>
  )
}
