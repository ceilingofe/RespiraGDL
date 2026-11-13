import { useEffect, useRef, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine,
} from "recharts";
import {
  SEMAFORO, NORMA_PM25, PROTECCION_MINIMA, PROTECCION_BUENA, nivelPm25,
  MOCK_ESCUELA, MOCK_SALONES, MOCK_LECTURAS, MOCK_PRONOSTICO,
  // API_URL, // <- descomentar al conectar la API
} from "../data/demo.js";

// Píldora del semáforo. `color` es lo que manda la API: "verde" | "amarillo" | "rojo".
export function Semaforo({ color, pm, big, prefijo }) {
  const s = SEMAFORO[color] ?? SEMAFORO.amarillo;
  return (
    <span className={`rg-aq rg-aq--${s.id}${big ? " rg-aq--big" : ""}`}>
      <i aria-hidden="true" />
      {prefijo}{s.nombre}{pm != null && ` · PM2.5 ${pm}`}
    </span>
  );
}

// Íconos de línea (estilo Lucide, trazo 1.5) en SVG inline para no sumar dependencias.
const Icono = ({ children, className = "rg-ico" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{children}</svg>
);
const IconoAviso = () => (
  <Icono><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z" /><path d="M12 9v4M12 17h.01" /></Icono>
);
const IconoPulmones = () => (
  <Icono>
    <path d="M12 3v9M12 12c-1 1.5-3 2-4 2" /><path d="M12 12c1 1.5 3 2 4 2" />
    <path d="M8 7C5 7 3 12 3 17c0 2 1 3 3 3s3-1.5 3-3V9c0-1-.4-2-1-2z" />
    <path d="M16 7c3 0 5 5 5 10 0 2-1 3-3 3s-3-1.5-3-3V9c0-1 .4-2 1-2z" />
  </Icono>
);
const IconoCheck = () => <Icono><path d="M20 6 9 17l-5-5" /></Icono>;

// Lee un token de tokens.css para pasárselo a Recharts (que pide colores como props).
function useToken(name, fallback) {
  const [v, setV] = useState(fallback);
  useEffect(() => {
    const val = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    if (val) setV(val);
  }, [name]);
  return v;
}

function TooltipLecturas({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="rg-tip">
      <strong>{label}</strong>
      {payload.map((p) => (
        <span key={p.dataKey}><i style={{ background: p.stroke }} />{p.name}: {p.value} µg/m³</span>
      ))}
    </div>
  );
}

// Etiqueta directa al final de cada línea (para no depender solo del color).
const etiquetaFinal = (texto, color, total) => ({ x, y, index }) =>
  index === total - 1 ? (
    <text x={x + 8} y={y + 4} fill={color} className="rg-chart__end">{texto}</text>
  ) : null;

function GraficaLecturas({ data, grupo }) {
  const fuera = useToken("--rg-aq-bad", "#b23c0a");
  const dentro = useToken("--rg-teal", "#0b585b");
  const grid = useToken("--rg-sage", "#ceddd1");
  const muted = useToken("--rg-muted", "#59735f");
  const tick = { fill: muted, fontSize: 11, fontFamily: "var(--rg-font)" };
  // La guía pide respetar prefers-reduced-motion: Recharts anima por JS, así que se apaga aquí.
  const animar = !window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
  return (
    <div className="rg-rchart" role="img" aria-label={`PM2.5 fuera y dentro del salón ${grupo} de 7:00 a 16:00`}>
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data} margin={{ top: 16, right: 56, bottom: 0, left: -16 }}>
          <CartesianGrid stroke={grid} strokeOpacity={0.6} vertical={false} />
          <XAxis dataKey="h" tick={tick} tickLine={false} axisLine={false} />
          <YAxis domain={[0, 80]} ticks={[0, 20, 40, 60, 80]} tick={tick} tickLine={false} axisLine={false} />
          <ReferenceLine y={NORMA_PM25} stroke={muted} strokeDasharray="5 6"
            label={{ value: `norma ${NORMA_PM25}`, position: "insideTopRight", fill: muted, fontSize: 11 }} />
          <Tooltip content={<TooltipLecturas />} cursor={{ stroke: muted, strokeWidth: 1 }} />
          <Line type="monotone" dataKey="fuera" name="Fuera" stroke={fuera} strokeWidth={2.5}
            dot={false} activeDot={{ r: 5 }} isAnimationActive={animar} label={etiquetaFinal("Fuera", fuera, data.length)} />
          <Line type="monotone" dataKey="dentro" name="Dentro del salón" stroke={dentro} strokeWidth={2.5}
            dot={false} activeDot={{ r: 5 }} isAnimationActive={animar} label={etiquetaFinal("Dentro", dentro, data.length)} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// Número de PM2.5 coloreado por nivel, siempre con la palabra (nunca color solo).
function Pm({ valor }) {
  const n = nivelPm25(valor);
  return (
    <span className={`rg-pm rg-pm--${n.id}`}>
      <strong>{valor}</strong>
      <small>{n.nombre}</small>
    </span>
  );
}

export default function Tablero() {
  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Datos de la escuela y semáforo de hoy. Valor inicial = mock; la API lo sobrescribe.
  const [escuela, setEscuela] = useState(MOCK_ESCUELA);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Tabla de salones -> GET /salones
  const [salones, setSalones] = useState(MOCK_SALONES);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Series del día por salón { [salonId]: [{ h, fuera, dentro }] } -> GET /lecturas?salon={id}&fecha=hoy
  // Al conectar: arrancar en {} y llenar con el useEffect de `seleccionado` de abajo.
  const [lecturas, setLecturas] = useState(MOCK_LECTURAS);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Pronóstico de mañana -> GET /pronostico/manana
  const [pronostico, setPronostico] = useState(MOCK_PRONOSTICO);

  // Estado de la interfaz (no es mock): salón elegido en la tabla y envío del aviso.
  const [seleccionado, setSeleccionado] = useState("3B");
  const [envio, setEnvio] = useState("listo"); // "listo" | "enviando" | "enviado"
  const timer = useRef();
  useEffect(() => () => clearTimeout(timer.current), []);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Al conectar: cambien los useState de arriba a useState(null) o [] y descomenten esto.
  useEffect(() => {
    // const get = (ruta) => fetch(`${API_URL}${ruta}`).then((r) => r.json());
    // get("/escuelas/miravalle").then(setEscuela);
    // get("/salones").then(setSalones);
    // get("/pronostico/manana").then(setPronostico);
  }, []);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Pide la serie del salón seleccionado si todavía no la tenemos.
  useEffect(() => {
    // if (lecturas[seleccionado]) return;
    // fetch(`${API_URL}/lecturas?salon=${seleccionado}&fecha=hoy`).then((r) => r.json())
    //   .then((serie) => setLecturas((l) => ({ ...l, [seleccionado]: serie })));
  }, [seleccionado]);

  const enviarAviso = () => {
    setEnvio("enviando");
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // Reemplazar el setTimeout por: fetch(`${API_URL}/alertas/enviar`, { method: "POST" }).then(() => setEnvio("enviado"))
    timer.current = setTimeout(() => setEnvio("enviado"), 1200);
  };

  // Derivados de los datos (no son mock: se calculan de lo que mande /salones)
  const alertas = salones.filter((s) => s.proteccion < PROTECCION_MINIMA);
  const salon = salones.find((s) => s.id === seleccionado) ?? salones[0];
  const serie = lecturas[salon?.id] ?? [];
  const sem = SEMAFORO[pronostico.semaforo] ?? SEMAFORO.amarillo;

  return (
    <main className="rg-app">
      <div className="rg-demo-note">Demo con datos simulados. En la versión final se conecta a los sensores y a la API.</div>

      <header className="rg-dir">
        <div className="rg-dir__brand">
          <span className="rg-dir__logo">Respira <b>GDL</b></span>
          <span className="rg-dir__tag">{escuela.nombreCorto}</span>
        </div>
        <div className="rg-dir__right">
          <span className="rg-muted">Vista del director · {escuela.momento}</span>
          <a className="rg-pill rg-pill--blue rg-tap" href="#/maestro">Vista del maestro</a>
        </div>
        <div className={`rg-dir__today rg-aq-bg--${SEMAFORO[escuela.semaforoHoy]?.id}`}>
          <small>Semáforo de hoy</small>
          <Semaforo color={escuela.semaforoHoy} pm={escuela.pm25Hoy} big />
          <span className="rg-muted">PM2.5 fuera en µg/m³ · {escuela.estacion} · {escuela.actualizado}</span>
        </div>
      </header>

      <div className="rg-dash">
        <section className="rg-panel rg-surface-lilac">
          <h2 className="rg-panel__title">Salones · PM2.5 fuera / dentro y protección</h2>
          <div className="rg-table-wrap">
            <table className="rg-table rg-table--salones">
              <thead>
                <tr><th>Grupo</th><th>Protección</th><th>Fuera</th><th>Dentro</th><th>%</th><th>Asma</th></tr>
              </thead>
              <tbody>
                {salones.map((s) => {
                  const activo = s.id === salon?.id;
                  const nivelBarra = s.proteccion >= PROTECCION_BUENA ? "good" : "ok";
                  return (
                    <tr key={s.id} className={activo ? "is-selected" : ""} aria-selected={activo}
                      onClick={() => setSeleccionado(s.id)}>
                      <td>
                        <button type="button" className="rg-row-btn" aria-pressed={activo}
                          aria-label={`Ver gráfica de ${s.grupo}`}>{s.grupo}</button>
                      </td>
                      <td>
                        <div className={`rg-bar rg-bar--${nivelBarra}`}>
                          <span style={{ width: `${Math.max(s.proteccion, 0)}%` }} />
                        </div>
                      </td>
                      <td>{s.fuera}</td>
                      <td><Pm valor={s.dentro} /></td>
                      <td>{s.proteccion} %</td>
                      <td>
                        <span className="rg-asma" title="Alumnos con asma (solo el número)">
                          <IconoPulmones />{s.asma}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="rg-muted">Toca un grupo para ver su gráfica. PM2.5 en µg/m³.</p>

          {alertas.map((s) => (
            <p key={s.id} className="rg-warn" role="alert">
              <IconoAviso />
              <span><strong>{s.grupo}: protección baja ({s.proteccion} %).</strong>{" "}
                Revisar que el filtro esté encendido y la puerta cerrada.</span>
            </p>
          ))}
        </section>

        <div className="rg-dash__col">
          <section className="rg-panel rg-surface-mist">
            <div className="rg-panel__head">
              <h2 className="rg-panel__title">Hoy en {salon?.grupo} · PM2.5 <span className="rg-unit">(µg/m³)</span></h2>
              <div className="rg-legend">
                <span><i className="is-fuera" />Fuera</span>
                <span><i className="is-dentro" />Dentro del salón</span>
                <span><i className="is-norma" />Norma {NORMA_PM25}</span>
              </div>
            </div>
            <GraficaLecturas data={serie} grupo={salon?.grupo} />
          </section>

          <section className={`rg-panel rg-aq-bg--${sem.id}`}>
            <p className="rg-panel__title rg-eyebrow">Pronóstico de {pronostico.dia.toLowerCase()}</p>
            <p className={`rg-forecast rg-forecast--${sem.id}`}>{sem.nombre} · PM2.5 {pronostico.pm25}</p>
            <p>
              <strong>Recomendación:</strong> {pronostico.recomendacion}; avisar a {pronostico.familiasAviso} familias
              de alumnos con asma.
            </p>
            <button type="button" className="rg-pill rg-pill--primary rg-full rg-tap"
              onClick={enviarAviso} disabled={envio !== "listo"}>
              {envio === "enviando" ? "Enviando…" : envio === "enviado" ? "Aviso enviado" : "Enviar aviso a familias"}
            </button>
            <div aria-live="polite">
              {envio === "enviado" && (
                <p className="rg-sent"><IconoCheck />Aviso enviado a {pronostico.familiasAviso} familias por Telegram (simulado).</p>
              )}
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
