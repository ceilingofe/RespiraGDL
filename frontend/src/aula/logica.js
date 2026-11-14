// Aula Limpia · lógica pura (sin React) para calcular protección, semáforo y recomendaciones.
// Respira GDL orienta y recuerda; no es una herramienta de diagnóstico.

export const NORMA_PM25 = 45; // µg/m³ promedio 24 h, NOM-025-SSA1-2021
export const PROTECCION_MINIMA = 40; // % por debajo del cual el salón pide revisión
export const DIAS_CAMBIO_FILTRO = 90; // MERV-13 en salón: cambio aprox. cada 3 meses

// Cortes de PM2.5 (µg/m³) iguales a los del tablero; confirmar con Juan.
export const NIVELES = [
  { max: 25, id: "good", nombre: "Buena" },
  { max: 45, id: "ok", nombre: "Aceptable" },
  { max: 79, id: "bad", nombre: "Mala" },
  { max: 147, id: "vbad", nombre: "Muy mala" },
  { max: Infinity, id: "ext", nombre: "Extremadamente mala" },
];

export const nivel = (pm) => NIVELES.find((n) => pm <= n.max);
const rango = (pm) => NIVELES.indexOf(nivel(pm));

// % de PM2.5 de fuera que no entra al salón = 1 − dentro/fuera
export function proteccion(fuera, dentro) {
  if (!fuera || fuera <= 0) return null;
  return Math.round((1 - dentro / fuera) * 100);
}

export function diasDesde(fechaIso, hoy = new Date()) {
  if (!fechaIso) return null;
  return Math.floor((hoy - new Date(fechaIso)) / 86400000);
}

// Devuelve recomendaciones ordenadas por prioridad: "alta" | "media" | "ok"
export function recomendaciones({ fuera, dentro, filtro, filtroCambio, asma = 0 }, hoy = new Date()) {
  const r = [];
  const p = proteccion(fuera, dentro);
  const nf = rango(fuera);
  const nd = rango(dentro);

  if (!filtro) {
    r.push({ prioridad: "alta", texto: "Enciende el filtro y cierra la puerta.", porque: "Sin filtro, casi todo el PM2.5 de fuera entra al salón." });
  } else if (p !== null && p < PROTECCION_MINIMA && nf >= 1) {
    r.push({ prioridad: "alta", texto: "Protección baja: cierra puerta y ventanas y revisa que nada tape el filtro.", porque: `Solo se detiene el ${Math.max(p, 0)} % del PM2.5 de fuera.` });
  }

  if (dentro > NORMA_PM25) {
    r.push({ prioridad: "alta", texto: "Dentro del salón se rebasa la norma. Evita actividad física intensa adentro.", porque: `PM2.5 dentro ${dentro} µg/m³; la norma es ${NORMA_PM25}.` });
  }

  if (nf >= 3) {
    r.push({ prioridad: "alta", texto: "Recreo adentro para todo el grupo.", porque: `La calidad del aire de fuera es ${nivel(fuera).nombre.toLowerCase()}.` });
  } else if (nf === 2) {
    r.push({ prioridad: "media", texto: asma > 0 ? `Recreo adentro para ${asma === 1 ? "el alumno" : `los ${asma} alumnos`} con asma.` : "Recreo corto o adentro si hay alumnos con asma.", porque: "La calidad del aire de fuera es mala." });
  }

  if (asma > 0 && nf >= 2) {
    r.push({ prioridad: "media", texto: "Recuerda al grupo traer su inhalador en la mochila.", porque: "Días de aire malo aumentan el riesgo de crisis." });
  }

  const dias = diasDesde(filtroCambio, hoy);
  if (dias !== null && dias >= DIAS_CAMBIO_FILTRO) {
    r.push({ prioridad: "media", texto: "Toca cambiar los 4 filtros MERV-13.", porque: `Llevan ${dias} días; se cambian cada ${DIAS_CAMBIO_FILTRO}.` });
  }

  if (nf === 0 && nd <= 1) {
    r.push({ prioridad: "ok", texto: "Aire de fuera bueno: abre ventanas 10 minutos entre clases para ventilar.", porque: "Ventilar baja el CO₂ y el calor del salón." });
  }
  if (!r.some((x) => x.prioridad === "alta") && filtro && p !== null && p >= PROTECCION_MINIMA) {
    r.push({ prioridad: "ok", texto: "El filtro está funcionando. Mantén la puerta cerrada.", porque: `Se detiene el ${p} % del PM2.5 de fuera.` });
  }

  const orden = { alta: 0, media: 1, ok: 2 };
  return r.sort((a, b) => orden[a.prioridad] - orden[b.prioridad]);
}

// --- Simulación para la demo ---------------------------------------------------
// Fuera oscila suave; dentro se acerca al valor de equilibrio (rápido con filtro).
export function paso(estado, t, salon) {
  const fuera = Math.max(5, Math.round(salon.fuera + 6 * Math.sin(t / 7) + (Math.random() - 0.5) * 4));
  const eficiencia = estado.filtro ? salon.eficiencia : 0.08; // fuga natural del salón
  const meta = fuera * (1 - eficiencia);
  const velocidad = estado.filtro ? 0.22 : 0.15;
  const dentro = Math.max(2, Math.round(estado.dentro + (meta - estado.dentro) * velocidad + (Math.random() - 0.5) * 2));
  return { ...estado, fuera, dentro };
}
