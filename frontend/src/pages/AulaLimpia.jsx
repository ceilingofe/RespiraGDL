import { useEffect, useMemo, useRef, useState } from "react";
import { ESCUELA_AULA, SALONES_AULA, leerSalon } from "../aula/datos.js";
import { NORMA_PM25, PROTECCION_MINIMA, DIAS_CAMBIO_FILTRO, nivel, proteccion, recomendaciones, diasDesde, paso } from "../aula/logica.js";
import "../styles/aula.css";

const TICK_SIM = 2500; // ms entre lecturas simuladas
const TICK_API = 30000; // ms entre lecturas reales (los nodos mandan cada 10 s)
const PUNTOS = 24;

function Aq({ pm, big }) {
  const n = nivel(pm);
  return (
    <span className={`rg-aula-aq rg-aula-aq--${n.id}${big ? " rg-aula-aq--big" : ""}`}>
      <i aria-hidden="true" />
      {n.nombre} · {pm}
    </span>
  );
}

function Anillo({ pct }) {
  const v = Math.max(0, Math.min(100, pct ?? 0));
  const R = 52, C = 2 * Math.PI * R;
  const baja = pct !== null && pct < PROTECCION_MINIMA;
  return (
    <svg viewBox="0 0 128 128" className="rg-aula-ring" role="img" aria-label={`Protección del salón ${pct ?? "sin dato"} por ciento`}>
      <circle cx="64" cy="64" r={R} className="rg-aula-ring__track" />
      <circle
        cx="64" cy="64" r={R}
        className={`rg-aula-ring__val${baja ? " is-low" : ""}`}
        strokeDasharray={`${(v / 100) * C} ${C}`}
        transform="rotate(-90 64 64)"
      />
      <text x="64" y="66" textAnchor="middle" className="rg-aula-ring__num">{pct === null ? "—" : `${Math.max(pct, 0)}%`}</text>
      <text x="64" y="86" textAnchor="middle" className="rg-aula-ring__lbl">protección</text>
    </svg>
  );
}

function Serie({ data }) {
  const W = 600, H = 180, P = { l: 30, r: 10, t: 12, b: 12 };
  const max = Math.max(80, ...data.map((d) => d.fuera + 5));
  const x = (i) => P.l + (i * (W - P.l - P.r)) / Math.max(PUNTOS - 1, 1);
  const y = (v) => P.t + (1 - v / max) * (H - P.t - P.b);
  const line = (k) => data.map((d, i) => `${x(i)},${y(d[k])}`).join(" ");
  return (
    <svg className="rg-aula-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label="Últimas lecturas de PM2.5 fuera y dentro del salón">
      {[0, 40, 80].map((v) => (
        <text key={v} x={P.l - 8} y={y(v) + 4} textAnchor="end" className="rg-aula-chart__tick">{v}</text>
      ))}
      <line x1={P.l} x2={W - P.r} y1={y(NORMA_PM25)} y2={y(NORMA_PM25)} className="rg-aula-chart__norma" />
      <text x={W - P.r} y={y(NORMA_PM25) - 6} textAnchor="end" className="rg-aula-chart__tick">norma {NORMA_PM25}</text>
      {data.length > 1 && <polyline points={line("fuera")} className="rg-aula-chart__fuera" />}
      {data.length > 1 && <polyline points={line("dentro")} className="rg-aula-chart__dentro" />}
    </svg>
  );
}

// Llena el historial con lecturas previas para que la gráfica no arranque vacía
function calentar(s) {
  let e = { fuera: s.fuera, dentro: s.dentro, filtro: s.filtro, hist: [] };
  for (let i = -PUNTOS; i < 0; i++) {
    e = paso(e, i, s);
    e.hist = [...e.hist, { fuera: e.fuera, dentro: e.dentro }];
  }
  return e;
}

