# Semáforo de salón · ESP32 DevKit V1 + MQ-135 + OLED HW-239

Este es el montaje disponible para la demostración. El ESP32 mueve tres LEDs a partir de la API y muestra el estado en una OLED I²C de 0.96 pulgadas. El MQ-135 se lee **solo como indicador eléctrico sin calibrar**. No mide PM2.5 ni CO₂; no se envía como `pm25` al backend.

## 1. Material disponible

Un ESP32 DevKit V1 clásico (ESP32-WROOM), módulo MQ-135 con AO, OLED HW-239 de cuatro pines, tres LEDs independientes, **seis resistencias de 1 kΩ**, protoboard, cables y USB. Los números que siguen son **GPIO impresos en la placa**, no posiciones físicas. GPIO34 es entrada; no se usa para un LED. Este cableado no corresponde a ESP32-C3/S3.

## 2. Conecta con el USB desconectado

- GPIO25 → resistencia de 1 kΩ → pata larga (ánodo) del LED verde.
- GPIO26 → resistencia de 1 kΩ → pata larga del LED amarillo.
- GPIO27 → resistencia de 1 kΩ → pata larga del LED rojo.
- Las tres patas cortas (cátodos, lado plano del LED) → GND común.
- MQ-135 VCC → pin de **5 V/VIN que entregue los 5 V del USB** de tu DevKit. No a 3V3. Si tu variante no ofrece esa salida, usa alimentación regulada de 5 V y comparte GND; no unas dos alimentaciones de 5 V diferentes.
- MQ-135 GND → GND común.
- MQ-135 AO → divisor de abajo → GPIO34. **DO queda desconectado.**
- OLED VCC → **3V3** del ESP32; OLED GND → GND.
- OLED SCL → GPIO22; OLED SDA → GPIO21. Sigue las etiquetas: el orden físico puede cambiar entre módulos.

El divisor lo construyes con tres resistencias iguales de 1 kΩ:

```text
MQ AO ──[1 kΩ]──[1 kΩ]──●── GPIO34
                        │
                      [1 kΩ]
                        │
                       GND
```

El punto ● recibe un tercio de AO: si AO llega a 5 V, GPIO34 recibe aproximadamente 1.67 V. La OLED no necesita este divisor. Nunca conectes AO o DO de un módulo de 5 V directamente a un GPIO. El calentador del MQ puede consumir cerca de 190 mA: usa un USB estable, no una salida GPIO, y no toques la cápsula caliente.

## 3. Carga el programa

En Arduino IDE instala **esp32 by Espressif Systems**, **ArduinoJson 7** y **U8g2**. Abre `semaforo-mq135.ino`, selecciona ESP32 Dev Module y el puerto COM de la placa. Carga el programa. También puedes usar PlatformIO desde esta carpeta:

```powershell
pio run
pio run -t upload
pio device monitor
```

El código de los nodos PMS5003 originales sigue en `../nodo-aire/`; no es el programa de este montaje.

## 4. Configura los valores reales por USB

Abre el monitor serial a **115200 baudios**, con terminador **nueva línea**. Reinicia la placa si perdiste los primeros mensajes. Escribe `configurar` y pulsa Enter. El programa pide, en este orden:

1. Nombre real de la red WiFi de **2.4 GHz**.
2. Contraseña real de esa red. El firmware no la imprime.
3. URL HTTP completa de `/alertas/hoy` de la laptop que ejecuta el backend. Obtén su IPv4 con `ipconfig`; combina `http://`, esa IPv4, `:8000` y `/alertas/hoy`. No uses localhost ni la URL de GitHub Pages. Es una conexión HTTP de demostración en una red de confianza.
4. Identificador real del salón que se mostrará, por ejemplo `3A` en nuestra escuela ficticia.

Los valores se guardan en la memoria de **esa placa**, fuera del código y del repositorio. Esa memoria no está cifrada por este firmware: no entregues una placa configurada con credenciales de una red privada. La clave no necesita enviarse al equipo ni al chat.

## 5. Comprueba primero el montaje, después la API

Escribe `verde`, `amarillo` y `rojo`, uno a la vez. Cada comando enciende de forma intermitente su LED durante 60 s y dibuja el semáforo en pantalla con **PRUEBA SIMULADA**. Esto prueba LEDs y pantalla; no mide el ambiente. Escribe `vivo` para terminar antes y consultar la API.

La pantalla tiene nombre del salón, tres posiciones del semáforo, texto grande, PM2.5 **de la API** cuando existe, acción escolar, conexión y milivoltios del MQ. El pie alterna estado y MQ para mantener el texto legible. En una OLED de franja amarilla y azul, esos colores son físicos y no representan por sí mismos la calidad del aire.

- **Un LED fijo:** respuesta vigente de la API, marcada como no simulada.
- **Un LED intermitente + SIMULADO:** la API usó lecturas simuladas o se activó la prueba por USB.
- **Los tres LEDs intermitentes + SIN DATOS:** falta configuración, WiFi, API, metadatos, o el dato está vencido. No significa aire peligroso ni limpio.
- El programa consulta cada 10 s y descarta un dato después de 45 s sin respuesta válida. También rechaza datos que el servidor marque como antiguos. Esta vigencia de comunicación no sustituye la fecha de medición del servidor.

Para alimentar el semáforo desde la API, inicia el backend en `0.0.0.0:8000`, conecta laptop y ESP32 a la misma red y verifica la URL desde el teléfono. Los campos `simulado` y `desactualizado` de `/alertas/hoy` forman parte de esta implementación: una API anterior no los ofrece y el firmware muestra SIN DATOS deliberadamente.

Las lecturas simuladas de `python -m scripts.simular_nodos --salon 3A` solo se usan para el promedio escolar durante 7:00–14:59, según el backend. Fuera de ese horario puedes demostrar el hardware con los comandos seriales, sin fingir un dato actual.

## 6. OLED y MQ: qué esperar

La OLED se busca en 0x3C y 0x3D. SSD1306 128×64 es la configuración inicial para HW-239; si responde por I²C pero queda desplazada o no dibuja bien, escribe `oled`: cambia a SH1106 y reinicia. Escribe el mismo comando para volver. La serigrafía HW-239 por sí sola no verifica el controlador de cada lote.

El MQ muestra el voltaje **en GPIO34, después del divisor**. Un valor mayor no se convierte automáticamente en una categoría de salud. La fase inicial de 120 s solo advierte de variación de arranque; **no es una calibración**. Winsen especifica más de 48 horas de precalentamiento en sus condiciones de prueba. No provoques humo, llamas o escapes de gas para la demo: muestra la lectura y las limitaciones. Una lectura pegada en cero exige revisar AO/GND/divisor; no certifica aire limpio.

No se ha realizado aquí una prueba física de este montaje. Compilar no verifica polaridad, corriente de alimentación, calibración ni cableado real.

Fuentes: [MQ-135, Winsen](https://www.winsen-sensor.com/manual/mq135.html?lang=en), [GPIO, Espressif](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gpio.html), [U8g2](https://github.com/olikraus/u8g2).
