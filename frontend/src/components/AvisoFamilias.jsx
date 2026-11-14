import { useEffect, useRef, useState } from "react";
import { HORA_PREDETERMINADA, MAX_CARACTERES, mensajePredeterminado } from "../data/avisos.js";
// import { API_URL } from "../data/demo.js"; // <- descomentar al conectar la API

// Preferencias de la demo guardadas en este navegador (si el navegador lo permite).
const leer = (clave, defecto) => {
  try { return localStorage.getItem(clave) ?? defecto; } catch { return defecto; }
};
const guardar = (clave, valor) => {
  try { localStorage.setItem(clave, valor); } catch { /* sin almacenamiento: no pasa nada */ }
};

// Tarjeta pequeña con el resumen del aviso. Al hacer clic se abre una ventana modal para
// editar el mensaje, enviarlo en el momento y cambiar la hora del envío diario.
// `datos` = { escuela, semaforo, pm25, familias } (sale del pronóstico de mañana).
export default function AvisoFamilias({ datos }) {
  // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
  // Hoy el texto y la hora viven en el navegador. Con la API: leerlos de GET /alertas/programacion.
  const [mensaje, setMensaje] = useState(() => leer("rg-aviso-mensaje", mensajePredeterminado(datos)));
  const [hora, setHora] = useState(() => leer("rg-aviso-hora", HORA_PREDETERMINADA));
  const [horaGuardada, setHoraGuardada] = useState(hora);

  // Estado de la interfaz (no es mock)
  const [envio, setEnvio] = useState("listo"); // "listo" | "enviando" | "enviado"
  const [enviadoA, setEnviadoA] = useState(null);
  const dialogo = useRef(null);
  const timer = useRef();
  useEffect(() => () => clearTimeout(timer.current), []);

  const abrir = () => dialogo.current?.showModal();
  const cerrar = () => dialogo.current?.close();
  // Clic en el fondo oscuro (fuera de la ventana) también cierra.
  const clicFondo = (e) => { if (e.target === dialogo.current) cerrar(); };

  const editar = (texto) => {
    setMensaje(texto);
    guardar("rg-aviso-mensaje", texto);
    if (envio === "enviado") setEnvio("listo");
  };

  const usarPredeterminado = () => editar(mensajePredeterminado(datos));

  const guardarHora = () => {
    if (!hora) return;
    setHoraGuardada(hora);
    guardar("rg-aviso-hora", hora);
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // fetch(`${API_URL}/alertas/programacion`, { method: "PUT", headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ hora, mensaje }) });
  };

  const enviarAhora = () => {
    setEnvio("enviando");
    // TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
    // Reemplazar el setTimeout por:
    // fetch(`${API_URL}/alertas/enviar`, { method: "POST", headers: { "Content-Type": "application/json" },
    //   body: JSON.stringify({ mensaje }) }).then(() => { setEnvio("enviado"); setEnviadoA(hora actual); });
    timer.current = setTimeout(() => {
      setEnvio("enviado");
      setEnviadoA(new Date().toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" }));
    }, 1200);
  };

  const vacio = mensaje.trim() === "";

  return (
    <>
      <button type="button" className="rg-panel rg-surface-sky rg-aviso-mini" onClick={abrir} aria-haspopup="dialog">
        <span className="rg-panel__title">Aviso a familias</span>
        <span className="rg-aviso-mini__prev">{vacio ? "Sin mensaje" : mensaje.replace(/\s+/g, " ")}</span>
        <span className="rg-muted">
          Programado: todos los días a las {horaGuardada}
          {envio === "enviado" && ` · último envío ${enviadoA}`}
        </span>
        <span className="rg-aviso-mini__cta">Editar, programar o enviar ahora →</span>
      </button>

      <dialog ref={dialogo} className="rg-modal" aria-labelledby="rg-aviso-titulo" onClick={clicFondo}>
        <div className="rg-modal__body rg-aviso">
          <div className="rg-modal__head">
            <h2 id="rg-aviso-titulo">Aviso a familias</h2>
            <button type="button" className="rg-modal__close" onClick={cerrar} aria-label="Cerrar">×</button>
          </div>

          <div className="rg-field">
            <div className="rg-field__head">
              <label htmlFor="rg-aviso-texto">Mensaje</label>
              <button type="button" className="rg-pill rg-pill--blue rg-tap" onClick={usarPredeterminado}>
                Usar mensaje predeterminado
              </button>
            </div>
            <textarea id="rg-aviso-texto" className="rg-textarea" rows={10} maxLength={MAX_CARACTERES}
              value={mensaje} onChange={(e) => editar(e.target.value)} />
            <p className="rg-muted rg-field__foot">
              <span>El predeterminado se arma con el semáforo y el PM2.5 de mañana. No escribas nombres de alumnos.</span>
              <span>{mensaje.length}/{MAX_CARACTERES}</span>
            </p>
          </div>

          <div className="rg-field">
            <label htmlFor="rg-aviso-hora">Envío programado</label>
            <div className="rg-field__row">
              <span>Todos los días a las</span>
              <input id="rg-aviso-hora" type="time" className="rg-time" value={hora}
                onChange={(e) => setHora(e.target.value)} />
              <button type="button" className="rg-pill rg-pill--blue rg-tap" onClick={guardarHora}
                disabled={!hora || hora === horaGuardada}>
                Guardar hora
              </button>
            </div>
            <p className="rg-muted" aria-live="polite">Programado: todos los días a las {horaGuardada} (simulado).</p>
          </div>

          <button type="button" className="rg-pill rg-pill--primary rg-full rg-tap"
            onClick={enviarAhora} disabled={vacio || envio === "enviando"}>
            {envio === "enviando" ? "Enviando…" : "Enviar ahora"}
          </button>
          <div aria-live="polite">
            {envio === "enviado" && (
              <p className="rg-sent">Aviso enviado ahora ({enviadoA}) a {datos.familias} familias por Telegram (simulado).</p>
            )}
          </div>
        </div>
      </dialog>
    </>
  );
}
