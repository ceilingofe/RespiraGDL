import { useState } from "react";
import {
  ESCUELA, SALONES, SERIES, PRONOSTICO, AVISO_FAMILIAS, FAMILIAS_BOT, INDICADORES, SEMANAS, INCIDENTES,
  PROTECCION_MINIMA, nivel,
} from "../data/demo.js";
import { PROTOCOLO } from "../data/planAsma.js";
import { useApi, post, horaActual, filas } from "../lib/api.js";
import { Semaforo, Icono, GraficaAire, BarraProteccion, AntesAhora, DemoNote } from "../components/ui.jsx";

// Se mantiene la exportación para las páginas que ya la importan desde aquí.
export { Semaforo };

// Barras por semana: días fuera de norma (fondo) y faltas por asma (número).
function Semanas({ data }) {
  const max = Math.max(...data.map((d) => d.fuera), 1);
  return (
    <div className="rg-weeks" role="img" aria-label="Días fuera de norma y faltas por asma por semana">
      {data.map((d) => (
        <div key={d.s} className="rg-weeks__col">
          <b>{d.faltas}</b>
          <span className="rg-weeks__bar" style={{ height: `${(d.fuera / max) * 100}%` }} title={`${d.fuera} días fuera de norma`} />
          <small>{d.s}</small>
        </div>
      ))}
    </div>
  );
}

