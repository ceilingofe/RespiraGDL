// Respira GDL: semaforo escolar, MQ-135 y OLED I2C HW-239 de 128x64.
// El MQ NO mide PM2.5, CO2 ni concentraciones de gases calibradas.
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <Wire.h>
#include <U8g2lib.h>

constexpr uint8_t LED_VERDE = 25, LED_AMARILLO = 26, LED_ROJO = 27;
constexpr uint8_t PIN_MQ = 34, PIN_SDA = 21, PIN_SCL = 22;
constexpr uint32_t CONSULTA_MS = 10000, CADUCIDAD_MS = 45000;
constexpr uint32_t PRUEBA_MS = 60000, ESTABILIZACION_MS = 120000;

Preferences ajustes;
U8G2_SSD1306_128X64_NONAME_F_HW_I2C pantallaSSD(U8G2_R0, U8X8_PIN_NONE);
U8G2_SH1106_128X64_NONAME_F_HW_I2C pantallaSH(U8G2_R0, U8X8_PIN_NONE);
U8G2 *pantalla = &pantallaSSD;
bool hayPantalla = false, simulada = false, hayDato = false;
String ssid, clave, urlAlertas, salon, linea, nuevoSsid, nuevaClave;
String mensaje = "Configurar por USB";
int pasoConfig = 0, nivel = -1, prueba = -1;
uint32_t ultimoDato = 0, ultimaConsulta = 0, ultimaWifi = 0;
uint32_t ultimoMQ = 0, ultimoDibujo = 0, inicioPrueba = 0;
uint32_t mqMilivoltios = 0;
float pm25 = 0;

void iniciarPantalla() {
  Wire.begin(PIN_SDA, PIN_SCL);
  Wire.setTimeOut(50);
  pantalla = ajustes.getBool("sh1106", false) ? static_cast<U8G2 *>(&pantallaSH)
                                             : static_cast<U8G2 *>(&pantallaSSD);
  for (uint8_t direccion : {0x3C, 0x3D}) {
    Wire.beginTransmission(direccion);
    if (Wire.endTransmission() == 0) {
      pantalla->setI2CAddress(direccion << 1);
      pantalla->begin();
      pantalla->setContrast(150);
      hayPantalla = true;
      Serial.printf("OLED encontrada: 0x%02X\n", direccion);
      return;
    }
  }
  Serial.println("OLED no encontrada; revisa SDA=21, SCL=22 y alimentacion 3.3 V.");
}

int colorDe(const String &valor) {
  if (valor == "verde") return 0;
  if (valor == "amarillo") return 1;
  if (valor == "rojo") return 2;
  return -1;
}

bool pruebaActiva(uint32_t ahora) {
  return prueba >= 0 && uint32_t(ahora - inicioPrueba) < PRUEBA_MS;
}

bool datoVigente(uint32_t ahora) {
  return hayDato && WiFi.status() == WL_CONNECTED &&
         uint32_t(ahora - ultimoDato) < CADUCIDAD_MS && pasoConfig == 0;
}

void conectarWifi() {
  if (ssid.isEmpty()) return;
  WiFi.begin(ssid.c_str(), clave.c_str());
  ultimaWifi = millis();
  mensaje = "Conectando WiFi";
}

void configurar() {
  pasoConfig = 1;
  hayDato = false;
  prueba = -1;
  mensaje = "Configurar por USB";
  Serial.println("Nombre real de tu red WiFi de 2.4 GHz (SSID):");
}

