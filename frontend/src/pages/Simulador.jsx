import { useEffect, useState } from "react";
import EscuelaIsometrica, { estadoAula } from "../components/EscuelaIsometrica.jsx";
import { crearEscenario, avanzar, configurarSalon, cambiarPresupuesto, distribuirFiltros, resumen, SUPUESTOS } from "../data/simulacion.js";
import "../styles/simulador.css";

const PRESETS = [{ nombre: "Jornada tranquila", fuera: 20 }, { nombre: "Tráfico de entrada", fuera: 62 }, { nombre: "Contaminación alta", fuera: 110 }];

function Tendencia({ historial, salon }) {
  const maximo = Math.max(30, ...historial.flatMap((p) => [p.salones[salon].dentro, p.salones[salon].sinFiltro]));
  const ultimoMinuto = Math.max(60, historial.at(-1).minuto);
  const puntos = (campo) => historial.map((p) => `${38 + p.minuto / ultimoMinuto * 322},${112 - p.salones[salon][campo] / maximo * 92}`).join(" ");
  return (
    <figure className="rg-sim-trend">
      <figcaption>Salón {salon} · comparación bajo los mismos supuestos</figcaption>
      <svg viewBox="0 0 385 140" role="img" aria-label={`Concentración interior simulada del salón ${salon} comparada con el mismo salón sin filtro. Minuto ${historial.at(-1).minuto}.`}>
        <path d="M38 15V112H365" fill="none" stroke="var(--rg-sage)" />
        <text x="1" y="22">{Math.ceil(maximo)}</text><text x="20" y="115">0</text><text x="38" y="132">0 min</text><text x="322" y="132">{ultimoMinuto} min</text>
        <polyline points={puntos("sinFiltro")} fill="none" stroke="var(--rg-muted)" strokeWidth="2" strokeDasharray="5 5" />
        <polyline points={puntos("dentro")} fill="none" stroke="var(--rg-teal)" strokeWidth="3" strokeLinejoin="round" />
      </svg>
      <div className="rg-sim-legend"><span><i />Con el reparto actual</span><span><i className="is-baseline" />Sin filtros</span><span>PM2.5 · µg/m³</span></div>
    </figure>
  );
}

