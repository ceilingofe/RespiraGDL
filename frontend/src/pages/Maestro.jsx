import { useEffect, useState } from "react";
import { MOCK_MAESTRA, SEMAFORO } from "../data/demo.js";
// import { API_URL } from "../data/demo.js"; // <- descomentar al conectar la API
import { Semaforo } from "./Tablero.jsx";

// Guía general de ejemplo, NO es diagnóstico ni indicación médica.
// Debe validarla un médico y siempre manda el plan de acción de cada alumno.
// (Texto fijo del frontend, no viene de la API.)
const PASOS_CRISIS = [
  "Siéntalo derecho, quédate con él y háblale con calma.",
  "Ayúdalo a usar su inhalador de rescate como indica su plan de acción.",
  "Espera unos minutos. Si no mejora, repite como indica su plan y avisa a la dirección.",
  "Si le cuesta hablar, tiene los labios azulados o no mejora, llama al 911 y avisa a su familia.",
];

export default function Maestro() {
  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Resumen del salón (semáforo y número de alumnos con asma) -> GET /salones/3B/hoy
  const [salon, setSalon] = useState(MOCK_MAESTRA);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Checklist "Qué hacer hoy". Hoy vive solo en el navegador; si backend guarda
  // las marcas, inicializar desde GET /salones/3B/hoy y mandar un POST en `marcar`.
  const [tareas, setTareas] = useState(MOCK_MAESTRA.tareas);

  // Estado de la interfaz (no es mock): muestra u oculta la guía de crisis.
  const [crisis, setCrisis] = useState(false);

  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Al conectar: descomenten el fetch y borren MOCK_MAESTRA de demo.js.
  useEffect(() => {
    // fetch(`${API_URL}/salones/3B/hoy`).then((r) => r.json()).then((d) => {
    //   setSalon(d);
    //   setTareas(d.tareas);
    // });
  }, []);

  const marcar = (id) => {
    setTareas((t) => t.map((x) => (x.id === id ? { ...x, hecho: !x.hecho } : x)));
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // fetch(`${API_URL}/salones/3B/tareas/${id}`, { method: "POST" });
  };

  return (
    <main className="rg-app rg-app--phone">
      <div className="rg-demo-note">Demo con datos simulados. La guía es un ejemplo y debe validarla un médico.</div>
      <div className="rg-phone-bar">
        <span className="rg-muted">Vista del maestro · {salon.momento}</span>
        <a className="rg-pill rg-pill--blue rg-tap" href="#/tablero">Vista del director</a>
      </div>
      <div className="rg-phone">
        {!crisis ? (
          <>
            <p className="rg-eyebrow">Hoy</p>
            <h1>{salon.titulo}</h1>

            <div className={`rg-today rg-aq-bg--${SEMAFORO[salon.semaforo]?.id}`}>
              <small>Semáforo de hoy</small>
              <Semaforo color={salon.semaforo} pm={salon.pm25} big />
            </div>
            <div className="rg-kpi rg-surface-mint">
              <small>Alumnos con asma en el grupo</small>
              <strong>{salon.conAsma}</strong>
              <span>Revisa que traigan su inhalador y su plan de acción.</span>
            </div>

            <h2 className="rg-phone__h2">Qué hacer hoy</h2>
            <ul className="rg-checks">
              {tareas.map((t) => (
                <li key={t.id}>
                  <label className={t.hecho ? "is-done" : ""}>
                    <input type="checkbox" checked={t.hecho} onChange={() => marcar(t.id)} />
                    {t.texto}
                  </label>
                </li>
              ))}
            </ul>

            <button className="rg-pill rg-pill--danger rg-full rg-sos" onClick={() => setCrisis(true)}>
              Un alumno tiene una crisis
            </button>
          </>
        ) : (
          <>
            <button className="rg-pill rg-pill--blue rg-tap" onClick={() => setCrisis(false)}>← Volver</button>
            <h1>Guía de crisis</h1>
            <ol className="rg-steps">
              {PASOS_CRISIS.map((p, i) => (
                <li key={i} className="rg-step rg-surface-ice">
                  <span className="rg-step__n">{i + 1}</span>
                  <p>{p}</p>
                </li>
              ))}
            </ol>
            <a className="rg-pill rg-pill--danger rg-full rg-sos" href="tel:911">Llamar al 911</a>
            <p className="rg-muted">Guía general de ejemplo. Siempre sigue el plan de acción del alumno.</p>
          </>
        )}
      </div>
    </main>
  );
}
