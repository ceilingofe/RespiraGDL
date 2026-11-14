// DATOS SIMULADOS para la demo. Cuando la API esté arriba se reemplazan
// por GET /lecturas, /salones/{id}/proteccion, /alertas/hoy, /escuelas y /plan-asma/*.
// Ver src/lib/api.js: cada pantalla pide a la API y, si no responde, usa estos datos.

export const NORMA_PM25 = 45; // µg/m³ promedio 24 h, NOM-025-SSA1-2021

// Niveles del semáforo (puntos de corte de PM2.5 en µg/m³, simplificados para la demo).
// Los mismos cortes viven en backend/app/services/semaforo.py: si cambian, cambien ambos.
export const NIVELES = [
  { id: "good", nombre: "Buena", color: "verde", max: 15, consejo: "Recreo normal al aire libre." },
  { id: "ok", nombre: "Aceptable", color: "verde", max: 33, consejo: "Recreo normal; vigilar a niños con asma." },
  { id: "bad", nombre: "Mala", color: "amarillo", max: 79, consejo: "Recreo adentro para niños con asma; filtro encendido." },
  { id: "vbad", nombre: "Muy mala", color: "rojo", max: 130, consejo: "Recreo adentro para todos; ventanas cerradas y filtro al máximo." },
  { id: "ext", nombre: "Extremadamente mala", color: "rojo", max: Infinity, consejo: "Seguir indicaciones de Protección Civil." },
];

export function nivel(pm) {
  return NIVELES.find((n) => pm <= n.max);
}

// Por debajo de este % de protección el tablero avisa que algo falla en el salón.
export const PROTECCION_MINIMA = 40;

export const proteccion = (fuera, dentro) => Math.round((1 - dentro / fuera) * 100);

export const ESCUELA = {
  id: "miravalle",
  nombre: "Primaria de demostración · Miravalle",
  estacion: "SIMAJ Miravalle",
  hora: "10:00",
};

// Una sola lectura de fuera para toda la escuela (sensor exterior o estación del SIMAJ).
const HORAS = ["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00"];
const FUERA = [48, 57, 66, 62, 64, 60, 55, 52];

// Serie de dentro por salón. 4B y 6B no tienen filtro: dentro casi igual que fuera.
const DENTRO = {
  "1A": [40, 30, 24, 21, 20, 19, 18, 17],
  "2A": [41, 33, 27, 24, 22, 21, 20, 19],
  "3A": [40, 31, 24, 19, 19, 18, 18, 17],
  "4B": [44, 51, 58, 55, 57, 54, 50, 47],
  "5A": [41, 32, 26, 23, 22, 21, 20, 19],
  "6B": [45, 53, 61, 58, 60, 56, 51, 49],
};

// pm25 fuera y dentro a las 10:00; % de protección = 1 − dentro/fuera.
// "asma" es solo el número de alumnos del grupo: nunca nombres.
const GRUPOS = [
  { id: "1A", asma: 3, filtro: true, maestra: "Mtra. de 1°A" },
  { id: "2A", asma: 2, filtro: true, maestra: "Mtro. de 2°A" },
  { id: "3A", asma: 4, filtro: true, maestra: "Mtra. de 3°A" },
  { id: "4B", asma: 1, filtro: false, maestra: "Mtra. de 4°B" },
  { id: "5A", asma: 2, filtro: true, maestra: "Mtro. de 5°A" },
  { id: "6B", asma: 3, filtro: false, maestra: "Mtra. de 6°B" },
];
const AHORA = HORAS.indexOf(ESCUELA.hora);

export const SALONES = GRUPOS.map((g) => {
  const fuera = FUERA[AHORA];
  const dentro = DENTRO[g.id][AHORA];
  return { ...g, fuera, dentro, proteccion: proteccion(fuera, dentro) };
});

export const SERIES = Object.fromEntries(
  Object.entries(DENTRO).map(([id, d]) => [id, HORAS.map((h, i) => ({ h, fuera: FUERA[i], dentro: d[i] }))])
);
export const SERIE = SERIES["3A"]; // compatibilidad con código anterior

