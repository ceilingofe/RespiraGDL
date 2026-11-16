import test from "node:test";
import assert from "node:assert/strict";
import { crearEscenario, avanzar, configurarSalon, cambiarPresupuesto, distribuirFiltros, resumen } from "../src/data/simulacion.js";

test("un aula sin filtro conserva el equilibrio con el exterior", () => {
  const estado = cambiarPresupuesto(crearEscenario(), 0);
  const siguiente = avanzar(estado, 60);
  assert.ok(siguiente.salones.every((s) => Math.abs(s.dentro - 62) < 1e-9));
  assert.equal(resumen(siguiente).reduccion, 0);
});

test("el filtro reduce concentración y exposición respecto al contrafactual", () => {
  const siguiente = avanzar(crearEscenario(), 60);
  const aula = siguiente.salones.find((s) => s.filtro);
  assert.ok(aula.dentro > 0 && aula.dentro < aula.sinFiltro);
  assert.ok(aula.exposicion > 0 && aula.exposicion < aula.exposicionBase);
  assert.ok(resumen(siguiente).reduccion > 0);
});

test("el cálculo exacto coincide al dividir el intervalo y no modifica el original", () => {
  const estado = crearEscenario();
  const copia = structuredClone(estado);
  const completo = avanzar(estado, 10);
  const dividido = avanzar(avanzar(estado, 5), 5);
  for (let i = 0; i < 6; i++) {
    assert.ok(Math.abs(completo.salones[i].dentro - dividido.salones[i].dentro) < 1e-9);
    assert.ok(Math.abs(completo.salones[i].exposicion - dividido.salones[i].exposicion) < 1e-8);
  }
  assert.deepEqual(estado, copia);
});

test("la integral sin filtro equivale a concentración por minutos", () => {
  const estado = avanzar(cambiarPresupuesto(crearEscenario(), 0), 15);
  assert.ok(Math.abs(estado.salones[0].exposicion - 930) < 1e-9);
});

test("ni una activación manual ni el reparto exceden el inventario", () => {
  let estado = cambiarPresupuesto(crearEscenario(), 2);
  const apagado = estado.salones.find((s) => !s.filtro);
  assert.throws(() => configurarSalon(estado, apagado.id, { filtro: true }), /presupuesto/i);
  estado = distribuirFiltros(estado);
  assert.equal(estado.salones.filter((s) => s.filtro).length, 2);
  assert.equal(distribuirFiltros(cambiarPresupuesto(estado, 0)).salones.filter((s) => s.filtro).length, 0);
});

test("sin presupuesto cambia solo filtros y el reparto prioriza la ocupación comparable", () => {
  let estado = cambiarPresupuesto(crearEscenario(), 1);
  estado = { ...estado, salones: estado.salones.map((s, i) => ({ ...s, ventanas: false, ocupacion: i === 5 ? 40 : 10 })) };
  const repartido = distribuirFiltros(estado);
  assert.equal(repartido.salones.find((s) => s.filtro).id, "6B");
  assert.equal(estado.salones[5].filtro, false);
});

test("rechaza valores no físicos, desconocidos y no finitos", () => {
  assert.throws(() => crearEscenario({ fuera: NaN }), /exterior/i);
  assert.throws(() => avanzar(crearEscenario(), -1), /minutos/i);
  assert.throws(() => configurarSalon(crearEscenario(), "9Z", {}), /salón/i);
  assert.throws(() => configurarSalon(crearEscenario(), "1A", { ocupacion: 90 }), /ocupación/i);
  assert.throws(() => cambiarPresupuesto(crearEscenario(), 7), /presupuesto/i);
});

test("cero ocupantes no produce una falsa mejora porcentual", () => {
  let estado = crearEscenario();
  for (const s of estado.salones) estado = configurarSalon(estado, s.id, { ocupacion: 0 });
  assert.equal(resumen(avanzar(estado, 30)).reduccion, 0);
});

test("al cambiar el exterior no se reinicia el interior ni el tiempo", () => {
  const estado = avanzar(crearEscenario(), 10);
  const siguiente = avanzar({ ...estado, fuera: 100 }, 5);
  assert.equal(siguiente.minuto, 15);
  assert.equal(siguiente.historial.at(-1).minuto, 15);
  assert.ok(siguiente.salones.every((s) => Number.isFinite(s.dentro) && s.dentro >= 0 && s.dentro <= 100));
});
