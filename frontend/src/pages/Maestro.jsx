import { useEffect, useState } from "react";
import { SALONES, PRONOSTICO, nivel } from "../data/demo.js";
import { PROTOCOLO, PASOS_CRISIS, SENALES_ALARMA } from "../data/planAsma.js";
import { post, horaActual } from "../lib/api.js";
import { Semaforo, Icono, DemoNote } from "../components/ui.jsx";

// Cronómetro desde que el alumno usó su inhalador. No marca minutos fijos:
// el tiempo de espera lo dice el plan firmado por el médico de cada alumno.
function Cronometro() {
  const [inicio, setInicio] = useState(null);
  const [ahora, setAhora] = useState(Date.now());
  useEffect(() => {
    if (!inicio) return;
    const t = setInterval(() => setAhora(Date.now()), 1000);
    return () => clearInterval(t);
  }, [inicio]);
  if (!inicio) {
    return (
      <button className="rg-pill rg-pill--white rg-full rg-tap" onClick={() => { setInicio(Date.now()); setAhora(Date.now()); }}>
        <Icono name="reloj" /> Ya usó el inhalador: medir tiempo
      </button>
    );
  }
  const s = Math.floor((ahora - inicio) / 1000);
  return (
    <div className="rg-timer" aria-live="polite">
      <Icono name="reloj" />
      <strong>{Math.floor(s / 60)}:{String(s % 60).padStart(2, "0")}</strong>
      <span>desde el inhalador · compáralo con su plan</span>
    </div>
  );
}

function Inicio({ salon, setSalon, hoy, onCrisis }) {
  const s = SALONES.find((x) => x.id === salon);
  const n = nivel(hoy);
  const tareas = PROTOCOLO[n.id].maestro;
  const [hechas, setHechas] = useState({});
  useEffect(() => setHechas({}), [salon]);
  const total = Object.values(hechas).filter(Boolean).length;
  return (
    <>
      <div className="rg-phone__top">
        <div>
          <p className="rg-eyebrow">Grupo {salon} · hoy</p>
          <h1>Plan de asma del grupo</h1>
        </div>
        <label className="rg-select">
          <span className="rg-sr">Grupo</span>
          <select value={salon} onChange={(e) => setSalon(e.target.value)}>
            {SALONES.map((x) => <option key={x.id} value={x.id}>{x.id}</option>)}
          </select>
        </label>
      </div>
      <div className="rg-phone__row">
        <div className={`rg-kpi rg-aq-bg--${n.id}`}>
          <small>Hoy</small>
          <Semaforo pm={hoy} />
          <span>{PROTOCOLO[n.id].titulo}</span>
        </div>
        <div className="rg-kpi rg-surface-lilac">
          <small>Con asma</small>
          <strong>{s.asma}</strong>
          <span>alumnos, sin nombres</span>
        </div>
      </div>
      <div className="rg-kpi rg-surface-sky rg-kpi--row">
        <div>
          <small>Dentro del salón</small>
          <strong>{s.dentro}</strong>
        </div>
        <span>{s.filtro ? `${s.proteccion} % menos PM2.5 que afuera` : "Sin filtro: dentro casi igual que afuera"}</span>
      </div>
      <div>
        <h2 className="rg-phone__h2">Qué hacer hoy <small>{total} de {tareas.length}</small></h2>
        <ul className="rg-todo">
          {tareas.map((t) => (
            <li key={t}>
              <label className={hechas[t] ? "is-done" : ""}>
                <input type="checkbox" checked={!!hechas[t]} onChange={() => setHechas({ ...hechas, [t]: !hechas[t] })} />
                <span className="rg-todo__box" aria-hidden="true"><Icono name="check" /></span>
                {t}
              </label>
            </li>
          ))}
        </ul>
      </div>
      <button className="rg-pill rg-pill--danger rg-full rg-crisis" onClick={onCrisis}>
        Un alumno tiene una crisis
      </button>
      <p className="rg-muted rg-center">Abre la guía paso a paso y avisa a la familia. No sustituye la atención médica.</p>
      <a className="rg-pill rg-pill--blue rg-full rg-tap" href="#/plan">
        <Icono name="documento" /> Ver plan de asma escolar
      </a>
    </>
  );
}

