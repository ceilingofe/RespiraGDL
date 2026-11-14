// Aula Limpia · datos de la demo y conexión a la API.
// DATOS SIMULADOS: se reemplazan solos cuando VITE_API_URL apunta a la API y responde.

export const API_URL = import.meta.env.VITE_API_URL || "";

export const ESCUELA_AULA = {
  nombre: "Primaria de demostración · Miravalle",
  estacion: "SIMAJ Miravalle",
};

// fuera/dentro en µg/m³; eficiencia = fracción que detiene el filtro casero (medida en la prueba)
export const SALONES_AULA = [
  { id: "1A", grupo: "1°A", fuera: 62, dentro: 21, eficiencia: 0.66, filtro: true, filtroCambio: "2026-10-02", asma: 3 },
  { id: "3A", grupo: "3°A", fuera: 62, dentro: 19, eficiencia: 0.7, filtro: true, filtroCambio: "2026-10-02", asma: 4 },
  { id: "4B", grupo: "4°B", fuera: 62, dentro: 55, eficiencia: 0.64, filtro: false, filtroCambio: "2026-07-20", asma: 1 },
  { id: "5A", grupo: "5°A", fuera: 62, dentro: 44, eficiencia: 0.32, filtro: true, filtroCambio: "2026-06-30", asma: 2 },
  { id: "6B", grupo: "6°B", fuera: 62, dentro: 58, eficiencia: 0.6, filtro: false, filtroCambio: "2026-10-02", asma: 3 },
];

// GET /salones/{id}/proteccion → { fuera, dentro, proteccion_pct }.
// Devuelve null si la API no está configurada o no trae lecturas (se usa la simulación).
export async function leerSalon(id) {
  if (!API_URL) return null;
  try {
    const r = await fetch(`${API_URL}/salones/${id}/proteccion`);
    if (!r.ok) return null;
    const d = await r.json();
    if (typeof d.fuera !== "number" || typeof d.dentro !== "number") return null;
    return { fuera: Math.round(d.fuera), dentro: Math.round(d.dentro) };
  } catch {
    return null;
  }
}
