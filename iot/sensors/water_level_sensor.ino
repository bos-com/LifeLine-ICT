#include <WiFi.h>
#include <HTTPClient.h>

// --- Configuration ---
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* api_endpoint = "http://your-backend-api.com/data"; // Placeholder

// --- Sensor Pins (HC-SR04 Ultrasonic Sensor) ---
const int trig_pin = 12; // GPIO12
const int echo_pin = 13; // GPIO13

// --- Sensor Calibration ---
// Distance from sensor to bottom of the water body when empty
const float container_height_cm = 100.0; 

void setup() {
  Serial.begin(115200);
  Serial.println("Starting Water Level Sensor...");

  // --- Initialize WiFi ---
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("
Connected to WiFi!");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // --- Initialize Sensor Pins ---
  pinMode(trig_pin, OUTPUT);
  pinMode(echo_pin, INPUT);
}

void loop() {
  // Report every 5 minutes (300,000 ms)
  delay(300000);

  float water_level_cm = read_water_level();
  Serial.printf("Current water level: %.2f cm
", water_level_cm);

  // --- Send data to backend ---
  send_data(water_level_cm);
}

float read_water_level() {
  // --- Trigger the sensor ---
  digitalWrite(trig_pin, LOW);
  delayMicroseconds(2);
  digitalWrite(trig_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig_pin, LOW);

  // --- Read the echo ---
  long duration = pulseIn(echo_pin, HIGH);

  // --- Calculate distance in cm ---
  // Speed of sound = 343 m/s = 0.0343 cm/us
  // Distance = (duration * speed of sound) / 2
  float distance_cm = (duration * 0.0343) / 2;

  // --- Calculate water level ---
  float water_level = container_height_cm - distance_cm;

  // --- Clamp values to avoid negative readings ---
  if (water_level < 0) {
    water_level = 0;
  }

  return water_level;
}

void send_data(float water_level) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(api_endpoint);
    http.addHeader("Content-Type", "application/json");

    // --- Create JSON payload ---
    String json_payload = "{\"sensor_type\":\"water_level\", \"value\":