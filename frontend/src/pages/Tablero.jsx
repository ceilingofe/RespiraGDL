import { useState } from "react";
import { ESCUELA, SALONES, SERIE, PRONOSTICO, NORMA_PM25, AVISO_FAMILIAS, nivel } from "../data/demo.js";

export function Semaforo({ pm, big }) {
  const n = nivel(pm);
  return (
    <span className={`rg-aq rg-aq--${n.id}${big ? " rg-aq--big" : ""}`}>
      <i aria-hidden="true" />
      {n.nombre} · {pm}
    </span>
  );
}

function Chart({ data }) {
  const W = 1000, H = 300, P = { l: 36, r: 16, t: 16, b: 30 };
  const max = 80;
  const x = (i) => P.l + (i * (W - P.l - P.r)) / (data.length - 1);
  const y = (v) => P.t + (1 - v / max) * (H - P.t - P.b);
  const line = (k) => data.map((d, i) => `${x(i)},${y(d[k])}`).join(" ");
  return (
    <svg className="rg-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="PM2.5 fuera y dentro del salón 3A durante el día">
      {[0, 20, 40, 60, 80].map((v) => (
        <g key={v}>
          <line x1={P.l} x2={W - P.r} y1={y(v)} y2={y(v)} className="rg-chart__grid" />
          <text x={P.l - 8} y={y(v) + 4} textAnchor="end" className="rg-chart__tick">{v}</text>
        </g>
      ))}
      <line x1={P.l} x2={W - P.r} y1={y(NORMA_PM25)} y2={y(NORMA_PM25)} className="rg-chart__norma" />
      <text x={W - P.r} y={y(NORMA_PM25) - 6} textAnchor="end" className="rg-chart__tick">norma 45</text>
      <polyline points={line("fuera")} className="rg-chart__fuera" />
      <polyline points={line("dentro")} className="rg-chart__dentro" />
      {data.map((d, i) => (
        <text key={d.h} x={x(i)} y={H - 8} textAnchor="middle" className="rg-chart__tick">{d.h}</text>
      ))}
    </svg>
  );
}

export default function Tablero() {
  const [enviado, setEnviado] = useState(false);
  const hoy = PRONOSTICO[0].pm;
  const conFiltro = SALONES.filter((s) => s.filtro);
  const prom = Math.round(conFiltro.reduce((a, s) => a + s.proteccion, 0) / conFiltro.length);
  const asma = SALONES.reduce((a, s) => a + s.asma, 0);
  return (
    <main className="rg-app">
      <div className="rg-demo-note">Demo con datos simulados. En la versión final se conecta a los sensores y a la API.</div>
      <header className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Tablero de la escuela</p>
          <h1>{ESCUELA.nombre}</h1>
          <p className="rg-muted">Estación de referencia: {ESCUELA.estacion} · hoy 10:00</p>
        </div>
        <Semaforo pm={hoy} big />
      </header>

      <section className="rg-kpis">
        <div className="rg-kpi rg-surface-mint">
          <small>Protección promedio con filtro</small>
          <strong>{prom} %</strong>
          <span>menos PM2.5 dentro del salón</span>
        </div>
        <div className="rg-kpi rg-surface-sky">
          <small>Salones con filtro</small>
          <strong>{conFiltro.length} de {SALONES.length}</strong>
          <span>4°B y 6°B aún sin filtro</span>
        </div>
        <div className="rg-kpi rg-surface-aqua">
          <small>Alumnos con asma</small>
          <strong>{asma}</strong>
          <span>solo el número, sin nombres</span>
        </div>
      </section>

      <section className="rg-panel rg-surface-mist">
        <div className="rg-panel__head">
          <h2>Salón 3°A · fuera contra dentro</h2>
          <div className="rg-legend">
            <span><i className="is-fuera" />Fuera</span>
            <span><i className="is-dentro" />Dentro</span>
          </div>
        </div>
        <Chart data={SERIE} />
      </section>

      <div className="rg-two">
        <section className="rg-panel rg-surface-lilac">
          <h2>Salones</h2>
          <table className="rg-table">
            <thead>
              <tr><th>Salón</th><th>Fuera</th><th>Dentro</th><th>Protección</th><th>Asma</th></tr>
            </thead>
            <tbody>
              {SALONES.map((s) => (
                <tr key={s.id}>
                  <td><strong>{s.id}</strong>{!s.filtro && <em> sin filtro</em>}</td>
                  <td>{s.fuera}</td>
                  <td><Semaforo pm={s.dentro} /></td>
                  <td>
                    <div className="rg-bar"><span style={{ width: `${Math.max(s.proteccion, 0)}%` }} /></div>
                    {s.proteccion} %
                  </td>
                  <td>{s.asma}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>

        <section className="rg-panel rg-surface-ice">
          <h2>Pronóstico</h2>
          <ul className="rg-forecast">
            {PRONOSTICO.map((p) => (
              <li key={p.dia}><span>{p.dia}</span><Semaforo pm={p.pm} /></li>
            ))}
          </ul>
          <p className="rg-muted">{nivel(PRONOSTICO[1].pm).consejo}</p>
          <div className="rg-message">
            <small>Aviso a familias (vista previa)</small>
            <p>{AVISO_FAMILIAS}</p>
          </div>
          <button className="rg-pill rg-pill--primary rg-full" onClick={() => setEnviado(true)} disabled={enviado}>
            {enviado ? "Aviso programado para las 7:00 ✓" : "Enviar aviso a familias"}
          </button>
        </section>
      </div>
    </main>
  );
}
