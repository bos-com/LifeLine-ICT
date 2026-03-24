// Example ESP32 Arduino sketch for sending sensor data to LifeLine-ICT backend
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* serverUrl = "http://<YOUR_SERVER_IP>:5000/data";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"sensor_id\": 1, \"metric\": \"temperature\", \"value\": 23.5, \"timestamp\": \"2025-10-11T12:00:00Z\"}";
    int httpResponseCode = http.POST(payload);
    String response = http.getString();
    Serial.print("Response code: ");
    Serial.println(httpResponseCode);
    Serial.println(response);
    http.end();
  }
  delay(60000); // Send data every 60 seconds
}
