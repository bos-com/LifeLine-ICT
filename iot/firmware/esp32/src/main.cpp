#include <Arduino.h>

// This program simulates IoT sensor data without any hardware

void setup() {
  Serial.begin(115200);             // Start the serial console
  Serial.println("Simulating IoT data...");
}

void loop() {
  // Generate random rainfall and water level values
  float rain = random(0, 50);      // 0-50 mm rainfall
  float level = random(50, 150);   // 50-150 cm water level

  // Print simulated JSON payload
  Serial.print("Payload: ");
  Serial.print("{\"rain\":");
  Serial.print(rain);
  Serial.print(",\"level\":");
  Serial.print(level);
  Serial.println("}");

  delay(3000); // wait 3 seconds before sending next reading
}
