import { useState } from "react";
import { ESCUELAS, nivel } from "../data/demo.js";
import { PROTOCOLO } from "../data/planAsma.js";
import { useApi, filas } from "../lib/api.js";
import { Semaforo, Icono, BarraProteccion, DemoNote } from "../components/ui.jsx";

const ORDEN = {
  manana: (a, b) => b.pmManana - a.pmManana,
  proteccion: (a, b) => a.proteccion - b.proteccion,
  faltas: (a, b) => b.faltas.ahora - a.faltas.ahora,
};

// Vista para autoridades (SEJ, municipio): todas las escuelas piloto en una tabla.
export default function Red() {
  const { data: escuelas, simulado } = useApi("/escuelas", ESCUELAS, filas("id", "pmHoy", "pmManana", "salones", "conFiltro", "faltas"));
  const [orden, setOrden] = useState("manana");
  const lista = [...escuelas].sort(ORDEN[orden]);

  const sum = (f) => escuelas.reduce((a, e) => a + f(e), 0);
  const salones = sum((e) => e.salones);
  const conFiltro = sum((e) => e.conFiltro);
  const asma = sum((e) => e.asma);
  const antes = sum((e) => e.faltas.antes);
  const ahora = sum((e) => e.faltas.ahora);
  const recreo = sum((e) => e.recreo);
  const fuera = sum((e) => e.fueraNorma);
  const alerta = escuelas.filter((e) => ["vbad", "ext"].includes(nivel(e.pmManana).id) || e.conFiltro < e.salones);
  const faltan = salones - conFiltro;

  return (
    <main className="rg-app">
      <DemoNote simulado={simulado} />
      <header className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Red de escuelas · vista de autoridades</p>
          <h1>Escuelas piloto de la zona metropolitana</h1>
          <p className="rg-muted">Miravalle, Las Pintas y Santa Fe · datos agregados, sin nombres de alumnos</p>
        </div>
        <a className="rg-pill rg-pill--blue" href="#/plan">Ver plan de asma escolar</a>
      </header>

      <section className="rg-kpis rg-kpis--4">
        <div className="rg-kpi rg-surface-mint">
          <small>Escuelas en la red</small>
          <strong>{escuelas.length}</strong>
          <span>{salones} salones · {conFiltro} con filtro</span>
        </div>
        <div className="rg-kpi rg-surface-aqua">
          <small>Alumnos con asma cubiertos</small>
          <strong>{asma}</strong>
          <span>con plan de asma en su grupo</span>
        </div>
        <div className="rg-kpi rg-surface-sky">
          <small>Faltas por asma</small>
          <strong>−{Math.round((1 - ahora / antes) * 100)} %</strong>
          <span>{antes} → {ahora} contra el ciclo pasado</span>
        </div>
        <div className="rg-kpi rg-surface-lilac">
          <small>Días con recreo protegido</small>
          <strong>{Math.round((recreo / fuera) * 100)} %</strong>
          <span>{recreo} de {fuera} días fuera de norma</span>
        </div>
      </section>

      {alerta.length > 0 && (
        <section className="rg-alert" role="status">
          <Icono name="alerta" />
          <div>
            <strong>Para decidir hoy</strong>
            <ul>
              {alerta.map((e) => (
                <li key={e.id}>
                  {e.nombre}: mañana <Semaforo pm={e.pmManana} />
                  {e.conFiltro < e.salones && ` · faltan ${e.salones - e.conFiltro} filtros`}
                </li>
              ))}
            </ul>
          </div>
        </section>
      )}

      <section className="rg-panel rg-surface-mist">
        <div className="rg-panel__head">
          <h2>Escuelas</h2>
          <div className="rg-selector" role="group" aria-label="Ordenar por">
            {[["manana", "Aire de mañana"], ["proteccion", "Menor protección"], ["faltas", "Más faltas"]].map(([k, t]) => (
              <button key={k} className={`rg-amount rg-amount--sm${orden === k ? " is-on" : ""}`} onClick={() => setOrden(k)}>{t}</button>
            ))}
          </div>
        </div>
        <div className="rg-schools">
          {lista.map((e) => {
            const n = nivel(e.pmManana);
            return (
              <article key={e.id} className="rg-school">
                <header>
                  <div>
                    <h3>{e.nombre}</h3>
                    <small>{e.municipio} · {e.estacion}</small>
                  </div>
                  {e.id === "miravalle" && <a className="rg-pill rg-pill--white" href="#/tablero">Tablero <Icono name="flecha" /></a>}
                </header>
                <dl>
                  <div><dt>Hoy</dt><dd><Semaforo pm={e.pmHoy} /></dd></div>
                  <div><dt>Mañana</dt><dd><Semaforo pm={e.pmManana} /></dd></div>
                  <div><dt>Filtros</dt><dd>{e.conFiltro} de {e.salones}</dd></div>
                  <div><dt>Protección</dt><dd><BarraProteccion valor={e.proteccion} minimo={40} /></dd></div>
                  <div><dt>Con asma</dt><dd>{e.asma}</dd></div>
                  <div><dt>Faltas por asma</dt><dd>{e.faltas.antes} → <b>{e.faltas.ahora}</b></dd></div>
                </dl>
                <p className="rg-school__plan"><b>Plan para mañana:</b> {PROTOCOLO[n.id].escuela[0]}</p>
              </article>
            );
          })}
        </div>
      </section>

      <section className="rg-panel rg-surface-mint2">
        <h2>Costo para cubrir la red</h2>
        <p>
          Faltan <b>{faltan}</b> salones sin filtro. A unos $3,700 MXN por kit (ventilador, 4 filtros MERV-13 y dos sensores), cubrirlos cuesta
          cerca de <b>${(faltan * 3700).toLocaleString("es-MX")} MXN</b>. Solo el filtro, sin sensores, cuesta unos $2,200 MXN por salón.
        </p>
        <p className="rg-muted">Precios estimados del plan del proyecto; confirmar con proveedores.</p>
      </section>
    </main>
  );
}