export default function Tablero() {
  const { data: salones, simulado } = useApi("/salones", SALONES, filas("id", "fuera", "dentro", "proteccion", "asma", "filtro"));
  const { data: pronostico } = useApi("/alertas/pronostico", PRONOSTICO, filas("dia", "pm"));
  const [sel, setSel] = useState("3A");
  const [aviso, setAviso] = useState(AVISO_FAMILIAS);
  const [enviado, setEnviado] = useState(null);

  const hoy = pronostico[0].pm;
  const manana = pronostico[1];
  const nManana = nivel(manana.pm);
  const conFiltro = salones.filter((s) => s.filtro);
  const prom = Math.round(conFiltro.reduce((a, s) => a + s.proteccion, 0) / Math.max(conFiltro.length, 1));
  const asma = salones.reduce((a, s) => a + s.asma, 0);
  const bajos = salones.filter((s) => s.proteccion < PROTECCION_MINIMA);
  const salon = salones.find((s) => s.id === sel) ?? salones[0];
  const I = INDICADORES;

  const enviar = () => {
    const hora = horaActual();
    setEnviado(hora);
    post("/alertas/aviso", { escuela_id: ESCUELA.id, texto: aviso });
  };

  return (
    <main className="rg-app">
      <DemoNote simulado={simulado} />
      <header className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Tablero de la escuela · vista de dirección</p>
          <h1>{ESCUELA.nombre}</h1>
          <p className="rg-muted">Estación de referencia: {ESCUELA.estacion} · hoy {ESCUELA.hora}</p>
        </div>
        <div className="rg-app__actions">
          <Semaforo pm={hoy} big prefijo="Hoy: " />
          <a className="rg-pill rg-pill--blue" href="#/plan">Plan de asma escolar</a>
          <a className="rg-pill" href="#/red">Red de escuelas</a>
        </div>
      </header>

      <section className="rg-kpis rg-kpis--4">
        <div className="rg-kpi rg-surface-mint">
          <small>Protección promedio con filtro</small>
          <strong>{prom} %</strong>
          <span>menos PM2.5 dentro del salón</span>
        </div>
        <div className="rg-kpi rg-surface-sky">
          <small>Salones con filtro</small>
          <strong>{conFiltro.length} de {salones.length}</strong>
          <span>{salones.filter((s) => !s.filtro).map((s) => s.id).join(" y ") || "todos"} sin filtro</span>
        </div>
        <div className="rg-kpi rg-surface-aqua">
          <small>Alumnos con asma</small>
          <strong>{asma}</strong>
          <span>solo el número, sin nombres</span>
        </div>
        <div className="rg-kpi rg-surface-lilac">
          <small>Días con recreo protegido</small>
          <strong>{I.diasRecreoProtegido} de {I.diasFueraNorma}</strong>
          <span>días fuera de norma · {I.periodo}</span>
        </div>
      </section>

      {bajos.length > 0 && (
        <section className="rg-alert" role="status">
          <Icono name="alerta" />
          <div>
            <strong>{bajos.length === 1 ? "1 salón" : `${bajos.length} salones`} con protección baja</strong>
            <ul>
              {bajos.map((s) => (
                <li key={s.id}>
                  <button className="rg-link" onClick={() => setSel(s.id)}>{s.id}</button>: {s.proteccion} % ·{" "}
                  {s.filtro ? "revisar que el filtro esté encendido y la puerta cerrada." : "no tiene filtro; es el siguiente en la lista."}
                  {s.asma > 0 && ` Tiene ${s.asma} ${s.asma === 1 ? "alumno" : "alumnos"} con asma.`}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      <section className="rg-panel rg-surface-mist">
        <div className="rg-panel__head">
          <h2>Salón {salon.id} · fuera contra dentro</h2>
          <div className="rg-legend">
            <span><i className="is-fuera" />Fuera</span>
            <span><i className="is-dentro" />Dentro</span>
          </div>
        </div>
        <div className="rg-selector" role="tablist" aria-label="Elegir salón">
          {salones.map((s) => (
            <button key={s.id} role="tab" aria-selected={s.id === sel} className={`rg-amount${s.id === sel ? " is-on" : ""}`} onClick={() => setSel(s.id)}>
              {s.id}
            </button>
          ))}
        </div>
        {SERIES[salon.id] && <GraficaAire data={SERIES[salon.id]} label={`PM2.5 fuera y dentro del salón ${salon.id} de 7:00 a 14:00`} />}
        <p className="rg-muted">
          A las {ESCUELA.hora}: fuera {salon.fuera}, dentro {salon.dentro} µg/m³. Protección = 1 − {salon.dentro}/{salon.fuera} = {salon.proteccion} %.
          {!salon.filtro && " Este salón aún no tiene filtro."}
        </p>
      </section>

      <div className="rg-two">
        <section className="rg-panel rg-surface-lilac">
          <h2>Salones</h2>
          <div className="rg-table-wrap">
            <table className="rg-table">
              <thead>
                <tr><th>Salón</th><th>Fuera</th><th>Dentro</th><th>Protección</th><th>Asma</th></tr>
              </thead>
              <tbody>
                {salones.map((s) => (
                  <tr key={s.id} className={s.id === sel ? "is-sel" : ""} onClick={() => setSel(s.id)}>
                    <td><strong>{s.id}</strong>{!s.filtro && <em> sin filtro</em>}</td>
                    <td>{s.fuera}</td>
                    <td><Semaforo pm={s.dentro} /></td>
                    <td><BarraProteccion valor={s.proteccion} minimo={PROTECCION_MINIMA} /></td>
                    <td>{s.asma}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <section className="rg-panel rg-surface-ice">
          <h2>Pronóstico</h2>
          <ul className="rg-forecast">
            {pronostico.map((p) => (
              <li key={p.dia}><span>{p.dia}</span><Semaforo pm={p.pm} /></li>
            ))}
          </ul>
          <div className="rg-message">
            <small>Plan para mañana · {PROTOCOLO[nManana.id].titulo}</small>
            <ul className="rg-dots">
              {PROTOCOLO[nManana.id].escuela.map((t) => <li key={t}>{t}</li>)}
            </ul>
          </div>
          <label className="rg-message rg-message--edit">
            <small>Aviso a {FAMILIAS_BOT} familias de alumnos con asma (puedes editarlo)</small>
            <textarea value={aviso} onChange={(e) => { setAviso(e.target.value); setEnviado(null); }} rows={5} />
          </label>
          <button className="rg-pill rg-pill--primary rg-full rg-tap" onClick={enviar} disabled={!!enviado || !aviso.trim()}>
            <Icono name={enviado ? "check" : "enviar"} />
            {enviado ? `Aviso enviado a las ${enviado}` : "Enviar aviso a familias"}
          </button>
        </section>
      </div>

      <section className="rg-panel rg-surface-mint2">
        <div className="rg-panel__head">
          <div>
            <h2>¿Está funcionando? · indicadores del ciclo</h2>
            <p className="rg-muted">{I.periodo} contra el mismo periodo del ciclo pasado. Datos agregados, sin nombres.</p>
          </div>
        </div>
        <div className="rg-grid-ind">
          <div className="rg-ind">
            <h3>Faltas por asma</h3>
            <AntesAhora antes={I.faltasAsma.antes} ahora={I.faltasAsma.ahora} unidad="faltas" />
          </div>
          <div className="rg-ind">
            <h3>Crisis atendidas en la escuela</h3>
            <AntesAhora antes={I.crisisEscuela.antes} ahora={I.crisisEscuela.ahora} unidad="crisis" />
          </div>
          <div className="rg-ind">
            <h3>Faltas por semana</h3>
            <Semanas data={SEMANAS} />
            <p className="rg-muted">Barra: días fuera de norma. Número: faltas por asma.</p>
          </div>
          <div className="rg-ind">
            <h3>Últimas crisis registradas</h3>
            <ul className="rg-log">
              {INCIDENTES.map((x) => (
                <li key={x.id}>
                  <span>{x.fecha} · {x.hora}</span>
                  <strong>{x.salon}</strong>
                  <small>{x.avisoFamilia ? "familia avisada" : "falta avisar"}</small>
                </li>
              ))}
            </ul>
            <p className="rg-muted">{I.avisosEnviados} avisos enviados · {I.respuestasSintomas} respuestas anónimas de familias.</p>
          </div>
        </div>
      </section>
    </main>
  );
}
