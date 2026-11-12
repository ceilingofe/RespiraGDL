// Nodo Respira GDL: lee PM2.5/PM10 del PMS5003 y lo manda al backend.
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "PMS.h"
#include "config.h"

HardwareSerial pmsSerial(2);   // RX2=16, TX2=17
PMS pms(pmsSerial);
PMS::DATA data;

void setup() {
  Serial.begin(115200);
  pmsSerial.begin(9600, SERIAL_8N1, 16, 17);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print('.'); }
  Serial.println("\nWiFi conectado");
}

void loop() {
  if (pms.readUntil(data, 2000)) {
    JsonDocument doc;
    doc["nodo_id"] = NODO_ID;
    doc["pm25"] = data.PM_AE_UG_2_5;
    doc["pm10"] = data.PM_AE_UG_10_0;
    String body; serializeJson(doc, body);
    HTTPClient http; http.begin(API_URL);
    http.addHeader("Content-Type", "application/json");
    int code = http.POST(body);
    Serial.printf("PM2.5=%d -> %d\n", data.PM_AE_UG_2_5, code);
    http.end();
  }
  delay(INTERVALO_MS);
}
