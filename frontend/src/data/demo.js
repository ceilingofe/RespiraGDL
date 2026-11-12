// DATOS SIMULADOS para la demo. Cuando la API esté arriba se reemplazan
// por GET /lecturas, /salones/{id}/proteccion y /alertas/hoy.

export const NORMA_PM25 = 45; // µg/m³ promedio 24 h, NOM-025-SSA1-2021

// Niveles del semáforo (puntos de corte de PM2.5 en µg/m³, simplificados para la demo)
export const NIVELES = [
  { id: "good", nombre: "Buena", max: 15, consejo: "Recreo normal al aire libre." },
  { id: "ok", nombre: "Aceptable", max: 33, consejo: "Recreo normal; vigilar a niños con asma." },
  { id: "bad", nombre: "Mala", max: 79, consejo: "Recreo adentro para niños con asma; filtro encendido." },
  { id: "vbad", nombre: "Muy mala", max: 130, consejo: "Recreo adentro para todos; ventanas cerradas y filtro al máximo." },
  { id: "ext", nombre: "Extremadamente mala", max: Infinity, consejo: "Seguir indicaciones de Protección Civil." },
];

export function nivel(pm) {
  return NIVELES.find((n) => pm <= n.max);
}

export const ESCUELA = {
  nombre: "Primaria de demostración · Miravalle",
  estacion: "SIMAJ Miravalle",
};

// pm25 fuera y dentro, % de protección = 1 − dentro/fuera
export const SALONES = [
  { id: "1A", fuera: 62, dentro: 21, asma: 3, filtro: true },
  { id: "2A", fuera: 62, dentro: 24, asma: 2, filtro: true },
  { id: "3A", fuera: 62, dentro: 19, asma: 4, filtro: true },
  { id: "4B", fuera: 62, dentro: 55, asma: 1, filtro: false },
  { id: "5A", fuera: 62, dentro: 23, asma: 2, filtro: true },
  { id: "6B", fuera: 62, dentro: 58, asma: 3, filtro: false },
].map((s) => ({ ...s, proteccion: Math.round((1 - s.dentro / s.fuera) * 100) }));

// Serie de un día (7:00 a 14:00) en el salón 3A
const horas = ["7:00", "8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00"];
const fuera = [48, 57, 66, 71, 64, 60, 55, 52];
const dentro = [40, 31, 24, 21, 19, 18, 18, 17];
export const SERIE = horas.map((h, i) => ({ h, fuera: fuera[i], dentro: dentro[i] }));

export const PRONOSTICO = [
  { dia: "Hoy", pm: 62 },
  { dia: "Mañana", pm: 71 },
  { dia: "Sábado", pm: 38 },
];

export const AVISO_FAMILIAS =
  "Buenos días. Mañana se espera calidad del aire MALA en Miravalle. Si su hijo o hija tiene asma, revise que lleve su inhalador y su plan. El recreo será adentro.";
