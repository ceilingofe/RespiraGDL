// Modelo educativo de mezcla perfecta. Supuestos, no mediciones ni recomendación clínica.
export const SUPUESTOS = Object.freeze({ volumen: 180, cadr: 400, recambioCerrado: 0.6, recambioAbierto: 3 });
const IDS = ["1A", "2A", "3A", "4B", "5A", "6B"];
const OCUPACION = [24, 30, 28, 32, 26, 30];

function validarNumero(valor, minimo, maximo, nombre) {
  if (!Number.isFinite(valor) || valor < minimo || valor > maximo) throw new Error(`${nombre} fuera de rango`);
}

function evolucion(concentracion, fuera, aula, filtro, minutos) {
  const recambio = aula.ventanas ? SUPUESTOS.recambioAbierto : SUPUESTOS.recambioCerrado;
  const perdida = recambio + (filtro ? SUPUESTOS.cadr / SUPUESTOS.volumen : 0);
  const k = perdida / 60;
  const equilibrio = recambio * fuera / perdida;
  const decaimiento = Math.exp(-k * minutos);
  return {
    final: equilibrio + (concentracion - equilibrio) * decaimiento,
    integral: equilibrio * minutos + (concentracion - equilibrio) * (-Math.expm1(-k * minutos)) / k,
  };
}

function punto(estado) {
  return { minuto: estado.minuto, fuera: estado.fuera,
    salones: Object.fromEntries(estado.salones.map((s) => [s.id, { dentro: s.dentro, sinFiltro: s.sinFiltro }])) };
}

export function crearEscenario({ fuera = 62 } = {}) {
  validarNumero(fuera, 0, 250, "Exterior");
  const estado = { minuto: 0, fuera, presupuesto: 4, salones: IDS.map((id, i) => ({
    id, ocupacion: OCUPACION[i], ventanas: i === 3 || i === 5, conexion: true,
    filtro: ![3, 5].includes(i), dentro: fuera, sinFiltro: fuera,
    exposicion: 0, exposicionBase: 0, dosis: 0, dosisBase: 0,
  })) };
  return { ...estado, historial: [punto(estado)] };
}

export function avanzar(estado, minutos = 1) {
  validarNumero(minutos, Number.EPSILON, 60, "Minutos");
  validarNumero(estado.fuera, 0, 250, "Exterior");
  const dt = Math.min(minutos, Math.max(0, 360 - estado.minuto));
  if (!dt) return estado;
  const salones = estado.salones.map((s) => {
    const actual = evolucion(s.dentro, estado.fuera, s, s.filtro, dt);
    const base = evolucion(s.sinFiltro, estado.fuera, s, false, dt);
    return { ...s, dentro: actual.final, sinFiltro: base.final,
      exposicion: s.exposicion + actual.integral, exposicionBase: s.exposicionBase + base.integral,
      dosis: s.dosis + actual.integral * s.ocupacion, dosisBase: s.dosisBase + base.integral * s.ocupacion };
  });
  const siguiente = { ...estado, minuto: estado.minuto + dt, salones };
  return { ...siguiente, historial: [...estado.historial, punto(siguiente)].slice(-361) };
}

export function configurarSalon(estado, id, cambios) {
  const aula = estado.salones.find((s) => s.id === id);
  if (!aula) throw new Error("Salón desconocido");
  const permitidas = ["filtro", "ventanas", "ocupacion", "conexion"];
  if (Object.keys(cambios).some((k) => !permitidas.includes(k))) throw new Error("Cambio desconocido");
  for (const k of ["filtro", "ventanas", "conexion"]) {
    if (k in cambios && typeof cambios[k] !== "boolean") throw new Error("Estado inválido");
  }
  if ("ocupacion" in cambios) {
    validarNumero(cambios.ocupacion, 0, 40, "Ocupación");
    if (!Number.isInteger(cambios.ocupacion)) throw new Error("Ocupación debe ser entera");
  }
  if (cambios.filtro && !aula.filtro && estado.salones.filter((s) => s.filtro).length >= estado.presupuesto) {
    throw new Error("No quedan filtros en el presupuesto. Apaga otro o cambia el inventario.");
  }
  return { ...estado, salones: estado.salones.map((s) => s.id === id ? { ...s, ...cambios } : s) };
}

export function cambiarPresupuesto(estado, cantidad) {
  validarNumero(cantidad, 0, 6, "Presupuesto");
  if (!Number.isInteger(cantidad)) throw new Error("Presupuesto debe ser entero");
  let usados = 0;
  return { ...estado, presupuesto: cantidad, salones: estado.salones.map((s) => ({ ...s,
    filtro: s.filtro && ++usados <= cantidad })) };
}

export function distribuirFiltros(estado) {
  const prioridad = estado.salones.map((s) => {
    const sin = evolucion(s.dentro, estado.fuera, s, false, 60).integral;
    const con = evolucion(s.dentro, estado.fuera, s, true, 60).integral;
    return { id: s.id, ganancia: Math.max(0, sin - con) * s.ocupacion };
  }).sort((a, b) => b.ganancia - a.ganancia || a.id.localeCompare(b.id));
  const elegidos = new Set(prioridad.slice(0, estado.presupuesto).filter((s) => s.ganancia > 0).map((s) => s.id));
  return { ...estado, salones: estado.salones.map((s) => ({ ...s, filtro: elegidos.has(s.id) })) };
}

export function resumen(estado) {
  const personas = estado.salones.reduce((s, aula) => s + aula.ocupacion, 0);
  const dosis = estado.salones.reduce((s, aula) => s + aula.dosis, 0);
  const base = estado.salones.reduce((s, aula) => s + aula.dosisBase, 0);
  return { personas, filtros: estado.salones.filter((s) => s.filtro).length,
    promedio: personas ? estado.salones.reduce((s, aula) => s + aula.dentro * aula.ocupacion, 0) / personas : 0,
    reduccion: base > 0 ? Math.max(0, Math.min(100, 100 * (1 - dosis / base))) : 0 };
}
