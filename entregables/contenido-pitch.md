# Contenido para pitch · ocho diapositivas

Este archivo contiene el contenido para maquetar; no es todavía un PPT/PDF. Usar los identificadores del hackathon y `docs/diseno/README.md`. No presentar como realizados pilotos, pruebas físicas o revisiones médicas pendientes.

## 1. Respira GDL · decisiones escolares antes de un día de aire contaminado

Una maestra, un salón y una decisión de prevención. Prototipo para Miravalle, Guadalajara. Equipo Sergio, Juan, Carlos y Damaris. Escuela ficticia de demostración.

## 2. Un problema local con dos fuentes verificables

SIMAJ: exposición histórica de Miravalle, 2020–2024, con cobertura incompleta. Anuario de Morbilidad: contexto estatal de asma, sin extrapolación infantil ni atribución causal. Mostrar ambos enlaces de `docs/datasets.md` y distinguir periodo histórico de fecha actual.

## 3. De los datos a una acción

Tablero → revisión de tareas de maestra → preparación de aviso. Semáforo visible en OLED y LEDs. Texto y posición complementan el color. Demostrar el recorrido, conservando la etiqueta de simulación.

## 4. El prototipo disponible y su alcance

Software React + FastAPI/SQLite; ESP32 + MQ-135 + tres LEDs + OLED. El MQ no mide partículas. Sin PMS5003/filtro, las lecturas dentro/fuera son simuladas. Desconexión significa SIN DATOS. Diferenciador: información comprensible y procedencia explícita frente a una cifra aislada.

## 5. Evaluamos contra una alternativa sencilla

Reevaluación retrospectiva con pipeline corregido: 276 días de prueba de 2024, MAE 10.96 frente a 11.56 de persistencia. Mostrar también falsas alarmas y acierto de color. Mejor MAE no equivale a eficacia clínica. Se descargaron los archivos oficiales, se reentrenó y se verificaron las predicciones del modelo recargado; no hay validación externa ni clínica.

## 6. Tres disciplinas y protección de menores

Ingeniería: actuador e interfaz. Ciencia de datos: modelo y evaluación. Salud pública: prevención, contexto y equidad. Sin datos reales de menores en la demo. Acceso por rol simulado; antes de un piloto se requiere consentimiento, seguridad y revisión profesional.

## 7. Un piloto que pueda comprobarse

Escuela autorizada → cotejar dos sensores PM2.5 → comparar periodos con/sin filtro → medir cobertura, exposición, comprensión y recepción de avisos. No hay resultados de ese piloto todavía. Presupuesto de la web ilustrativo, sujeto a cotización, mantenimiento y aclaración de la BOM.

## 8. Qué pedimos y qué entregaríamos

Propuesta de siguiente colaboración: autorización escolar, revisión de salud y acceso a sensores de partículas para ejecutar un piloto medible. Entregamos código, fuentes y límites del prototipo. Declarar uso de IA como apoyo. No prometer diagnóstico, reducción de crisis o validación ya conseguida.
