import { nivelPm25 } from "../data/demo.js";

export function estadoAula(aula) {
  if (!aula.conexion) return { nombre: "Sin datos", color: "muted", categoria: null };
  const categoria = nivelPm25(aula.dentro);
  const color = { good: "good", ok: "good", bad: "ok", vbad: "vbad", ext: "vbad" }[categoria.id];
  return { nombre: { good: "Verde", ok: "Amarillo", vbad: "Rojo" }[color], color, categoria };
}

function Persona({ x, y, variante }) {
  return (
    <g transform={`translate(${x} ${y})`}>
      <path d="M-9 10 5 6 14 12 0 17Z" fill="var(--rg-pill-olive)" />
      <path d="M-6 2Q-6-5 0-5Q6-5 6 2L7 8-3 11Z" fill={variante ? "var(--rg-teal)" : "var(--rg-leaf)"} />
      <circle cy="-11" r="5" fill="var(--rg-muted)" />
      <path d="M-9 10V20M14 12V21" stroke="var(--rg-muted)" strokeWidth="2" />
    </g>
  );
}

function Filtro({ activo }) {
  return (
    <g transform="translate(16 33)">
      <path d="M0 0 17-5 27 1 10 6Z" fill="var(--rg-white)" stroke="var(--rg-teal)" />
      <path d="M0 0 10 6 10 29 0 23Z" fill="var(--rg-sage)" stroke="var(--rg-teal)" />
      <path d="M10 6 27 1 27 24 10 29Z" fill="var(--rg-white)" stroke="var(--rg-teal)" />
      {[7, 11, 15, 19].map((y) => <path key={y} d={`M14 ${y}l9-3`} stroke="var(--rg-sage)" strokeWidth="2" />)}
      <circle cx="18" cy="6" r="3" fill={activo ? "var(--rg-teal)" : "var(--rg-sage)"} />
      {activo && <g className="rg-air-strokes"><path d="M15-9q-5-5 0-11M22-10q-5-5 0-11" fill="none" stroke="var(--rg-teal)" strokeWidth="1.5" /></g>}
    </g>
  );
}

function Dispositivo({ aula, estado }) {
  return (
    <g transform="translate(173 -35)">
      <rect width="47" height="29" rx="4" fill="var(--rg-ink)" />
      <rect x="5" y="4" width="29" height="18" rx="2" fill="var(--rg-mint)" />
      <text x="19" y="11" textAnchor="middle" fontSize="4.5" fill="var(--rg-ink)">SIMULADO</text>
      <text x="19" y="19" textAnchor="middle" fontSize="7" fontWeight="600" fill="var(--rg-ink)">{aula.conexion ? Math.round(aula.dentro) : "--"}</text>
      {["good", "ok", "vbad"].map((color, i) => <circle key={color} cx="40" cy={7 + i * 7} r="2" fill={color === estado.color ? `var(--rg-aq-${color})` : "var(--rg-muted)"} />)}
      <path d="M18 29v9m10-9v9" stroke="var(--rg-muted)" strokeWidth="2" />
    </g>
  );
}