void recibirLinea(String valor) {
  if (pasoConfig == 1) {
    if (valor.isEmpty() || valor.length() > 32) {
      Serial.println("SSID invalido; escribe entre 1 y 32 caracteres."); return;
    }
    nuevoSsid = valor;
    pasoConfig = 2;
    Serial.println("Clave WiFi (no se imprime; linea vacia para red abierta):");
  } else if (pasoConfig == 2) {
    if (!valor.isEmpty() && (valor.length() < 8 || valor.length() > 63)) {
      Serial.println("Clave invalida; usa 8 a 63 caracteres o linea vacia."); return;
    }
    nuevaClave = valor;
    pasoConfig = 3;
    Serial.println("URL HTTP completa y real de /alertas/hoy de tu laptop:");
  } else if (pasoConfig == 3) {
    valor.trim();
    if (!valor.startsWith("http://") || !valor.endsWith("/alertas/hoy") || valor.length() > 180) {
      Serial.println("La URL debe empezar con http:// y terminar con /alertas/hoy."); return;
    }
    urlAlertas = valor;
    pasoConfig = 4;
    Serial.println("Identificador del salon (1 a 8 caracteres, por ejemplo 3A):");
  } else if (pasoConfig == 4) {
    valor.trim();
    if (valor.isEmpty() || valor.length() > 8) {
      Serial.println("Usa entre 1 y 8 caracteres para el salon."); return;
    }
    salon = valor;
    ssid = nuevoSsid;
    clave = nuevaClave;
    ajustes.putString("ssid", ssid);
    ajustes.putString("clave", clave);
    ajustes.putString("url", urlAlertas);
    ajustes.putString("salon", salon);
    nuevaClave = "";
    pasoConfig = 0;
    WiFi.disconnect();
    conectarWifi();
    ultimaConsulta = millis() - CONSULTA_MS;
    Serial.println("Configuracion guardada en esta placa. Nunca se imprime la clave.");
  } else {
    valor.trim();
    if (valor == "configurar") configurar();
    else if (valor == "vivo") {
      prueba = -1;
      hayDato = false;
      ultimaConsulta = millis() - CONSULTA_MS;
      mensaje = "Esperando API";
    } else if (valor == "verde" || valor == "amarillo" || valor == "rojo") {
      prueba = colorDe(valor);
      inicioPrueba = millis();
      Serial.println("PRUEBA SIMULADA por 60 s. No es una medicion ambiental.");
    } else if (valor == "oled") {
      ajustes.putBool("sh1106", !ajustes.getBool("sh1106", false));
      Serial.println("Cambiando SSD1306/SH1106; reiniciando.");
      delay(100);
      ESP.restart();
    } else {
      Serial.println("Comandos: configurar | verde | amarillo | rojo | vivo | oled");
    }
  }
}

void leerSerial() {
  while (Serial.available()) {
    const char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      recibirLinea(linea);
      linea = "";
    } else if (linea.length() < 200) linea += c;
  }
}

void consultar() {
  HTTPClient http;
  http.useHTTP10(true);  // JSON por stream sin transferencia HTTP chunked.
  http.setConnectTimeout(1200);
  http.setTimeout(1500);
  http.setFollowRedirects(HTTPC_DISABLE_FOLLOW_REDIRECTS);
  hayDato = false;
  mensaje = "API sin respuesta";
  if (!http.begin(urlAlertas)) return;
  const int codigo = http.GET();
  if (codigo == 200 && http.getSize() <= 16384) {
    // Una respuesta sin metadatos no demuestra que sea actual ni real.
    JsonDocument doc;
    const auto error = deserializeJson(doc, http.getStream());
    if (!error && doc["desactualizado"].is<bool>() && doc["simulado"].is<bool>() &&
        doc["pm"].is<float>() && !doc["desactualizado"].as<bool>()) {
      const int nuevo = colorDe(doc["nivel"].as<String>());
      const float pm = doc["pm"].as<float>();
      if (nuevo >= 0 && isfinite(pm) && pm >= 0) {
        nivel = nuevo;
        pm25 = pm;
        simulada = doc["simulado"].as<bool>();
        ultimoDato = millis();
        hayDato = true;
        mensaje = simulada ? "API simulada" : "API disponible";
      }
    } else mensaje = "Dato viejo/invalido";
  }
  http.end();
  Serial.printf("API HTTP %d | %s\n", codigo, mensaje.c_str());
}

