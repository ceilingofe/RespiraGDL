import { NIVELES, PRONOSTICO, nivel } from "../data/demo.js";
import { PROTOCOLO, PASOS_CRISIS, SENALES_ALARMA, DATOS_SI, DATOS_NO, ROLES } from "../data/planAsma.js";
import { Semaforo, Icono } from "../components/ui.jsx";

// Ejemplo de PM2.5 por nivel para mostrar la píldora con número.
const EJEMPLO = { good: 12, ok: 28, bad: 62, vbad: 95, ext: 150 };
const RANGO = (i) => {
  const min = i === 0 ? 0 : NIVELES[i - 1].max + 1;
  const max = NIVELES[i].max;
  return max === Infinity ? `más de ${min - 1}` : `${min} a ${max}`;
};

export default function PlanAsma() {
  const hoy = nivel(PRONOSTICO[0].pm).id;
  return (
    <main className="rg-app rg-plan">
      <div className="rg-demo-note">Borrador del plan. Debe validarlo un médico antes de usarse con alumnos.</div>
      <header className="rg-app__head">
        <div>
          <p className="rg-eyebrow">Plan de asma escolar</p>
          <h1>Qué hace la escuela según el aire del día</h1>
          <p className="rg-plan__lead">
            Un protocolo corto para dirección, maestros y familias. Usa el semáforo de PM2.5 del sensor del salón y del SIMAJ.
            Orienta y recuerda; no diagnostica. Cada alumno sigue el plan de acción firmado por su médico.
          </p>
        </div>
        <div className="rg-app__actions">
          <a className="rg-pill rg-pill--primary" href="#/maestro">Abrir vista del maestro</a>
          <button className="rg-pill rg-pill--blue" onClick={() => window.print()}>Imprimir</button>
        </div>
      </header>

      <section className="rg-panel rg-surface-mist">
        <h2>1 · Protocolo por nivel del semáforo</h2>
        <div className="rg-levels">
          {NIVELES.map((n, i) => {
            const p = PROTOCOLO[n.id];
            return (
              <article key={n.id} className={`rg-level${n.id === hoy ? " is-today" : ""}`}>
                <header className={`rg-aq-bg--${n.id}`}>
                  <Semaforo pm={EJEMPLO[n.id]} />
                  <small>PM2.5 {RANGO(i)} µg/m³</small>
                  <h3>{p.titulo}</h3>
                  {n.id === hoy && <b className="rg-level__hoy">Hoy</b>}
                </header>
                <div>
                  <h4>Escuela</h4>
                  <ul className="rg-dots">{p.escuela.map((t) => <li key={t}>{t}</li>)}</ul>
                  <h4>Maestro</h4>
                  <ul className="rg-dots">{p.maestro.map((t) => <li key={t}>{t}</li>)}</ul>
                  {p.familias.length > 0 && (
                    <>
                      <h4>Familias</h4>
                      <ul className="rg-dots">{p.familias.map((t) => <li key={t}>{t}</li>)}</ul>
                    </>
                  )}
                </div>
              </article>
            );
          })}
        </div>
        <p className="rg-muted">Cortes simplificados para la demo, a partir de la NOM-025-SSA1-2021 (norma de 24 h: 45 µg/m³). Confirmar con el índice AIRE Y SALUD.</p>
      </section>

      <div className="rg-two rg-two--even">
        <section className="rg-panel rg-surface-aqua">
          <h2>2 · Guía de crisis</h2>
          <ol className="rg-steps rg-steps--static">
            {PASOS_CRISIS.map((x, i) => (
              <li key={i} className={x.urgente ? "is-urgent" : ""}>
                <span className="rg-step__n">{i + 1}</span>
                <span>{x.texto}</span>
              </li>
            ))}
          </ol>
        </section>
        <section className="rg-panel rg-aq-bg--vbad">
          <h2>Llamar al 911 si…</h2>
          <ul className="rg-dots rg-dots--big">{SENALES_ALARMA.map((t) => <li key={t}>{t}</li>)}</ul>
          <a className="rg-pill rg-pill--danger rg-tap" href="tel:911"><Icono name="telefono" /> 911</a>
        </section>
      </div>

      <section className="rg-panel rg-surface-sky">
        <h2>3 · Quién hace qué</h2>
        <div className="rg-roles">
          {ROLES.map((r) => (
            <div key={r.quien} className="rg-role">
              <h3>{r.quien}</h3>
              <ul className="rg-dots">{r.hace.map((t) => <li key={t}>{t}</li>)}</ul>
            </div>
          ))}
        </div>
      </section>

      <section className="rg-panel rg-surface-lilac">
        <h2><Icono name="candado" /> 4 · Datos: qué se guarda y qué no</h2>
        <div className="rg-two rg-two--even">
          <div>
            <h4>Sí se guarda</h4>
            <ul className="rg-dots">{DATOS_SI.map((t) => <li key={t}>{t}</li>)}</ul>
          </div>
          <div>
            <h4>Nunca se guarda</h4>
            <ul className="rg-dots rg-dots--no">{DATOS_NO.map((t) => <li key={t}>{t}</li>)}</ul>
          </div>
        </div>
      </section>
    </main>
  );
}
