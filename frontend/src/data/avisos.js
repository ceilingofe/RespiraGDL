// Mensaje predeterminado del aviso a familias según el semáforo y el nivel de PM2.5.
// Esto NO es mock: es la plantilla del texto. Los datos (escuela, semáforo, PM2.5) vienen de la API.
// Debe coincidir con mensaje_aviso() de bot/bot.py.
import { nivelPm25 } from "./demo.js";

const ICONO = { verde: "🟢", amarillo: "🟡", rojo: "🔴" };

const CONSEJO = {
  verde: "Recreo normal al aire libre.",
  amarillo: "Si su hijo o hija tiene asma, revise que lleve su inhalador y su plan de acción.",
  rojo: "El recreo y la educación física serán adentro. Revise que lleve su inhalador y su plan de acción.",
};

export const HORA_PREDETERMINADA = "07:00";
export const MAX_CARACTERES = 1000;

export function mensajePredeterminado({ escuela, semaforo, pm25 }) {
  const nivel = nivelPm25(pm25);
  return [
    `Aviso de Respira GDL · ${escuela}`,
    "",
    `${ICONO[semaforo] ?? ""} Pronóstico para mañana: ${semaforo.toUpperCase()}`,
    `PM2.5 esperado: ${pm25} µg/m³ (calidad del aire ${nivel.nombre.toLowerCase()})`,
    "",
    CONSEJO[semaforo] ?? "",
    "",
    "Si su hijo o hija tuvo tos, silbido en el pecho o le faltó el aire hoy, responda 1.",
    "Esto no es un diagnóstico; ante cualquier duda consulte a su médico.",
  ].join("\n");
}
