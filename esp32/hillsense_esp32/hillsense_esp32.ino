#include <WiFi.h>
#include <Firebase_ESP_Client.h>

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

#include <DHT.h>

// ======================================
// WIFI DETAILS
// ======================================

#define WIFI_SSID "Emmanuel"
#define WIFI_PASSWORD "emmanuel@2021"

// ======================================
// FIREBASE DETAILS
// ======================================

#define API_KEY "AIzaSyDucc9PCKDQeL0fhnO1B6VC2s-BuTGyvRo"

#define DATABASE_URL "https://hillsenseai-default-rtdb.firebaseio.com/"

// ======================================
// DHT11 SETTINGS
// ======================================

#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// ======================================
// FIREBASE OBJECTS
// ======================================

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// ======================================
// SOIL MOISTURE SENSOR
// ======================================

int soilPin = 34;

// ======================================
// SETUP
// ======================================

void setup() {

  Serial.begin(115200);

  dht.begin();

  // ----------------------------------
  // CONNECT TO WIFI
  // ----------------------------------

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {

    Serial.print(".");

    delay(1000);
  }

  Serial.println();
  Serial.println("WiFi Connected");

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // ----------------------------------
  // FIREBASE CONFIG
  // ----------------------------------

  config.api_key = API_KEY;

  config.database_url = DATABASE_URL;

  config.token_status_callback =
      tokenStatusCallback;

  // ----------------------------------
  // FIREBASE SIGNUP
  // ----------------------------------

  if (Firebase.signUp(&config, &auth, "", "")) {

    Serial.println("Firebase Signup OK");

  } else {

    Serial.println("Firebase Signup Failed");

    Serial.println(
      config.signer.signupError.message.c_str()
    );
  }

  Firebase.begin(&config, &auth);

  Firebase.reconnectWiFi(true);

  Firebase.setDoubleDigits(5);

  Serial.println("Firebase Started");
}

// ======================================
// LOOP
// ======================================

void loop() {

  // ----------------------------------
  // CHECK WIFI
  // ----------------------------------

  if (WiFi.status() != WL_CONNECTED) {

    Serial.println("WiFi Disconnected");

    WiFi.reconnect();

    delay(3000);

    return;
  }

  // ----------------------------------
  // READ DHT11
  // ----------------------------------

  float temperature =
      dht.readTemperature();

  float humidity =
      dht.readHumidity();

  // ----------------------------------
  // READ SOIL MOISTURE
  // ----------------------------------

  int raw =
      analogRead(soilPin);

  float moisture =
      100 - ((raw / 4095.0) * 100);

  // ----------------------------------
  // CHECK SENSOR VALUES
  // ----------------------------------

  if (isnan(temperature) || isnan(humidity)) {

    Serial.println("DHT Sensor Error");

    delay(2000);

    return;
  }

  // ----------------------------------
  // PRINT VALUES
  // ----------------------------------

  Serial.println("====================");

  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");

  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");

  Serial.print("Moisture: ");
  Serial.print(moisture);
  Serial.println(" %");

  // ----------------------------------
  // SEND TO FIREBASE
  // ----------------------------------

  bool tempStatus =
      Firebase.RTDB.setFloat(
          &fbdo,
          "/sensor/temperature",
          temperature
      );

  bool humStatus =
      Firebase.RTDB.setFloat(
          &fbdo,
          "/sensor/humidity",
          humidity
      );

  bool moistStatus =
      Firebase.RTDB.setFloat(
          &fbdo,
          "/sensor/moisture",
          moisture
      );

  // ----------------------------------
  // FIREBASE STATUS
  // ----------------------------------

  if (tempStatus &&
      humStatus &&
      moistStatus) {

    Serial.println("Firebase Upload OK");

  } else {

    Serial.println("Firebase Upload Failed");

    Serial.println(
        fbdo.errorReason()
    );
  }

  delay(5000);
}