import { useEffect, useState } from "react";
import { ArtAula, ArtAsma, ArtPronostico, Tile } from "../art/Art.jsx";

const TEMAS = [
  {
    id: "green",
    pilar: "Aula Limpia",
    sub: "Diseño de filtro y monitoreo",
    t1: "Aire limpio,",
    t2: "aulas seguras",
    p: "Un prototipo para ayudar a las escuelas a anticipar días de aire contaminado y organizar acciones de prevención. La reducción con filtro aún debe medirse.",
    Art: ArtAula,
  },
  {
    id: "aqua",
    pilar: "Plan de asma",
    sub: "Guía para el maestro",
    t1: "Un plan para",
    t2: "cada salón",
    p: "El maestro sabe cuántos alumnos con asma tiene (sin nombres), qué hacer hoy y cómo actuar si hay una crisis.",
    Art: ArtAsma,
  },
  {
    id: "blue",
    pilar: "Pronóstico",
    sub: "Aviso con un día de anticipación",
    t1: "Un día",
    t2: "de ventaja",
    p: "Un modelo con datos del SIMAJ y del clima avisa a escuelas y familias antes de un día de mala calidad del aire.",
    Art: ArtPronostico,
  },
];

function Hero() {
  const [i, setI] = useState(0);
  const [paused, setPaused] = useState(false);
  useEffect(() => {
    const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduce || paused) return;
    const t = setInterval(() => setI((x) => (x + 1) % TEMAS.length), 5000);
    return () => clearInterval(t);
  }, [paused]);
  const tema = TEMAS[i];
  return (
    <section className={`rg-hero rg-theme-${tema.id}`} onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
      <div className="rg-hero__art" aria-hidden="true">
        {TEMAS.map((t, k) => (
          <t.Art key={t.id} className={`rg-hero__img${k === i ? " is-on" : ""}`} />
        ))}
      </div>
      <div className="rg-hero__copy" key={tema.id}>
        <h1>
          <span>{tema.t1}</span>
          <span>{tema.t2}</span>
        </h1>
        <p>{tema.p}</p>
        <a className="rg-pill rg-hero__cta" href="#/simulador">Explorar la escuela 3D ↗</a>
      </div>
      <div className="rg-pillars" role="tablist" aria-label="Pilares del proyecto">
        {TEMAS.map((t, k) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={k === i}
            className={`rg-pillar rg-pillar--${t.id}${k === i ? " is-active" : ""}`}
            onClick={() => setI(k)}
          >
            <t.Art className="rg-pillar__thumb" />
            <strong>{t.pilar}</strong>
            <small>{t.sub}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

function Intro() {
  return (
    <section className="rg-section rg-split-intro rg-reveal">
      <div className="rg-blob rg-blob--left"><ArtPronostico /></div>
      <div className="rg-split-intro__text">
        <h2>Protegemos a los niños donde pasan seis horas al día</h2>
        <p>
          El resumen SIMAJ de Miravalle registra 571 días observados con promedio de PM2.5 mayor a 25 µg/m³
          en 2020–2024, con 68.6 % de cobertura horaria. Empezamos con una escuela ficticia para probar el flujo de prevención.
        </p>
        <a className="rg-pill rg-pill--blue" href="#/tablero">Ver la demo</a>
      </div>
      <div className="rg-blob rg-blob--right"><ArtAula /></div>
    </section>
  );
}

const PROBLEMAS = [
  ["humo", "PM2.5 en la ciudad"],
  ["asma", "Asma infantil"],
  ["salon", "Salones sin filtrar"],
  ["norma", "571 días observados · 2020–2024"],
  ["recreo", "Recreo al aire libre"],
  ["familia", "Familias sin aviso"],
];

function Problemas() {
  return (
    <section className="rg-section rg-reveal">
      <header className="rg-section__head">
        <h2>Lo que queremos cambiar,<br />un salón a la vez</h2>
        <p>El Anuario de Morbilidad reporta 13,613 casos nuevos de asma en Jalisco en 2023, en todas las edades. Es contexto de salud pública; no una estimación de asma infantil causada por contaminación. <a href="#/evidencia">Ver fuentes y límites</a>.</p>
      </header>
      <div className="rg-grid3">
        {PROBLEMAS.map(([k, label]) => (
          <figure key={k} className="rg-photo">
            <Tile kind={k} className="rg-photo__img" />
            <figcaption>{label}</figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}

function Como() {
  return (
    <section id="como" className="rg-section rg-reveal">
      <header className="rg-section__head">
        <h2>Medimos, filtramos<br />y avisamos</h2>
        <p>Cuatro piezas baratas que una escuela pública puede armar y mantener.</p>
      </header>
      <div className="rg-overlap rg-overlap--right">
        <div className="rg-overlap__img"><ArtAula /></div>
        <div className="rg-overlap__card rg-surface-mint">
          <h3>Dentro contra fuera</h3>
          <p>
            El diseño contempla un ventilador, cuatro filtros MERV-13 y dos sensores PM2.5. En el montaje actual no contamos
            con esos componentes: el tablero demuestra la comparación con lecturas simuladas. El MQ-135 no mide partículas.
          </p>
          <a className="rg-pill" href="#/tablero">Ver el tablero</a>
        </div>
      </div>
      <div className="rg-overlap rg-overlap--left">
        <div className="rg-overlap__img"><ArtAsma /></div>
        <div className="rg-overlap__card rg-surface-ice">
          <h3>Un plan, no una alarma</h3>
          <p>
            El maestro consulta un semáforo, un conteo ficticio y una guía orientativa pendiente de revisión médica.
            Los avisos demuestran el flujo de comunicación; no garantizamos entregas automáticas a una hora fija.
          </p>
          <a className="rg-pill rg-pill--blue" href="#/maestro">Ver vista del maestro</a>
        </div>
      </div>
    </section>
  );
}

const ESCUELAS = [
  ["Miravalle", "Guadalajara", "humo", "rg-surface-lilac"],
  ["Las Pintas", "Tlaquepaque", "recreo", "rg-surface-aqua"],
  ["Santa Fe", "Tlajomulco", "salon", "rg-surface-lilac"],
];

function Escuelas() {
  return (
    <section id="escuelas" className="rg-section rg-reveal">
      <header className="rg-section__head">
        <h2>Zonas para un piloto propuesto</h2>
        <p>Escenarios ficticios cercanos a estaciones SIMAJ; no son escuelas participantes. Presupuesto preliminar del diseño completo: cerca de $3,700 MXN por salón, sujeto a cotización.</p>
      </header>
      <div className="rg-grid3">
        {ESCUELAS.map(([n, m, k, s]) => (
          <article key={n} className={`rg-initiative ${s}`}>
            <Tile kind={k} className="rg-initiative__img" />
            <h3>{n}</h3>
            <p>{m}</p>
            <a className="rg-pill rg-pill--white" href="#/tablero">Ver datos</a>
          </article>
        ))}
      </div>
    </section>
  );
}

const HISTORIAS = [
  ["Consultar el pronóstico de Miravalle", "Ejemplo simulado", "humo", "#/tablero"],
  ["Comparar PM2.5 dentro y fuera del 3°A", "Ejemplo simulado · no es medición física", "salon", "#/tablero"],
  ["Revisar actividades para un grupo con asma", "Ejemplo simulado", "asma", "#/maestro"],
  ["Preparar un aviso a las familias", "Ejemplo simulado · no es constancia de envío", "familia", "#/maestro"],
];

function Historias() {
  return (
    <section className="rg-section rg-reveal">
      <div className="rg-stories">
        <h2>Lo que puedes probar en la demo</h2>
        <div className="rg-stories__grid">
          {HISTORIAS.map(([t, d, k, href]) => (
            <a key={t} className="rg-story" href={href}>
              <Tile kind={k} className="rg-story__img" />
              <div className="rg-story__shade" />
              <div className="rg-story__text">
                <strong>{t}</strong>
                <small>{d}</small>
              </div>
              <span className="rg-story__arrow" aria-hidden="true">↗</span>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

function Unete() {
  const [n, setN] = useState(5);
  return (
    <section id="unete" className="rg-section rg-unete rg-reveal">
      <h2>Lleva Respira GDL a tu escuela</h2>
      <p>¿Cuántos salones quieres proteger?</p>
      <div className="rg-amounts" role="radiogroup" aria-label="Número de salones">
        {[1, 5, 10, 20].map((v) => (
          <button key={v} role="radio" aria-checked={n === v} className={`rg-amount${n === v ? " is-on" : ""}`} onClick={() => setN(v)}>
            {v} {v === 1 ? "salón" : "salones"}
          </button>
        ))}
      </div>
      <p className="rg-unete__total">
        Presupuesto ilustrativo, sin cotizar: <strong>${(n * 3700).toLocaleString("es-MX")} MXN</strong>
      </p>
      <a className="rg-pill rg-pill--primary" href="https://github.com/ceilingofe/respiragdl">Ver cómo armarlo</a>
    </section>
  );
}

export default function Landing() {
  return (
    <>
      <div className="rg-demo-note" role="status">Prototipo de hackathon · escuelas ficticias y ejemplos simulados. <a href="#/evidencia">Consulta la evidencia y el alcance real</a>.</div>
      <Hero />
      <Intro />
      <Problemas />
      <Como />
      <Escuelas />
      <Historias />
      <Unete />
    </>
  );
}
