#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>

// ============================
// KONFIGURASI PIN LORA
// ============================
#define SS   5
#define RST  14
#define DIO0 26

// ============================
// KONFIGURASI SENSOR
// ============================
#define DHTPIN 4
#define DHTTYPE DHT22

#define SOIL_PIN 34
#define LDR_PIN 35

DHT dht(DHTPIN, DHTTYPE);

// ============================
// SETUP
// ============================
void setup() {

  Serial.begin(115200);
  Serial.println("ESP32 LoRa Sensor Node");

  dht.begin();

  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(915E6)) {
    Serial.println("LoRa gagal start");
    while (1);
  }

  Serial.println("LoRa siap mengirim data");
}

// ============================
// LOOP
// ============================
void loop() {

  // ======================
  // BACA SENSOR
  // ======================
  float suhu = dht.readTemperature();
  float hum  = dht.readHumidity();

  int soil = analogRead(SOIL_PIN);
  int ldr  = analogRead(LDR_PIN);

  // ======================
  // CEK SENSOR ERROR
  // ======================
  if (isnan(suhu) || isnan(hum)) {
    Serial.println("Gagal membaca DHT22");
    return;
  }

  // ======================
  // FORMAT DATA
  // ======================
  String data = "";

  data += "TEMP=" + String(suhu) + ";";
  data += "HUM=" + String(hum) + ";";
  data += "SOIL=" + String(soil) + ";";
  data += "LDR=" + String(ldr);

  // ======================
  // KIRIM DATA LORA
  // ======================
  LoRa.beginPacket();
  LoRa.print(data);
  LoRa.endPacket();

  // ======================
  // TAMPIL DI SERIAL
  // ======================
  Serial.println("===== DATA SENSOR =====");
  Serial.print("Suhu        : ");
  Serial.print(suhu);
  Serial.println(" °C");

  Serial.print("Kelembapan  : ");
  Serial.print(hum);
  Serial.println(" %");

  Serial.print("Soil Moist  : ");
  Serial.println(soil);

  Serial.print("LDR Cahaya  : ");
  Serial.println(ldr);

  Serial.println("========================");

  Serial.print("Data dikirim : ");
  Serial.println(data);

  Serial.println();

  delay(2000);
}