export default function AulaLimpia() {
  const [salonId, setSalonId] = useState("3A");
  const salon = SALONES_AULA.find((s) => s.id === salonId);
  // Estado vivo por salón: lecturas actuales, filtro e historial
  const vivo = useRef(null);
  if (!vivo.current) vivo.current = Object.fromEntries(SALONES_AULA.map((s) => [s.id, calentar(s)]));
  const [, refrescar] = useState(0);
  const [fuente, setFuente] = useState("simulado");
  const [hora, setHora] = useState(() => new Date());
  const t = useRef(0);

  useEffect(() => {
    let vivoTimer;
    let cancelado = false;
    const tick = async () => {
      t.current += 1;
      const real = await leerSalon(salonId);
      if (cancelado) return;
      for (const s of SALONES_AULA) {
        const e = vivo.current[s.id];
        const nuevo = real && s.id === salonId ? { ...e, ...real } : paso(e, t.current, s);
        nuevo.hist = [...e.hist, { fuera: nuevo.fuera, dentro: nuevo.dentro }].slice(-PUNTOS);
        vivo.current[s.id] = nuevo;
      }
      setFuente(real ? "en vivo" : "simulado");
      setHora(new Date());
      refrescar((n) => n + 1);
      vivoTimer = setTimeout(tick, real ? TICK_API : TICK_SIM);
    };
    tick();
    return () => { cancelado = true; clearTimeout(vivoTimer); };
  }, [salonId]);

  const e = vivo.current[salonId];
  const pct = proteccion(e.fuera, e.dentro);
  const recs = useMemo(
    () => recomendaciones({ fuera: e.fuera, dentro: e.dentro, filtro: e.filtro, filtroCambio: salon.filtroCambio, asma: salon.asma }),
    [e.fuera, e.dentro, e.filtro, salon]
  );
  const dias = diasDesde(salon.filtroCambio);
  const alFiltro = () => {
    vivo.current[salonId] = { ...e, filtro: !e.filtro };
    refrescar((n) => n + 1);
  };

  return (
    <main className="rg-app rg-aula">
      <div className="rg-demo-note">
        {fuente === "en vivo" ? "Lecturas en vivo de los sensores." : "Demo con lecturas simuladas. Con la API conectada se usan los sensores reales."}
      </div>

      <header className="rg-aula__head">
        <div>
          <p className="rg-eyebrow">Aula Limpia</p>
          <h1>Salón {salon.grupo}</h1>
          <p className="rg-muted">
            {ESCUELA_AULA.nombre} · <span className="rg-aula-live"><i aria-hidden="true" />{fuente}</span> ·{" "}
            {hora.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </p>
        </div>
        <div className="rg-aula-salones" role="tablist" aria-label="Elegir salón">
          {SALONES_AULA.map((s) => (
            <button
              key={s.id}
              role="tab"
              aria-selected={s.id === salonId}
              className={`rg-aula-salon${s.id === salonId ? " is-on" : ""}`}
              onClick={() => setSalonId(s.id)}
            >
              {s.grupo}
            </button>
          ))}
        </div>
      </header>

      <section className="rg-aula-hero" aria-live="polite">
        <div className="rg-aula-read rg-surface-lilac">
          <small>Fuera del salón</small>
          <strong>{e.fuera}<span> µg/m³</span></strong>
          <Aq pm={e.fuera} />
          <p className="rg-muted">PM2.5 · sensor del patio y {ESCUELA_AULA.estacion}</p>
        </div>
        <div className="rg-aula-prot rg-surface-mint">
          <Anillo pct={pct} />
          <p className="rg-aula-formula">PM2.5 que no entra = 1 − {e.dentro}/{e.fuera}</p>
        </div>
        <div className={`rg-aula-read rg-aula-bg--${nivel(e.dentro).id}`}>
          <small>Dentro del salón</small>
          <strong>{e.dentro}<span> µg/m³</span></strong>
          <Aq pm={e.dentro} />
          <p className="rg-muted">{e.dentro > NORMA_PM25 ? `Arriba de la norma (${NORMA_PM25})` : `Debajo de la norma (${NORMA_PM25})`}</p>
        </div>
      </section>

      <div className="rg-aula-grid">
        <section className="rg-panel rg-surface-sky">
          <h2>Qué hacer ahora</h2>
          <ul className="rg-aula-recs">
            {recs.map((r) => (
              <li key={r.texto} className={`is-${r.prioridad}`}>
                <span className="rg-aula-recs__tag">{r.prioridad === "alta" ? "Ahora" : r.prioridad === "media" ? "Hoy" : "Bien"}</span>
                <div>
                  <strong>{r.texto}</strong>
                  <small>{r.porque}</small>
                </div>
              </li>
            ))}
          </ul>
          <p className="rg-muted">Respira GDL orienta y recuerda; no sustituye la atención médica.</p>
        </section>

        <section className="rg-panel rg-surface-mist">
          <div className="rg-panel__head">
            <h2>Últimos minutos</h2>
            <div className="rg-aula-legend">
              <span><i className="is-fuera" />Fuera</span>
              <span><i className="is-dentro" />Dentro</span>
            </div>
          </div>
          <Serie data={e.hist} />

          <div className="rg-aula-filtro">
            <div>
              <small>Filtro casero</small>
              <strong>{e.filtro ? "Encendido" : "Apagado"}</strong>
              <span className="rg-muted">
                Ventilador + 4 filtros MERV-13 · cambio hace {dias} días
                {dias >= DIAS_CAMBIO_FILTRO ? " (ya toca)" : ` (faltan ${DIAS_CAMBIO_FILTRO - dias})`}
              </span>
            </div>
            <button className={`rg-pill rg-tap ${e.filtro ? "rg-pill--blue" : "rg-pill--primary"}`} onClick={alFiltro} aria-pressed={e.filtro}>
              {e.filtro ? "Simular filtro apagado" : "Encender filtro"}
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
