#include <SPI.h>
#include <LoRa.h>
#include <WiFi.h>
#include <Firebase_ESP_Client.h>

// =============================
// WIFI
// =============================
#define WIFI_SSID "nurfitri"
#define WIFI_PASSWORD "12345678"

// =============================
// FIREBASE
// =============================
#define API_KEY "AIzaSyCr2glIokJBLIDpKnKesfahpduFa3qnyRg"
#define FIREBASE_PROJECT_ID "uts-telemetri-nurfitri"

#define USER_EMAIL "nurfitri@iot.com"
#define USER_PASSWORD "12345678"

// =============================
// LORA
// =============================
#define SS 5
#define RST 14
#define DIO0 26

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

String temperature;
String humidity;
String soil;
String ldr;
String rssi;

// =============================
void setup()
{

  Serial.begin(115200);

  // =============================
  // WIFI
  // =============================
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Menghubungkan WiFi");

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println();
  Serial.println("WiFi Connected");

  // =============================
  // FIREBASE CONFIG
  // =============================
  config.api_key = API_KEY;

  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  Serial.println("Firebase siap");

  // =============================
  // LORA
  // =============================
  LoRa.setPins(SS, RST, DIO0);

  if (!LoRa.begin(915E6))
  {
    Serial.println("LoRa gagal");
    while (1);
  }

  Serial.println("LoRa Receiver Ready");
}

// =============================
void loop()
{

  int packetSize = LoRa.parsePacket();

  if (packetSize)
  {

    String data = "";

    while (LoRa.available())
    {
      data += (char)LoRa.read();
    }

    int signal = LoRa.packetRssi();
    rssi = String(signal);

    Serial.println("Data diterima:");
    Serial.println(data);

    // contoh data:
    // TEMP=28.5;HUM=65.2;SOIL=1200;LDR=800

    int t1 = data.indexOf("TEMP=");
    int t2 = data.indexOf(";HUM=");

    int h1 = data.indexOf("HUM=");
    int h2 = data.indexOf(";SOIL=");

    int s1 = data.indexOf("SOIL=");
    int s2 = data.indexOf(";LDR=");

    int l1 = data.indexOf("LDR=");

    temperature = data.substring(t1 + 5, t2);
    humidity = data.substring(h1 + 4, h2);
    soil = data.substring(s1 + 5, s2);
    ldr = data.substring(l1 + 4);

    Serial.println("Parsing Data:");
    Serial.println("Temp : " + temperature);
    Serial.println("Hum  : " + humidity);
    Serial.println("Soil : " + soil);
    Serial.println("LDR  : " + ldr);
    Serial.println("RSSI : " + rssi);

    sendToFirebase();
  }
}

// =============================
void sendToFirebase()
{

  FirebaseJson content;

  content.set("fields/suhu/doubleValue", temperature.toFloat());
  content.set("fields/kelembapan/doubleValue", humidity.toFloat());
  content.set("fields/soil/integerValue", soil.toInt());
  content.set("fields/cahaya/integerValue", ldr.toInt());
  content.set("fields/rssi/integerValue", rssi.toInt());

  String documentPath = "sensor/node1";

  if (Firebase.Firestore.patchDocument(
        &fbdo,
        FIREBASE_PROJECT_ID,
        "",
        documentPath.c_str(),
        content.raw(),
        "suhu,kelembapan,soil,cahaya,rssi"))
  {
    Serial.println("Data terkirim ke Firestore");
  }
  else
  {
    Serial.println("Gagal kirim");
    Serial.println(fbdo.errorReason());
  }
}