function Crisis({ salon, onSalir }) {
  const [paso, setPaso] = useState(0);
  const [aviso, setAviso] = useState(null);
  const [llamo, setLlamo] = useState(false);
  const [registrado, setRegistrado] = useState(null);
  const p = PASOS_CRISIS[paso];
  const ultimo = paso === PASOS_CRISIS.length - 1;

  const registrar = () => {
    const hora = horaActual();
    setRegistrado(hora);
    // Registro anónimo: solo grupo, hora y si se avisó / llamó. Nunca nombre del alumno.
    post("/plan-asma/incidentes", { salon_id: salon, aviso_familia: !!aviso, llamada_911: llamo });
  };

  if (registrado) {
    return (
      <div className="rg-done">
        <span className="rg-done__ok"><Icono name="check" /></span>
        <h1>Crisis registrada</h1>
        <p>Grupo {salon} · {registrado}. Solo se guardó el grupo y la hora, sin nombre.</p>
        <p className="rg-muted">La dirección la ve en el tablero. Si el alumno sigue mal, llama al 911.</p>
        <button className="rg-pill rg-pill--primary rg-full rg-tap" onClick={onSalir}>Volver al plan del grupo</button>
      </div>
    );
  }

  return (
    <>
      <button className="rg-pill rg-pill--blue rg-tap rg-back" onClick={onSalir}>← Volver</button>
      <div>
        <h1>Guía de crisis de asma</h1>
        <p className="rg-muted">Según el plan firmado por su médico · paso {paso + 1} de {PASOS_CRISIS.length}</p>
      </div>
      <ol className="rg-steps">
        {PASOS_CRISIS.map((x, i) => (
          <li key={i} className={`${i === paso ? "is-on" : ""}${i < paso ? " is-past" : ""}${x.urgente ? " is-urgent" : ""}`}>
            <button onClick={() => setPaso(i)} aria-current={i === paso ? "step" : undefined}>
              <span className="rg-step__n">{i < paso ? <Icono name="check" /> : i + 1}</span>
              <span>{x.texto}</span>
            </button>
          </li>
        ))}
      </ol>
      {p.espera && <Cronometro />}
      {p.urgente && (
        <div className="rg-alarm">
          <strong>Señales de alarma</strong>
          <ul>{SENALES_ALARMA.map((t) => <li key={t}>{t}</li>)}</ul>
          <a className="rg-pill rg-pill--danger rg-full rg-tap" href="tel:911" onClick={() => setLlamo(true)}>
            <Icono name="telefono" /> Llamar al 911
          </a>
        </div>
      )}
      {ultimo && (
        <>
          {aviso ? (
            <p className="rg-ok"><Icono name="check" /> Se avisó a la familia a las {aviso}</p>
          ) : (
            <button className="rg-pill rg-pill--white rg-full rg-tap" onClick={() => setAviso(horaActual())}>
              Ya avisé a la familia
            </button>
          )}
        </>
      )}
      <div className="rg-phone__row">
        <button className="rg-pill rg-pill--blue rg-tap" disabled={paso === 0} onClick={() => setPaso(paso - 1)}>Anterior</button>
        {!ultimo ? (
          <button className="rg-pill rg-pill--primary rg-tap" onClick={() => setPaso(paso + 1)}>Siguiente</button>
        ) : (
          <button className="rg-pill rg-pill--primary rg-tap" onClick={registrar}>Registrar sin nombre</button>
        )}
      </div>
    </>
  );
}

export default function Maestro() {
  const [salon, setSalon] = useState("3A");
  const [crisis, setCrisis] = useState(false);
  const hoy = PRONOSTICO[0].pm;
  return (
    <main className="rg-app rg-app--phone">
      <DemoNote simulado>Demo con datos simulados. La guía es un borrador y debe validarla un médico.</DemoNote>
      <div className="rg-phone">
        {crisis ? (
          <Crisis salon={salon} onSalir={() => setCrisis(false)} />
        ) : (
          <Inicio salon={salon} setSalon={setSalon} hoy={hoy} onCrisis={() => setCrisis(true)} />
        )}
      </div>
    </main>
  );
}
