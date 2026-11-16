import { useState } from "react";
import { SEMAFORO } from "../data/demo.js";
import TarjetaModal from "../components/TarjetaModal.jsx";
import NotaDatos from "../components/NotaDatos.jsx";
import { apiAvisos, useConexionApi } from "../data/useAvisos.js";
import { useMaestraDatos } from "../data/useDatos.js";
import { Semaforo } from "./Tablero.jsx";
import { ResumenPlan } from "./Alumno.jsx";
import { usePlanes, DETONANTES } from "../data/planes.js";
import { salir, useSesion } from "../data/sesion.js";

// Cuenta cuántos alumnos tienen cada factor, de más a menos. Solo los que aparecen en los planes.
function contarFactores(planes) {
  return DETONANTES
    .map((d) => ({ ...d, alumnos: planes.filter((p) => p.detonantes.includes(d.id)).length }))
    .filter((d) => d.alumnos > 0)
    .sort((a, b) => b.alumnos - a.alumnos);
}
const alumnos = (n) => `${n} ${n === 1 ? "alumno" : "alumnos"}`;

// Guía general de ejemplo, NO es diagnóstico ni indicación médica.
// Debe validarla un médico y siempre manda el plan de acción de cada alumno.
// (Texto fijo del frontend, no viene de la API.)
const PASOS_CRISIS = [
  "Si le cuesta mucho respirar o hablar, está somnoliento o tiene labios azulados, llama al 911 de inmediato y avisa a la dirección y a su familia. No esperes a los siguientes pasos.",
  "Siéntalo derecho y llévalo a un lugar sin humo ni polvo. Quédate con él y háblale con calma.",
  "Ayúdalo a usar su inhalador de rescate como indica su plan de acción.",
  "Si no mejora o empeora, solicita atención urgente y sigue las indicaciones del servicio de emergencias y del plan individual. No improvises dosis ni repeticiones.",
];

export default function Maestro() {
  // Grupo de la maestra que inició sesión (maestra1 = 1° A ... maestra6 = 6° B).
  const salonId = useSesion()?.salonId ?? "3A";

  // Resumen del salón (semáforo, alumnos con asma) y "Qué hacer hoy": GET /salones/{salonId}/hoy cada
  // minuto; las marcas se guardan con POST /salones/{salonId}/tareas/{id}. Sin API: datos simulados.
  const modoApi = useConexionApi(apiAvisos);
  const { salon, origen, marcar, errorTarea } = useMaestraDatos(modoApi, salonId);
  const tareas = salon.tareas;

  // Estado de la interfaz (no es mock): muestra u oculta la guía de crisis.
  const [crisis, setCrisis] = useState(false);

  // Planes de acción del grupo, sin datos que identifiquen al alumno (simulados + capturados en este navegador).
  const planes = usePlanes(salon.salonId);
  const factores = contarFactores(planes);

  return (
    <main className="rg-app rg-app--phone">
      <NotaDatos origen={origen} extra="La guía es un ejemplo y debe validarla un médico." />
      <p className="rg-muted">Orientación general: <a href="https://www.nhlbi.nih.gov/es/salud/asma/crisis" target="_blank" rel="noreferrer">NIH · crisis de asma</a>. Ante signos de alarma, pide atención inmediata.</p>
      <div className="rg-phone-bar">
        <span className="rg-muted">Vista del maestro · {salon.momento}</span>
        <button type="button" className="rg-pill rg-pill--blue rg-tap" onClick={salir}>Salir</button>
      </div>
      <div className="rg-phone">
        {!crisis ? (
          <>
            <p className="rg-eyebrow">Hoy</p>
            <h1>{salon.titulo}</h1>

            <div className={`rg-today rg-aq-bg--${SEMAFORO[salon.semaforo]?.id}`}>
              <small>Semáforo de hoy</small>
              {salon.semaforo || salon.pm25 != null
                ? <Semaforo color={salon.semaforo} pm={salon.pm25} big />
                : <strong>Sin dato de hoy</strong>}
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
            {errorTarea && (
              <p className="rg-aviso__error" role="alert">No se pudo guardar la marca. Revise la conexión e intente de nuevo.</p>
            )}

            <h2 className="rg-phone__h2">Planes de acción del grupo</h2>

            <TarjetaModal titulo="Factores a cuidar" superficie="rg-surface-mint" cta="Ver factores"
              resumen={factores.length ? factores.map((f) => f.nombre).join(", ") : "Ningún expediente indica factores"}>
              <p className="rg-muted">Lo que les detona una crisis a los alumnos del grupo, según sus expedientes.</p>
              {factores.length ? (
                <ul className="rg-plans">
                  {factores.map((f) => (
                    <li key={f.id} className="rg-plan rg-plan--row rg-surface-ice">
                      <strong>{f.nombre}</strong><span>{alumnos(f.alumnos)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p>Ningún expediente indica factores.</p>
              )}
            </TarjetaModal>

            <TarjetaModal titulo="Expedientes" superficie="rg-surface-lilac" cta="Ver expedientes"
              resumen={`${alumnos(planes.length)} con expediente`}>
              <p className="rg-modal__count">{alumnos(planes.length)} con expediente</p>
              {planes.length > 0 && (
                <ul className="rg-plans">
                  {planes.map((p) => (
                    <li key={p.id} className="rg-plan rg-surface-ice"><ResumenPlan plan={p} /></li>
                  ))}
                </ul>
              )}
              <p className="rg-muted">Sin datos que identifiquen al alumno. No es diagnóstico: recuerda qué hacer en la escuela.</p>
            </TarjetaModal>

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
            {/* El sistema no guarda qué familia es de qué alumno (cero nombres), así que no avisa solo:
                la maestra llama al teléfono que la escuela ya tiene registrado. */}
            <div className="rg-plan rg-surface-lilac">
              <strong>Avisa a su familia</strong>
              <span>Llama a la familia del alumno al número de teléfono que ya tiene registrado la escuela.</span>
            </div>
            <p className="rg-muted">
              Guía general de ejemplo. Siempre sigue el plan de acción del alumno. Respira GDL orienta y alerta;
              no diagnostica ni sustituye la atención médica.
            </p>
          </>
        )}
      </div>
    </main>
  );
}