export default function Simulador() {
  const [escenario, setEscenario] = useState(crearEscenario);
  const [seleccionado, seleccionar] = useState("3A");
  const [reproduciendo, reproducir] = useState(false);
  const [acercar, setAcercar] = useState(false);
  const [aviso, setAviso] = useState("");
  const aula = escenario.salones.find((s) => s.id === seleccionado);
  const estado = estadoAula(aula);
  const total = resumen(escenario);
  useEffect(() => {
    if (!reproduciendo || escenario.minuto >= 180) return undefined;
    const timer = setInterval(() => setEscenario((e) => avanzar(e, 1)), 700);
    return () => clearInterval(timer);
  }, [reproduciendo, escenario.minuto >= 180]);
  const marcha = reproduciendo && escenario.minuto < 180;
  const cambiarAula = (cambios) => {
    try { setEscenario(configurarSalon(escenario, seleccionado, cambios)); setAviso(""); }
    catch (error) { setAviso(error.message); }
  };
  const reiniciar = (fuera = escenario.fuera) => { reproducir(false); setEscenario(crearEscenario({ fuera })); setAviso("Escenario reiniciado. Todos los datos de esta vista son simulados."); };
  return (
    <main className="rg-simulator">
      <div className="rg-sim-intro">
        <div>
          <p className="rg-eyebrow">Escuela 3D · laboratorio de decisiones</p>
          <h1>Un patio. Seis salones.<br />Ensaya la mejor decisión.</h1>
          <p>Cambia el aire de afuera, prueba un filtro y observa lo que ocurre dentro. Sin tocar datos reales.</p>
        </div>
        <a className="rg-pill rg-pill--blue" href="#/evidencia">Ver evidencia del proyecto ↗</a>
      </div>
      <div className="rg-sim-disclosure" role="note"><strong>Simulación educativa</strong><span>Escuela, personas y lecturas ficticias. Modelo sin calibrar; no predice crisis ni certifica aire seguro.</span></div>
      <div className="rg-sim-layout">
        <section className="rg-campus" aria-label="Mapa interactivo de aulas">
          <div className="rg-campus__toolbar"><span><i className={marcha ? "is-playing" : ""} />{marcha ? "Ensayo en marcha" : "Explora a tu ritmo"}</span><strong>Minuto {escenario.minuto} / 180</strong><button className="rg-pill rg-pill--plain" aria-pressed={acercar} onClick={() => setAcercar(!acercar)}>{acercar ? "Vista general" : "Acercar salón"}</button></div>
          <EscuelaIsometrica salones={escenario.salones} seleccionado={seleccionado} seleccionar={seleccionar} reproduciendo={marcha} acercar={acercar} />
          <div className="rg-campus__playback">
            <button className="rg-pill rg-pill--primary" disabled={escenario.minuto >= 180} onClick={() => reproducir(!reproduciendo)}>{marcha ? "Pausar" : "Reproducir"}</button>
            <button className="rg-pill rg-pill--blue" disabled={escenario.minuto >= 180} onClick={() => { reproducir(false); setEscenario(avanzar(escenario, Math.min(5, 180 - escenario.minuto))); }}>Avanzar 5 min</button>
            <button className="rg-pill rg-pill--plain" onClick={() => reiniciar()}>Reiniciar</button>
          </div>
          <p className="rg-campus__help">Selecciona un salón y usa Acercar para verlo a detalle. Personas y dispositivos ilustrativos; no representan alumnos reales ni sensores conectados.</p>
        </section>
        <aside className="rg-sim-room-panel" aria-label={`Controles del salón ${aula.id}`}>
          <div className="rg-sim-room-heading"><span className="rg-eyebrow">Explora este salón</span><select value={seleccionado} aria-label="Salón seleccionado" onChange={(e) => seleccionar(e.target.value)}>{escenario.salones.map((s) => <option key={s.id} value={s.id}>Salón {s.id}</option>)}</select></div>
          <div className="rg-sim-reading"><span>PM2.5 interior del modelo</span><strong>{aula.conexion ? Math.round(aula.dentro) : "—"}<small>µg/m³</small></strong><span className={`rg-sim-status is-${estado.color}`}>{estado.nombre} · simulado</span></div>
          <label className="rg-sim-toggle"><span><strong>Filtro del escenario</strong><small>CADR supuesto: {SUPUESTOS.cadr} m³/h</small></span><input type="checkbox" checked={aula.filtro} onChange={(e) => cambiarAula({ filtro: e.target.checked })} aria-label={`Filtro del salón ${aula.id}`} /></label>
          <label className="rg-sim-toggle"><span><strong>Ventanas abiertas</strong><small>Prueba cómo cambia el intercambio de aire</small></span><input type="checkbox" checked={aula.ventanas} onChange={(e) => cambiarAula({ ventanas: e.target.checked })} aria-label={`Ventanas del salón ${aula.id}`} /></label>
          <label className="rg-sim-toggle"><span><strong>Dispositivo conectado</strong><small>Ensaya una desconexión de ESP32/OLED</small></span><input type="checkbox" checked={aula.conexion} onChange={(e) => cambiarAula({ conexion: e.target.checked })} aria-label={`Conexión del salón ${aula.id}`} /></label>
          <label className="rg-sim-range">Ocupación ficticia <strong>{aula.ocupacion} personas</strong><input type="range" min="0" max="40" value={aula.ocupacion} onChange={(e) => cambiarAula({ ocupacion: Number(e.target.value) })} aria-label={`Ocupación del salón ${aula.id}`} /></label>
          <p className="rg-sim-room-note">{!aula.conexion ? "Sin conexión: el dispositivo indica SIN DATOS. El modelo sigue calculando para mostrar la diferencia entre un ambiente y la información disponible." : aula.filtro ? "El modelo ensaya filtración. En nuestro montaje físico, el MQ-135 no mide PM2.5." : "Este salón no tiene un filtro activo en el escenario. Puedes liberar uno en otro salón o cambiar el inventario."}</p>
        </aside>
      </div>
      <div className="rg-sim-feedback" role="status">{aviso}</div>
      <section className="rg-sim-decision" aria-labelledby="decision-titulo">
        <div className="rg-sim-controls">
          <h2 id="decision-titulo">¿Y si cambias la decisión?</h2>
          <p>Ensaya un reparto de recursos limitado. La comparación es contra el mismo escenario sin filtros.</p>
          <label className="rg-sim-range">PM2.5 exterior del escenario <strong>{escenario.fuera} µg/m³</strong><input type="range" min="0" max="180" step="1" value={escenario.fuera} onChange={(e) => setEscenario({ ...escenario, fuera: Number(e.target.value) })} /></label>
          <div className="rg-sim-presets">{PRESETS.map((p) => <button key={p.nombre} className="rg-pill rg-pill--blue" onClick={() => reiniciar(p.fuera)}>{p.nombre}</button>)}</div>
          <label className="rg-sim-range">Inventario hipotético <strong>{escenario.presupuesto} filtros</strong><input type="range" min="0" max="6" value={escenario.presupuesto} onChange={(e) => { setEscenario(cambiarPresupuesto(escenario, Number(e.target.value))); setAviso(""); }} /></label>
          <button className="rg-pill rg-pill--primary" onClick={() => { setEscenario(distribuirFiltros(escenario)); setAviso("Reparto ensayado: prioriza la reducción de exposición del modelo en los próximos 60 minutos, ponderada por ocupación. No es una recomendación médica."); }}>Ensayar reparto de filtros ↗</button>
          <p className="rg-sim-small">El algoritmo usa ocupación y supuestos físicos; no usa diagnósticos ni datos personales. Cambia ajustes y compara.</p>
        </div>
        <div className="rg-sim-results">
          <div className="rg-sim-kpis"><div><span>Menos exposición en el ensayo</span><strong>{Math.round(total.reduccion)}<small>%</small></strong><span>Acumulada · ponderada por ocupación</span></div><div><span>Filtros activos / disponibles</span><strong>{total.filtros}<small> / {escenario.presupuesto}</small></strong><span>{total.personas} personas ficticias</span></div></div>
          <Tendencia historial={escenario.historial} salon={seleccionado} />
          <p className="rg-sim-small">El porcentaje compara integrales de concentración × tiempo × ocupación, no probabilidad de enfermedad. Cambiar ajustes afecta el futuro del ensayo; reiniciar borra su historia.</p>
        </div>
      </section>
      <details className="rg-sim-method"><summary>Cómo funciona el modelo y qué no demuestra</summary><p>Mezcla perfecta en un volumen supuesto de {SUPUESTOS.volumen} m³. Recambio: {SUPUESTOS.recambioCerrado} h⁻¹ con ventanas cerradas y {SUPUESTOS.recambioAbierto} h⁻¹ abiertas. Filtración idealizada: {SUPUESTOS.cadr} m³/h por filtro. No se modelan fuentes interiores, deposición, clima, CO₂, contagios ni interacción entre salones.</p><p>Ecuación: dC/dt = λ·Cexterior − (λ + CADR/V)·C. Se integra de forma exponencial exacta. Abrir ventanas puede elevar o reducir PM2.5 según la diferencia dentro/fuera; esta demo no emite instrucciones reales de ventilación o seguridad.</p><p>Los cortes del semáforo escolar se aplican aquí al valor instantáneo del modelo: es una simplificación, no el cálculo completo de un índice oficial. Los colores sirven para ensayar la interfaz. El mapa no está conectado a sensores y no escribe lecturas en la API. La lectura del MQ del prototipo no calibra este modelo.</p><a href="#/evidencia">Revisar las fuentes y la evidencia real del proyecto</a></details>
    </main>
  );
}
