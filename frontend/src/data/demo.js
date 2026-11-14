// =====================================================================
// DATOS SIMULADOS PARA LA DEMO
// Todo lo que lleva "TODO: CONECTAR A LA API" se borra cuando la API esté arriba.
// Cada página ya trae el useEffect con el fetch comentado: descoméntenlo y
// borren el bloque mock correspondiente de este archivo.
// =====================================================================

// URL base de la API. Se configura con VITE_API_URL en frontend/.env.local
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const NORMA_PM25 = 45; // µg/m³ promedio 24 h, NOM-025-SSA1-2021

// Colores del semáforo que manda la API ("verde" | "amarillo" | "rojo")
// mapeados a las clases de tokens.css. Esto NO es mock, se queda.
export const SEMAFORO = {
  verde: { id: "good", nombre: "Verde" },
  amarillo: { id: "ok", nombre: "Amarillo" },
  rojo: { id: "vbad", nombre: "Rojo" },
};

// Nivel de PM2.5 (µg/m³) -> clase del semáforo de tokens.css y palabra.
// Esto NO es mock, se queda. Cortes aproximados al índice AIRE y SALUD; confirmar con Juan.
const NIVELES_PM25 = [
  { max: 25, id: "good", nombre: "Buena" },
  { max: 45, id: "ok", nombre: "Aceptable" },
  { max: 79, id: "bad", nombre: "Mala" },
  { max: 147, id: "vbad", nombre: "Muy mala" },
  { max: Infinity, id: "ext", nombre: "Extremadamente mala" },
];
export const nivelPm25 = (pm) => NIVELES_PM25.find((n) => pm <= n.max);

// Por debajo de este % la barra de protección se pinta ámbar en vez de verde.
export const PROTECCION_BUENA = 50;

// Por debajo de este % de protección el tablero muestra una alerta del salón.
export const PROTECCION_MINIMA = 40;

// Calcula % de protección = 1 − dentro/fuera. Si la API ya lo manda, no se usa.
export const proteccion = (fuera, dentro) => Math.round((1 - dentro / fuera) * 100);

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /escuelas/{id}  (o el que defina backend)
// ---------------------------------------------------------------------
export const MOCK_ESCUELA = {
  nombre: "Esc. Prim. Miravalle T/M",
  nombreCorto: "Esc. Prim. Miravalle",
  estacion: "SIMAJ Miravalle",
  semaforoHoy: "amarillo",
  pm25Hoy: 58, // PM2.5 fuera (µg/m³) del sensor exterior; el semáforo siempre lleva número
  actualizado: "10:00",
  // Texto fijo de la demo. Con la API: usar la hora del servidor o new Date().
  momento: "jueves 13:10",
};
// --- FIN MOCK ESCUELA ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /salones
// Forma esperada por fila: { id, grupo, fuera, dentro, proteccion, asma }
// "asma" es solo un número: nunca nombres ni datos de alumnos.
// ---------------------------------------------------------------------
export const MOCK_SALONES = [
  { id: "1A", grupo: "1° A", fuera: 58, dentro: 19, asma: 4 },
  { id: "2B", grupo: "2° B", fuera: 58, dentro: 21, asma: 3 },
  { id: "3B", grupo: "3° B", fuera: 58, dentro: 20, asma: 5 },
  { id: "4A", grupo: "4° A", fuera: 58, dentro: 22, asma: 2 },
  { id: "5A", grupo: "5° A", fuera: 58, dentro: 41, asma: 3 },
  { id: "6B", grupo: "6° B", fuera: 58, dentro: 23, asma: 1 },
].map((s) => ({ ...s, proteccion: proteccion(s.fuera, s.dentro) }));
// --- FIN MOCK SALONES ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /lecturas?salon={id}&fecha=hoy   (un llamado por salón seleccionado)
// Forma esperada: [{ h: "7:00", fuera: 41, dentro: 35 }, ...] de 7:00 a 16:00
// "fuera" es el mismo sensor exterior para toda la escuela; "dentro" es el nodo de cada salón.
// A las 10:00 (índice 3) los valores coinciden con la tabla de MOCK_SALONES.
// ---------------------------------------------------------------------
const MOCK_HORAS = ["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];
const MOCK_FUERA = [41, 49, 55, 58, 62, 60, 54, 49, 45, 43];
const MOCK_DENTRO_POR_SALON = {
  "1A": [33, 26, 21, 19, 18, 18, 17, 16, 16, 15],
  "2B": [34, 27, 23, 21, 20, 20, 19, 18, 17, 17],
  "3B": [35, 28, 23, 20, 19, 19, 18, 17, 17, 16],
  "4A": [36, 29, 24, 22, 21, 21, 20, 19, 18, 18],
  "5A": [38, 40, 41, 41, 43, 42, 39, 36, 34, 33], // filtro apagado o puerta abierta: casi no protege
  "6B": [36, 30, 25, 23, 22, 21, 20, 19, 19, 18],
};
export const MOCK_LECTURAS = Object.fromEntries(
  Object.entries(MOCK_DENTRO_POR_SALON).map(([id, dentro]) => [
    id,
    MOCK_HORAS.map((h, i) => ({ h, fuera: MOCK_FUERA[i], dentro: dentro[i] })),
  ])
);
// --- FIN MOCK LECTURAS ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /pronostico/manana
// "familiasAviso" = familias suscritas al bot con hijos con asma (puede no ser la suma
// de la columna asma: hay alumnos con familias sin bot y hermanos en otros grupos).
// ---------------------------------------------------------------------
export const MOCK_PRONOSTICO = {
  dia: "Mañana",
  semaforo: "rojo",
  pm25: 71,
  recomendacion: "Recreo y educación física adentro",
  familiasAviso: 21,
};
// --- FIN MOCK PRONÓSTICO ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /salones/3B/hoy  (vista de la maestra)
// ---------------------------------------------------------------------
export const MOCK_MAESTRA = {
  titulo: "Maestra 3° B",
  salonId: "3B",
  semaforo: "amarillo",
  pm25: 58, // PM2.5 fuera (µg/m³), el mismo del tablero; el semáforo siempre lleva número
  momento: "jueves 13:10", // texto fijo de la demo; con la API usar la hora real
  conAsma: 5,
  tareas: [
    { id: "recreo", texto: "Recreo adentro", hecho: false },
    { id: "filtro", texto: "Filtro encendido y puerta cerrada", hecho: false },
  ],
};
// --- FIN MOCK MAESTRA ---
