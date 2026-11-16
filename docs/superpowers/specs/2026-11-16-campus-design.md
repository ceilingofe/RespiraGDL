# Escuela 3D · diseño de la demostración

Sergio solicitó seis salones como cubos 3D con personas, alertas y prototipo, siguiendo el diseño del sitio, y autorizó continuar autónomamente y publicar una rama. Se conserva la prohibición de push directo a main y no se integra el PR sin solicitud.

Enfoque elegido: SVG isométrico React, sin motor WebGL ni nuevas dependencias. Favorece móvil, accesibilidad y una demo reproducible. La vista es un laboratorio de decisiones con datos ficticios, nunca un gemelo calibrado.

Cada salón muestra ocupación ilustrativa, filtro, semáforo, PM2.5 del modelo y dispositivo ESP32/OLED. El panel permite seleccionar salón por teclado, cambiar filtro/ventanas/ocupación, pausar, avanzar y restablecer. El usuario ajusta concentración exterior y presupuesto de filtros. Un algoritmo compara ganancias de exposición del modelo durante la próxima hora y ensaya el reparto de filtros bajo ese presupuesto.

Modelo: mezcla perfecta, volumen 180 m³, CADR ilustrativo 400 m³/h, recambio cerrado 0.6 h⁻¹ y abierto 3 h⁻¹, sin generación interior ni deposición. Evolución exponencial exacta e integral temporal de concentración. Comparación contrafactual con igual ventilación y sin filtración. Supuestos editables en código, declarados en interfaz; no son resultados medidos ni clínicos.

El modelo y UI nunca escriben a /lecturas. Sin conexión el dispositivo dibujado muestra SIN DATOS; eso no implica aire bueno. Los colores siguen el semáforo escolar existente. Se usan únicamente tokens visuales del proyecto. Movimiento solo al reproducir y con soporte de movimiento reducido. El boceto de Sergio guía la composición de dos filas por tres aulas.

Validación: pruebas de ecuación, integral, límite de presupuesto, no mutación, restauración y estados sin conexión. Build de producción, recorrido navegador desktop/móvil/teclado, firmware PlatformIO y batería backend. Revisión independiente antes del push. Se repitió la evaluación histórica tras corregir el pipeline, conservando hashes y versiones.