export const PRONOSTICO = [
  { dia: "Hoy", pm: 62 },
  { dia: "Mañana", pm: 71 },
  { dia: "Sábado", pm: 38 },
];

// Familias con hijos con asma suscritas al bot (no siempre es la suma de la columna asma:
// hay familias sin bot y hermanos en otros grupos).
export const FAMILIAS_BOT = 13;

export const AVISO_FAMILIAS =
  "Buenos días. Mañana se espera calidad del aire MALA en Miravalle (PM2.5 71). Si su hijo o hija tiene asma, revise que lleve su inhalador de rescate y su plan. El recreo será adentro. Si usa medicamento de control, no lo suspenda.";

// Indicadores del ciclo escolar (los tres del plan): días con recreo protegido,
// faltas por asma y crisis atendidas en la escuela. Antes = mismo periodo del ciclo pasado.
export const INDICADORES = {
  periodo: "Sep a nov 2026",
  diasFueraNorma: 23,
  diasRecreoProtegido: 21,
  faltasAsma: { antes: 38, ahora: 24 },
  crisisEscuela: { antes: 9, ahora: 4 },
  avisosEnviados: 19,
  respuestasSintomas: 41,
};

// Semanas del periodo: días fuera de norma y faltas por asma (simulado).
export const SEMANAS = [
  { s: "S1", fuera: 1, faltas: 4 },
  { s: "S2", fuera: 2, faltas: 3 },
  { s: "S3", fuera: 0, faltas: 1 },
  { s: "S4", fuera: 3, faltas: 3 },
  { s: "S5", fuera: 2, faltas: 2 },
  { s: "S6", fuera: 4, faltas: 3 },
  { s: "S7", fuera: 3, faltas: 2 },
  { s: "S8", fuera: 2, faltas: 2 },
  { s: "S9", fuera: 1, faltas: 1 },
  { s: "S10", fuera: 3, faltas: 2 },
  { s: "S11", fuera: 2, faltas: 1 },
];

// Registro anónimo de crisis atendidas: sin nombre, solo grupo, hora y si se avisó a la familia.
export const INCIDENTES = [
  { id: 1, fecha: "12 nov", hora: "10:42", salon: "3A", avisoFamilia: true, llamada911: false },
  { id: 2, fecha: "6 nov", hora: "12:15", salon: "6B", avisoFamilia: true, llamada911: false },
  { id: 3, fecha: "28 oct", hora: "9:30", salon: "4B", avisoFamilia: true, llamada911: false },
  { id: 4, fecha: "15 oct", hora: "11:05", salon: "1A", avisoFamilia: true, llamada911: false },
];

// Red de escuelas piloto para la vista de autoridades (SEJ / municipio).
export const ESCUELAS = [
  {
    id: "miravalle", nombre: "Primaria Miravalle", municipio: "Guadalajara", estacion: "SIMAJ Miravalle",
    pmHoy: 62, pmManana: 71, salones: 6, conFiltro: 4, proteccion: 65, asma: 15, faltas: { antes: 38, ahora: 24 }, recreo: 21, fueraNorma: 23,
  },
  {
    id: "las-pintas", nombre: "Primaria Las Pintas", municipio: "Tlaquepaque", estacion: "SIMAJ Las Pintas",
    pmHoy: 74, pmManana: 82, salones: 8, conFiltro: 3, proteccion: 58, asma: 19, faltas: { antes: 44, ahora: 35 }, recreo: 17, fueraNorma: 29,
  },
  {
    id: "santa-fe", nombre: "Primaria Santa Fe", municipio: "Tlajomulco", estacion: "SIMAJ Santa Fe",
    pmHoy: 41, pmManana: 49, salones: 6, conFiltro: 6, proteccion: 71, asma: 11, faltas: { antes: 21, ahora: 13 }, recreo: 14, fueraNorma: 15,
  },
];
