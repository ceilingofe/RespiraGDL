// Piezas compartidas del tablero, la vista del maestro y el plan de asma.
// Solo variables de tokens.css (ver docs/diseno/README.md).
import { NORMA_PM25, nivel } from "../data/demo.js";

// Semáforo: siempre color + palabra + número, nunca color solo.
export function Semaforo({ pm, big, prefijo }) {
  const n = nivel(pm);
  return (
    <span className={`rg-aq rg-aq--${n.id}${big ? " rg-aq--big" : ""}`}>
      <i aria-hidden="true" />
      {prefijo}{n.nombre} · {pm}
    </span>
  );
}

// Iconos de línea redondeada (estilo Lucide, trazo 1.5) en SVG inline.
const PATHS = {
  alerta: "M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0zM12 9v4M12 17h.01",
  check: "M20 6 9 17l-5-5",
  telefono: "M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z",
  reloj: "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20zM12 6v6l4 2",
  enviar: "M22 2 11 13M22 2l-7 20-4-9-9-4z",
  escuela: "M3 21h18M5 21V9l7-5 7 5v12M9 21v-6h6v6",
  documento: "M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8zM14 2v6h6M8 13h8M8 17h5",
  flecha: "M5 12h14M13 6l6 6-6 6",
  candado: "M5 11h14v10H5zM8 11V7a4 4 0 0 1 8 0v4",
};
export function Icono({ name, className = "rg-ico" }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d={PATHS[name]} />
    </svg>
  );
}

// Gráfica de líneas fuera contra dentro, SVG sin dependencias.
// Fuera en --rg-aq-bad, dentro en --rg-teal, norma punteada en --rg-muted (guía de diseño §5).
export function GraficaAire({ data, label, alto = 300 }) {
  // En celular se dibuja más angosto para que el texto no quede diminuto.
  const narrow = typeof window !== "undefined" && window.matchMedia?.("(max-width: 560px)").matches;
  const W = narrow ? 440 : 1000, H = narrow ? 280 : alto, P = { l: 30, r: narrow ? 74 : 90, t: 16, b: 30 };
  const max = Math.max(80, Math.ceil(Math.max(...data.map((d) => d.fuera)) / 20) * 20);
  const x = (i) => P.l + (i * (W - P.l - P.r)) / (data.length - 1);
  const y = (v) => P.t + (1 - v / max) * (H - P.t - P.b);
  const line = (k) => data.map((d, i) => `${x(i)},${y(d[k])}`).join(" ");
  const ult = data[data.length - 1];
  const ticks = Array.from({ length: max / 20 + 1 }, (_, i) => i * 20);
  return (
    <svg className="rg-chart" viewBox={`0 0 ${W} ${H}`} role="img" aria-label={label}>
      {ticks.map((v) => (
        <g key={v}>
          <line x1={P.l} x2={W - P.r} y1={y(v)} y2={y(v)} className="rg-chart__grid" />
          <text x={P.l - 8} y={y(v) + 4} textAnchor="end" className="rg-chart__tick">{v}</text>
        </g>
      ))}
      <line x1={P.l} x2={W - P.r} y1={y(NORMA_PM25)} y2={y(NORMA_PM25)} className="rg-chart__norma" />
      <text x={(W - P.r + P.l) / 2} y={y(NORMA_PM25) + 16} textAnchor="middle" className="rg-chart__tick">norma {NORMA_PM25}</text>
      <polyline points={line("fuera")} className="rg-chart__fuera" />
      <polyline points={line("dentro")} className="rg-chart__dentro" />
      <text x={W - P.r + 10} y={y(ult.fuera) + 4} className="rg-chart__end is-fuera">Fuera {ult.fuera}</text>
      <text x={W - P.r + 10} y={y(ult.dentro) + 4} className="rg-chart__end is-dentro">Dentro {ult.dentro}</text>
      {data.map((d, i) => (
        <g key={d.h}>
          <circle cx={x(i)} cy={y(d.fuera)} r="5" className="rg-chart__dot is-fuera"><title>{`${d.h} · fuera ${d.fuera} µg/m³`}</title></circle>
          <circle cx={x(i)} cy={y(d.dentro)} r="5" className="rg-chart__dot is-dentro"><title>{`${d.h} · dentro ${d.dentro} µg/m³`}</title></circle>
          {(!narrow || i % 2 === 0) && <text x={x(i)} y={H - 8} textAnchor="middle" className="rg-chart__tick">{d.h}</text>}
        </g>
      ))}
    </svg>
  );
}

// Barra de protección: verde si protege, ámbar si está bajo el mínimo.
export function BarraProteccion({ valor, minimo }) {
  const baja = valor < minimo;
  return (
    <span className="rg-prot">
      <span className="rg-bar"><span className={baja ? "is-baja" : ""} style={{ width: `${Math.max(valor, 2)}%` }} /></span>
      <span className={baja ? "rg-prot__baja" : ""}>{valor} %</span>
    </span>
  );
}

// Comparación antes/ahora con dos barras horizontales.
export function AntesAhora({ antes, ahora, unidad }) {
  const max = Math.max(antes, ahora);
  const cambio = Math.round(((ahora - antes) / antes) * 100);
  return (
    <div className="rg-vs">
      <div><small>Ciclo pasado</small><span className="rg-vs__bar is-antes" style={{ width: `${(antes / max) * 100}%` }} /><b>{antes}</b></div>
      <div><small>Este ciclo</small><span className="rg-vs__bar is-ahora" style={{ width: `${(ahora / max) * 100}%` }} /><b>{ahora}</b></div>
      <p className="rg-muted">{cambio <= 0 ? `${Math.abs(cambio)} % menos` : `${cambio} % más`} {unidad}</p>
    </div>
  );
}

export function DemoNote({ simulado, children }) {
  return (
    <div className="rg-demo-note">
      {simulado ? children || "Demo con datos simulados. En la versión final se conecta a los sensores y a la API." : "Datos en vivo de la API."}
    </div>
  );
}