void dibujar(uint32_t ahora) {
  const bool ensayo = pruebaActiva(ahora);
  const bool valido = datoVigente(ahora);
  const int color = ensayo ? prueba : valido ? nivel : -1;
  const bool parpadeo = (ahora / 500) % 2 == 0;
  const bool encendido = color < 0 ? parpadeo : (ensayo || simulada) ? parpadeo : true;
  digitalWrite(LED_VERDE, encendido && (color == 0 || color < 0));
  digitalWrite(LED_AMARILLO, encendido && (color == 1 || color < 0));
  digitalWrite(LED_ROJO, encendido && (color == 2 || color < 0));
  if (!hayPantalla || uint32_t(ahora - ultimoDibujo) < 250) return;
  ultimoDibujo = ahora;
  pantalla->clearBuffer();
  pantalla->setFont(u8g2_font_5x7_tf);
  pantalla->drawStr(1, 8, "RESPIRA GDL");
  pantalla->drawStr(128 - pantalla->getStrWidth(salon.c_str()), 8, salon.c_str());
  pantalla->drawHLine(0, 11, 128);
  // Semaforo dibujado: tres posiciones y texto, sin depender solo del color.
  pantalla->drawRFrame(1, 15, 18, 36, 4);
  for (int i = 0; i < 3; ++i) {
    if (i == color) pantalla->drawDisc(10, 22 + i * 11, 3);
    else pantalla->drawCircle(10, 22 + i * 11, 3);
  }
  const char *titulo[] = {"VERDE", "AMARILLO", "ROJO"};
  pantalla->setFont(u8g2_font_helvB10_tf);
  pantalla->drawStr(25, 28, color >= 0 ? titulo[color] : "SIN DATOS");
  pantalla->setFont(u8g2_font_5x7_tf);
  if (ensayo) pantalla->drawStr(25, 39, "PRUEBA SIMULADA");
  else if (valido) {
    char texto[30];
    snprintf(texto, sizeof(texto), "PM2.5 API %.1f", pm25);
    pantalla->drawStr(25, 39, texto);
  } else pantalla->drawStr(25, 39, mensaje.substring(0, 20).c_str());
  const char *acciones[] = {"Ver plan escolar", "Revisar actividades", "Seguir aviso escolar"};
  pantalla->drawStr(25, 49, color >= 0 ? acciones[color] : "Revisar conexion");
  pantalla->drawHLine(0, 53, 128);
  char pie[28];
  if ((ahora / 4000) % 2 == 0) {
    snprintf(pie, sizeof(pie), "MQ %lumV | %s", (unsigned long)mqMilivoltios,
             ahora < ESTABILIZACION_MS ? "INICIO" : "NO PM2.5");
  } else {
    snprintf(pie, sizeof(pie), "%s | %s", WiFi.status() == WL_CONNECTED ? "WiFi OK" : "SIN WiFi",
             ensayo || (valido && simulada) ? "SIMULADO" : valido ? "API" : "SIN DATO");
  }
  pantalla->drawStr(1, 63, pie);
  pantalla->sendBuffer();
}

void setup() {
  Serial.begin(115200);
  for (uint8_t pin : {LED_VERDE, LED_AMARILLO, LED_ROJO}) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  pinMode(PIN_MQ, INPUT);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_MQ, ADC_11db);
  ajustes.begin("respira", false);
  ssid = ajustes.getString("ssid", "");
  clave = ajustes.getString("clave", "");
  urlAlertas = ajustes.getString("url", "");
  salon = ajustes.getString("salon", "3A");
  iniciarPantalla();
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  Serial.println("Respira GDL | MQ-135: indicador SIN calibrar, no mide PM2.5 ni CO2.");
  Serial.println("El arranque de 120 s NO sustituye el acondicionamiento del fabricante (>48 h).");
  if (ssid.isEmpty() || urlAlertas.isEmpty()) {
    Serial.println("Escribe configurar y pulsa Enter para iniciar la configuracion.");
  } else conectarWifi();
}

void loop() {
  leerSerial();
  uint32_t ahora = millis();
  if (prueba >= 0 && !pruebaActiva(ahora)) {
    prueba = -1;
    hayDato = false;
    ultimaConsulta = ahora - CONSULTA_MS;
    mensaje = "Prueba terminada";
  }
  if (uint32_t(ahora - ultimoMQ) >= 2000) {
    ultimoMQ = ahora;
    uint32_t suma = 0;
    for (int i = 0; i < 16; ++i) suma += analogReadMilliVolts(PIN_MQ);
    mqMilivoltios = suma / 16;
    Serial.printf("MQ ADC=%lumV | indicador, NO PM2.5 | %s\n", (unsigned long)mqMilivoltios,
                  ahora < ESTABILIZACION_MS ? "estabilizando" : "sin calibracion");
  }
  if (pasoConfig == 0 && !ssid.isEmpty() && WiFi.status() != WL_CONNECTED &&
      uint32_t(ahora - ultimaWifi) >= 15000) {
    ultimaWifi = ahora;
    WiFi.reconnect();
  }
  if (pasoConfig == 0 && !pruebaActiva(ahora) && !urlAlertas.isEmpty() &&
      WiFi.status() == WL_CONNECTED && uint32_t(ahora - ultimaConsulta) >= CONSULTA_MS) {
    ultimaConsulta = ahora;
    consultar();
  }
  dibujar(millis());
  delay(5);
}
