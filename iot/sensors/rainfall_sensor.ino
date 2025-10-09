#include <WiFi.h>
#include <HTTPClient.h>

// --- Configuration ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* api_endpoint = "http://your-backend-api.com/data"; // Placeholder

// --- Sensor Pin ---
const int rain_sensor_pin = 14; // GPIO14

// --- Sensor State ---
volatile int tip_count = 0;
const float bucket_size_mm = 0.2794; // mm of rain per tip
unsigned long last_tip_time = 0;

// --- Debounce ---
const long debounce_delay = 50; // ms

// --- Interrupt Service Routine (ISR) ---
void IRAM_ATTR handle_interrupt() {
  if ((millis() - last_tip_time) > debounce_delay) {
    tip_count++;
    last_tip_time = millis();
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Starting Rainfall Sensor...");

  // --- Initialize WiFi ---
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // --- Initialize Sensor Pin ---
  pinMode(rain_sensor_pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(rain_sensor_pin), handle_interrupt, FALLING);
}

void loop() {
  // Report every 15 minutes (900,000 ms)
  delay(900000);

  if (tip_count > 0) {
    float rainfall_mm = tip_count * bucket_size_mm;
    Serial.printf("Rainfall detected: %.4f mm\n", rainfall_mm);

    // --- Send data to backend ---
    send_data(rainfall_mm);

    // --- Reset count ---
    tip_count = 0;
  } else {
    Serial.println("No rainfall detected in the last 15 minutes.");
  }
}

void send_data(float rainfall) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_endpoint);
    http.addHeader("Content-Type", "application/json");

    // --- Create JSON payload ---
    String json_payload = "{\"sensor_type\":\"rainfall\", \"value\":