export default function EscuelaIsometrica({ salones, seleccionado, seleccionar, reproduciendo, acercar }) {
  const indice = salones.findIndex((s) => s.id === seleccionado);
  const focoX = 55 + (indice % 3) * 305;
  const focoY = indice < 3 ? 123 : 383;
  return (
    <svg className={`rg-campus-map${reproduciendo ? " is-running" : ""}`} viewBox={acercar ? `${focoX - 18} ${focoY - 95} 280 280` : "0 0 960 590"} aria-label={acercar ? `Vista ampliada del salón ${seleccionado}, simulado.` : "Escuela ficticia con seis salones isométricos. Selecciona uno para ensayar decisiones."}>
      <defs><filter id="sombra-campus"><feDropShadow dx="0" dy="10" stdDeviation="9" floodColor="var(--rg-ink)" floodOpacity=".08" /></filter></defs>
      <g aria-hidden="true">
        <path d="M40 243Q490 230 920 243L920 289Q470 276 40 289Z" fill="var(--rg-white)" />
        <path d="M463 24 482 24 482 546 463 546Z" fill="var(--rg-white)" />
        <path d="M40 266H920" stroke="var(--rg-sage)" strokeDasharray="7 10" />
        {[[30, 96], [916, 105], [37, 457], [913, 458], [317, 530], [650, 534]].map(([x, y]) => (
          <g key={`${x}-${y}`} transform={`translate(${x} ${y})`}><path d="M0 0v18" stroke="var(--rg-muted)" strokeWidth="3" /><ellipse cy="-6" rx="12" ry="18" fill="var(--rg-sage)" /><ellipse cx="-6" cy="-9" rx="7" ry="12" fill="var(--rg-mint)" /></g>
        ))}
        <text x="480" y="570" textAnchor="middle" className="rg-map-caption">Escuela ficticia · Miravalle, Guadalajara</text>
      </g>
      {salones.map((aula, i) => {
        if (acercar && seleccionado !== aula.id) return null;
        const x = 55 + (i % 3) * 305;
        const y = i < 3 ? 123 : 383;
        const estado = estadoAula(aula);
        const activo = seleccionado === aula.id;
        const superficie = estado.categoria ? `var(--rg-aq-${estado.categoria.id}-bg)` : "var(--rg-mist)";
        return (
          <g key={aula.id} transform={`translate(${x} ${y})`} role="button" tabIndex="0"
            aria-pressed={activo} aria-label={`Salón ${aula.id}. ${estado.nombre}. ${aula.conexion ? `${Math.round(aula.dentro)} microgramos por metro cúbico simulados` : "Dispositivo sin conexión simulado"}. ${aula.ocupacion} personas ficticias.`}
            onClick={() => seleccionar(aula.id)} onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); seleccionar(aula.id); } }}
            className={`rg-room${activo ? " is-selected" : ""}`}>
            <g aria-hidden="true">
              <ellipse cx="122" cy="98" rx="131" ry="40" fill="var(--rg-sage)" opacity=".35" />
              <g filter="url(#sombra-campus)">
                <path d="M0-30 150-70 150 0 0 40Z" fill="var(--rg-mint-2)" stroke="var(--rg-sage)" />
                <path d="M150-70 240-15 240 55 150 0Z" fill="var(--rg-sage)" stroke="var(--rg-white)" />
                <path d="M0 40 150 0 240 55 90 95Z" fill={superficie} stroke="var(--rg-white)" strokeWidth="2" />
                <path d="M0 40 90 95 90 105 0 50Z" fill="var(--rg-sage)" />
                <path d="M90 95 240 55 240 65 90 105Z" fill="var(--rg-white)" />
                <path d="M17-20 64-33 64-2 17 11Z" fill={aula.ventanas ? "var(--rg-sky)" : "var(--rg-white)"} stroke="var(--rg-sage)" />
                <path d={aula.ventanas ? "M41-27 52-17 52 3 41 5Z" : "M41-27V5"} fill="var(--rg-aqua)" stroke="var(--rg-sage)" />
                <text x="85" y="-24" className="rg-room-wall">{aula.id}</text>
                {aula.ocupacion > 0 && [[68, 35], [115, 23], [162, 49], [111, 63]].slice(0, Math.min(4, Math.ceil(aula.ocupacion / 10))).map(([px, py], j) => <Persona key={j} x={px} y={py} variante={j % 2} />)}
                <Filtro activo={aula.filtro} /><Dispositivo aula={aula} estado={estado} />
                <path d="M0-30 90 25 240-15" fill="none" stroke={activo ? "var(--rg-teal)" : "var(--rg-sage)"} strokeDasharray="4 5" opacity=".6" />
              </g>
              <g transform="translate(12 125)">
                <rect width="218" height="37" rx="18" fill={activo ? "var(--rg-ink)" : "var(--rg-white)"} />
                <text x="14" y="23" className="rg-room-label" fill={activo ? "var(--rg-white)" : "var(--rg-ink)"}>{aula.id}</text>
                <circle cx="59" cy="19" r="4" fill={estado.color === "muted" ? "var(--rg-muted)" : `var(--rg-aq-${estado.color})`} />
                <text x="70" y="23" fontSize="12" fill={activo ? "var(--rg-white)" : "var(--rg-ink)"}>{estado.nombre}{aula.conexion ? ` · ${Math.round(aula.dentro)} µg/m³` : ""}</text>
              </g>
            </g>
          </g>
        );
      })}
    </svg>
  );
}
