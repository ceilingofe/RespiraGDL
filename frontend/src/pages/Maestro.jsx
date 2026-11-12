import { useState } from "react";
import { SALONES, PRONOSTICO, nivel } from "../data/demo.js";
import { Semaforo } from "./Tablero.jsx";

// Guía general de ejemplo. Debe validarla un médico antes de usarse con alumnos.
const PASOS = [
  "Mantén la calma y quédate con el alumno. Siéntalo un poco inclinado hacia adelante.",
  "Ayúdalo a usar su inhalador de rescate como indica su plan.",
  "Si no mejora en el tiempo que marca su plan, repite como indica el plan y avisa a la dirección.",
  "Si le cuesta hablar, tiene los labios azulados o no mejora, llama al 911.",
  "Avisa a la familia y anota la hora y lo que pasó.",
];

export default function Maestro() {
  const s = SALONES.find((x) => x.id === "3A");
  const hoy = PRONOSTICO[0].pm;
  const [guia, setGuia] = useState(false);
  const [paso, setPaso] = useState(0);
  return (
    <main className="rg-app rg-app--phone">
      <div className="rg-demo-note">Demo con datos simulados. La guía es un ejemplo y debe validarla un médico.</div>
      <div className="rg-phone">
        {!guia ? (
          <>
            <p className="rg-eyebrow">Grupo 3°A · hoy</p>
            <h1>Plan de asma</h1>
            <div className={`rg-today rg-aq-bg--${nivel(hoy).id}`}>
              <Semaforo pm={hoy} big />
              <p>{nivel(hoy).consejo}</p>
            </div>
            <div className="rg-phone__row">
              <div className="rg-kpi rg-surface-mint">
                <small>Alumnos con asma</small>
                <strong>{s.asma}</strong>
                <span>sin nombres</span>
              </div>
              <div className="rg-kpi rg-surface-sky">
                <small>Dentro del salón</small>
                <strong>{s.dentro}</strong>
                <span>{s.proteccion} % protegido</span>
              </div>
            </div>
            <ul className="rg-checklist">
              <li>Filtro encendido desde las 7:30</li>
              <li>Ventanas cerradas en recreo</li>
              <li>Recordar inhaladores en la mochila</li>
            </ul>
            <button className="rg-pill rg-pill--primary rg-full rg-tap" onClick={() => { setGuia(true); setPaso(0); }}>
              Guía de crisis
            </button>
          </>
        ) : (
          <>
            <button className="rg-pill rg-pill--blue rg-tap" onClick={() => setGuia(false)}>← Volver</button>
            <h1>Guía de crisis</h1>
            <p className="rg-muted">Paso {paso + 1} de {PASOS.length}</p>
            <div className="rg-step rg-surface-ice">
              <span className="rg-step__n">{paso + 1}</span>
              <p>{PASOS[paso]}</p>
            </div>
            <div className="rg-phone__row">
              <button className="rg-pill rg-pill--blue rg-tap" disabled={paso === 0} onClick={() => setPaso(paso - 1)}>Anterior</button>
              {paso < PASOS.length - 1 ? (
                <button className="rg-pill rg-pill--primary rg-tap" onClick={() => setPaso(paso + 1)}>Siguiente</button>
              ) : (
                <a className="rg-pill rg-pill--danger rg-tap" href="tel:911">Llamar al 911</a>
              )}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
