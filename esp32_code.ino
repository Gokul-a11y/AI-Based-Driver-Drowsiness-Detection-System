#include <Wire.h>
#include <LiquidCrystal_I2C.h>

#define BUZZER 14   // 🔊 buzzer + LED same pin

LiquidCrystal_I2C lcd(0x27, 16, 2); // use your working address

String data = "";

void setup() {
  Serial.begin(9600);

  // I2C setup
  Wire.begin(4,5);

  pinMode(BUZZER, OUTPUT);
  digitalWrite(BUZZER, LOW);

  lcd.begin(16, 2);
  lcd.backlight();

  // Startup message
  lcd.setCursor(0,0);
  lcd.print("DrowsinessSystem");
  delay(30000);
  lcd.clear();
}

void loop() {

  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      data.trim();

      // 🟢 AWAKE
      if (data == "AWAKE") {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Status:");
        lcd.setCursor(0,1);
        lcd.print("AWAKE");

        digitalWrite(BUZZER, LOW); // 🔊 OFF + LED OFF
      }

      // 🔵 DROWSY
      else if (data == "SHORT") {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Status:");
        lcd.setCursor(0,1);
        lcd.print("DROWSY");

        digitalWrite(BUZZER, HIGH); // 🔊 + 💡 ON
        delay(300);
        digitalWrite(BUZZER, LOW);
      }

      // 🔴 DEEP SLEEP (20 sec continuous)
      else if (data == "LONG") {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Status:");
        lcd.setCursor(0,1);
        lcd.print("DEEP SLEEP");

        digitalWrite(BUZZER, HIGH);  // 🔊 + 💡 ON
        delay(2000);                // 🔥 20 sec
        digitalWrite(BUZZER, LOW);
      }

      // ⚠️ MICROSLEEP (alert pattern)
      else if (data == "MICROSLEEP") {
        lcd.clear();
        lcd.setCursor(0,0);
        lcd.print("Status:");
        lcd.setCursor(0,1);
        lcd.print("MICROSLEEP");

        for (int i = 0; i < 5; i++) {
          digitalWrite(BUZZER, HIGH); // 🔊 + 💡 ON
          delay(200);
          digitalWrite(BUZZER, LOW);
          delay(200);
        }
      }

      data = "";
    }
    else {
      data += c;
    }
  }
}