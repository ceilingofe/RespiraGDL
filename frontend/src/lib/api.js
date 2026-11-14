import { useEffect, useState } from "react";

// URL de la API. Se configura con VITE_API_URL (ej. http://localhost:8000) en frontend/.env.local.
// Sin variable, la app usa solo los datos simulados de src/data y lo dice en pantalla.
export const API_URL = import.meta.env.VITE_API_URL || "";

// Pide `path` a la API. Si no hay API o falla, devuelve `fallback` y marca simulado = true.
// `adapt` convierte la respuesta de la API a la forma que usa la pantalla; si regresa null, se queda la demo.
export function useApi(path, fallback, adapt = (x) => x) {
  const [state, setState] = useState({ data: fallback, simulado: true });
  useEffect(() => {
    if (!API_URL || !path) return;
    const ctrl = new AbortController();
    fetch(`${API_URL}${path}`, { signal: ctrl.signal })
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then((json) => {
        const data = adapt(json);
        if (data) setState({ data, simulado: false }); // forma inesperada: se queda la demo
      })
      .catch(() => {});
    return () => ctrl.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [path]);
  return state;
}

// Envía datos a la API sin bloquear la demo: si no hay API, no pasa nada.
export function post(path, body) {
  if (!API_URL) return Promise.resolve(null);
  return fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  })
    .then((r) => (r.ok ? r.json() : null))
    .catch(() => null);
}

export const horaActual = () =>
  new Date().toLocaleTimeString("es-MX", { hour: "numeric", minute: "2-digit" });

// Acepta un arreglo solo si cada fila trae las llaves que la pantalla necesita.
export const filas = (...llaves) => (json) =>
  Array.isArray(json) && json.length > 0 && json.every((f) => llaves.every((k) => f?.[k] !== undefined)) ? json : null;
