import metricas from "../../../ml/resultados/metricas.json";

const FUENTE_SALUD = "https://iieg.gob.mx/ns/wp-content/uploads/2025/03/ficha_enfermedades_poblacion_jalisco_iieg_2023.pdf";
const ESTACIONES = [
  { nombre: "Miravalle", cobertura: 68.6, promedio: 25.2, dias: 571 },
  { nombre: "Las Pintas", cobertura: 66.7, promedio: 39.5, dias: 812 },
  { nombre: "Santa Fe", cobertura: 42.5, promedio: 27.2, dias: 412 },
  { nombre: "Centro", cobertura: 70.0, promedio: 20.0, dias: 372 },
];

export default function Evidencia() {
  return (
    <main className="rg-app">
      <div className="rg-demo-note" role="status">
        Evidencia histórica y evaluación retrospectiva. No son mediciones actuales del salón ni resultados clínicos.
      </div>
      <header className="rg-app__head">
        <div><p className="rg-eyebrow">Reto 02 · Salud y Bienestar</p><h1>Datos que puedes verificar</h1></div>
        <a className="rg-pill rg-pill--blue" href="#/tablero">Abrir demostración</a>
      </header>
      <section className="rg-panel rg-surface-mint" aria-labelledby="salud-evidencia">
        <h2 id="salud-evidencia">Por qué trabajar en prevención escolar</h2>
        <p><strong>13,613 casos nuevos de asma en Jalisco durante 2023.</strong> El IIEG los publica a partir del Anuario de Morbilidad de la DGE: 8,263 en mujeres y 5,350 en hombres.</p>
        <p>Es un conteo estatal de todas las edades; no representa prevalencia infantil, personas únicas ni casos causados por contaminación. Lo usamos para caracterizar el problema de salud, sin extrapolarlo a nuestra escuela ficticia.</p>
        <a href={FUENTE_SALUD} target="_blank" rel="noreferrer">Consultar dataset 11 · IIEG / DGE, página 3</a>
      </section>
      <section className="rg-section" aria-labelledby="aire-evidencia">
        <header className="rg-section__head">
          <h2 id="aire-evidencia">Dónde empezar a probar la solución</h2>
          <p>Dataset 39 · SIMAJ / SEMADET. Resumen del repositorio para 2020–2024. La cobertura incompleta impide tratar los días sin dato como días limpios.</p>
        </header>
        <div className="rg-grid3">
          {ESTACIONES.map((e) => (
            <article key={e.nombre} className="rg-panel rg-surface-sky">
              <h3>{e.nombre}</h3>
              <p><strong>{e.dias}</strong> días observados con promedio de 24 h mayor a 25 µg/m³ en el periodo completo.</p>
              <p>PM2.5 promedio: {e.promedio} µg/m³. Cobertura horaria: {e.cobertura} %.</p>
            </article>
          ))}
        </div>
        <p>Miravalle delimita la demo; no afirmamos que sea la estación más contaminada ni que represente el aire de cada salón. El umbral es una referencia de análisis: no convierte el histórico en una alerta oficial actual.</p>
        <a href="https://github.com/ceilingofe/RespiraGDL/blob/main/docs/resumen_datos.csv" target="_blank" rel="noreferrer">Revisar el resumen y su método en el repositorio</a>
      </section>
      <section className="rg-panel rg-surface-lilac" aria-labelledby="modelo-evidencia">
        <h2 id="modelo-evidencia">Qué aporta el modelo y qué sacrifica</h2>
        <p>Prueba temporal: {metricas.periodo_prueba.join(" a ")} · {metricas.dias_prueba} días de Miravalle. Se entrenó con {metricas.dias_entrenamiento} días de 2020–2023. Objetivo: promedio de PM2.5 de la siguiente jornada escolar.</p>
        <ul>
          <li>Error absoluto medio: modelo {metricas.modelo.mae} µg/m³; persistencia {metricas.persistencia.mae} µg/m³. Mejora registrada: {metricas.mejora_mae_pct} %.</li>
          <li>Días amarillo/rojo detectados: modelo {metricas.modelo.dias_amarillo_o_rojo_detectados_pct} %; persistencia {metricas.persistencia.dias_amarillo_o_rojo_detectados_pct} %.</li>
          <li>Falsas alarmas: modelo {metricas.modelo.falsas_alarmas_pct} %; persistencia {metricas.persistencia.falsas_alarmas_pct} %.</li>
          <li>Color correcto: modelo {metricas.modelo.acierto_semaforo_pct} %; persistencia {metricas.persistencia.acierto_semaforo_pct} %.</li>
        </ul>
        <p>Mejorar el error medio no equivale a acertar más colores. El modelo detectó más jornadas adversas, con más falsas alarmas. Estas métricas vienen del artefacto guardado en el repositorio; no demuestran menos crisis de asma ni validación médica.</p>
        <p>La limpieza se corrigió después para conservar completos los huecos largos. Estos resultados y el resumen histórico son anteriores a la corrección; requieren reprocesamiento y nueva evaluación antes de atribuirlos al pipeline actual.</p>
      </section>
      <section className="rg-section" aria-labelledby="alcance-evidencia">
        <h2 id="alcance-evidencia">Qué funciona y qué falta validar</h2>
        <ul>
          <li>Software: tablero, plan escolar y comparación de pronósticos. En GitHub Pages los datos de respaldo son simulados.</li>
          <li>Hardware disponible: ESP32, tres LEDs, OLED y MQ-135. El MQ muestra una señal eléctrica; no mide PM2.5 ni CO₂.</li>
          <li>Sin PMS5003, ventilador ni filtros no hay reducción física de PM2.5 medida por este equipo.</li>
          <li>Las escuelas y los alumnos de la demo son ficticios. El acceso por rol es simulado; no admite datos reales de salud.</li>
          <li>Piloto propuesto: comparar sensores PM2.5 antes y después del filtro, registrar cobertura y medir cuántas acciones escolares se completan. No hay resultados de ese piloto todavía.</li>
        </ul>
        <p>Ingeniería aporta el prototipo; salud pública aporta el contexto preventivo y la protección de datos; ciencia de datos aporta limpieza y evaluación temporal. El sistema orienta, recuerda y alerta; no diagnostica ni sustituye el plan médico individual.</p>
      </section>
    </main>
  );
}
