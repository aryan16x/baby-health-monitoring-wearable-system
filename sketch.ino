#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Wire.h>
#include <MPU6050.h>

// Wi-Fi credentials (Wokwi simulation)
const char* ssid = "Wokwi-GUEST";  // Use the default Wokwi network
const char* password = "";         // No password required for Wokwi

// Backend endpoint (Replace with your server's URL)
const char* serverName = "https://baby-health-monitoring-wearable-device.onrender.com/data";

// DHT sensor setup (for temperature monitoring)
#define DHT_SENSOR_PIN  32
#define DHT_SENSOR_TYPE DHT22
DHT dht_sensor(DHT_SENSOR_PIN, DHT_SENSOR_TYPE);

// MPU6050 (for fall detection)
MPU6050 mpu;

// Sound sensor pin (for cry detection)
#define SOUND_SENSOR_PIN 34  // Pin connected to sound sensor

// Thresholds
const int CRY_THRESHOLD = 500;    // Threshold for cry detection
const float FALL_THRESHOLD = 1.5; // Threshold for fall detection (in g)

// Sleep monitoring thresholds
float movementThreshold = 0.05; // Define based on test values
int sleepStage = 0; // 0 for awake, 1 for light sleep, 2 for deep sleep

void setup() {
  Serial.begin(115200);

  // Initialize DHT sensor
  dht_sensor.begin();

  // Initialize MPU6050
  Wire.begin();
  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU6050 connection failed!");
    while (1);
  } else {
    Serial.println("MPU6050 connected");
  }

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  // Collect data from the DHT sensor (simulate temperature)
  float tempC = dht_sensor.readTemperature();
  float humidity = dht_sensor.readHumidity();

  // Heart rate simulation (random between 60 and 120 bpm)
  int heartRate = random(60, 121);

  // Read acceleration data from MPU6050 for fall detection
  VectorInt16 accel;
  mpu.getAcceleration(&accel.x, &accel.y, &accel.z);

  // Calculate total acceleration in g
  float totalAccel = sqrt(sq(accel.x) + sq(accel.y) + sq(accel.z)) / 16384.0;

  // Detect fall if acceleration exceeds threshold
  bool fallDetected = totalAccel > FALL_THRESHOLD;

  // Determine sleep stage
  if (totalAccel < movementThreshold) {
    sleepStage = 2; // Deep sleep (minimal movement)
  } else if (totalAccel >= movementThreshold) {
    sleepStage = 1; // Light sleep or awake (movement detected)
  }

  // Read sound level for cry detection
  int soundLevel = analogRead(SOUND_SENSOR_PIN);
  bool cryDetected = soundLevel > CRY_THRESHOLD;

  // Display data
  if (isnan(tempC) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Temperature: ");
    Serial.println(tempC);
    Serial.print("Humidity: ");
    Serial.println(humidity);
    Serial.print("Heart Rate: ");
    Serial.println(heartRate);
    Serial.print("Fall Detected: ");
    Serial.println(fallDetected ? "True" : "False");
    Serial.print("Cry Detected: ");
    Serial.println(cryDetected ? "True" : "False");
    // Print sleep stage
    if (sleepStage == 2) {
      Serial.println("Deep sleep");
    } else {
      Serial.println("Light sleep or awake");
    }
  }

  // Send the data to the backend
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    // Prepare data to send
    String postData = "temperature=" + String(tempC) +
                      "&humidity=" + String(humidity) +
                      "&heartRate=" + String(heartRate) +
                      "&fallDetected=" + String(fallDetected) +
                      "&cryDetected=" + String(cryDetected) +
                      "&sleepStage=" + String(sleepStage);

    // Send the POST request
    int httpResponseCode = http.POST(postData);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("HTTP Response code: " + String(httpResponseCode));
      Serial.println("Response: " + response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }

  delay(5000);  // Adjust delay to control the frequency of sending data
}
