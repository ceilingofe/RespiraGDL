// =====================================================================
// DATOS SIMULADOS PARA LA DEMO
// El tablero y la vista de la maestra ya piden sus datos a la API (src/data/useDatos.js).
// Los bloques MOCK_* de abajo quedan como RESPALDO: se muestran cuando no hay API
// (p. ej. en GitHub Pages) y la pantalla lo dice. Los "TODO: CONECTAR A LA API" que siguen
// marcan qué ruta reemplaza a cada bloque.
// =====================================================================

// URL base de la API. Se configura con VITE_API_URL en frontend/.env.local
export const API_URL = import.meta.env?.VITE_API_URL || "http://localhost:8000";

export const NORMA_PM25 = 25; // µg/m³ promedio 24 h, NOM-025-SSA1-2021 (etapa vigente en 2026)

//
export const SEMAFORO = {
  verde: { id: "good", nombre: "Verde" },
  amarillo: { id: "ok", nombre: "Amarillo" },
  rojo: { id: "vbad", nombre: "Rojo" },
};

// Nivel de PM2.5 (µg/m³) -> clase del semáforo de tokens.css y palabra.
// Esto NO es mock, se queda. Cortes de PM2.5 de la NOM-172-SEMARNAT-2023 (Índice AIRE y SALUD,
// vigentes desde enero de 2026), iguales a backend/app/core/semaforo.py: si cambian, cambien ambos.
const NIVELES_PM25 = [
  { max: 15, id: "good", nombre: "Buena" },
  { max: 25, id: "ok", nombre: "Aceptable" },
  { max: 79, id: "bad", nombre: "Mala" },
  { max: 130, id: "vbad", nombre: "Muy mala" },
  { max: Infinity, id: "ext", nombre: "Extremadamente mala" },
];
export const nivelPm25 = (pm) => NIVELES_PM25.find((n) => pm <= n.max);

// Por debajo de este % la barra de protección se pinta ámbar en vez de verd
export const PROTECCION_BUENA = 50;

// Por debajo de este % de protección el tablero muestra una alerta del salón
export const PROTECCION_MINIMA = 40;

// Calcula % de protección = 1 − dentro/fuera. Si la API ya lo manda, no se usa
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
  pm25Hoy: 62, // PM2.5 fuera (µg/m³) del sensor exterior; el semáforo siempre lleva número
  actualizado: "10:00",
  // Texto fijo de la demo. Con la API: usar la hora del servidor o new Date().
  momento: "jueves 13:10",
};
// --- FIN MOCK ESCUELA ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /salones
// Forma esperada por fila: { id, grupo, fuera, dentro, proteccion, asma, filtro }
// "asma" es solo un número: nunca nombres ni datos de alumnos.
// Mismos salones que backend/scripts/cargar_demo.py (los usan el tablero y Aula Limpia):
// 1A, 2A, 3A, 4B, 5A, 6B; 4B y 6B todavía no tienen filtro.
// ---------------------------------------------------------------------
export const MOCK_SALONES = [
  { id: "1A", grupo: "1° A", fuera: 62, dentro: 21, asma: 3, filtro: true },
  { id: "2A", grupo: "2° A", fuera: 62, dentro: 24, asma: 2, filtro: true },
  { id: "3A", grupo: "3° A", fuera: 62, dentro: 19, asma: 4, filtro: true },
  { id: "4B", grupo: "4° B", fuera: 62, dentro: 55, asma: 1, filtro: false },
  { id: "5A", grupo: "5° A", fuera: 62, dentro: 23, asma: 2, filtro: true },
  { id: "6B", grupo: "6° B", fuera: 62, dentro: 58, asma: 3, filtro: false },
].map((s) => ({ ...s, proteccion: proteccion(s.fuera, s.dentro) }));
// --- FIN MOCK SALONES ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint: GET /lecturas/serie?salon_id={id}   (un llamado por salón seleccionado)
// Forma esperada: [{ h: "7:00", fuera: 41, dentro: 35 }, ...] de 7:00 a 16:00
// "fuera" es el mismo sensor exterior para toda la escuela; "dentro" es el nodo de cada salón.
// A las 10:00 (índice 3) los valores coinciden con la tabla de MOCK_SALONES.
// ---------------------------------------------------------------------
const MOCK_HORAS = ["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"];
const MOCK_FUERA = [44, 53, 59, 62, 66, 64, 58, 53, 48, 46];
const MOCK_DENTRO_POR_SALON = {
  "1A": [35, 28, 23, 21, 20, 20, 19, 18, 18, 17],
  "2A": [37, 30, 26, 24, 23, 22, 21, 20, 19, 19],
  "3A": [34, 27, 22, 19, 18, 18, 17, 16, 16, 15],
  "4B": [40, 48, 53, 55, 59, 58, 52, 48, 43, 41], // sin filtro: dentro sigue casi igual que fuera
  "5A": [36, 29, 25, 23, 22, 21, 20, 19, 19, 18],
  "6B": [42, 50, 56, 58, 62, 60, 55, 50, 45, 43], // sin filtro
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
  pm25: 95,
  recomendacion: "Recreo y educación física adentro",
  familiasAviso: 21,
};
// --- FIN MOCK PRONÓSTICO ---

// ---------------------------------------------------------------------
// TODO: CONECTAR A LA API - REEMPLAZAR MOCK DATA AQUÍ
// Endpoint esperado: GET /salones/3A/hoy  (vista de la maestra)
// ---------------------------------------------------------------------
export const MOCK_MAESTRA = {
  titulo: "Maestra 3° A",
  salonId: "3A",
  semaforo: "amarillo",
  pm25: 62, // PM2.5 fuera (µg/m³), el mismo del tablero; el semáforo siempre lleva número
  momento: "jueves 13:10", // texto fijo de la demo; con la API usar la hora real
  conAsma: 4,
  tareas: [
    { id: "recreo", texto: "Recreo adentro", hecho: false },
    { id: "filtro", texto: "Filtro encendido y puerta cerrada", hecho: false },
    { id: "inhalador", texto: "Preguntar quién trae inhalador", hecho: false },
  ],
};
// --- FIN MOCK MAESTRA ---
