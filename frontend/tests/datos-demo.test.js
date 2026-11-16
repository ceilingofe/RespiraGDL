import test from "node:test";
import assert from "node:assert/strict";
import { MOCK_PRONOSTICO, MOCK_ESCUELA, nivelPm25 } from "../src/data/demo.js";

test("los colores de ejemplo corresponden a su concentración, con los cortes escolares", () => {
  const color = { good: "verde", ok: "verde", bad: "amarillo", vbad: "rojo", ext: "rojo" };
  assert.equal(MOCK_ESCUELA.semaforoHoy, color[nivelPm25(MOCK_ESCUELA.pm25Hoy).id]);
  assert.equal(MOCK_PRONOSTICO.semaforo, color[nivelPm25(MOCK_PRONOSTICO.pm25).id]);
});
