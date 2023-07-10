#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

BluetoothSerial SerialBT;
int LED = 2;

void setup() {
  Serial.begin(115200);
  SerialBT.begin("TEMP_LED"); //Bluetooth device name
  Serial.println("Bluetooth enabled");
  pinMode(LED, OUTPUT);
  digitalWrite(LED, HIGH);
}

void loop() {
  // 接受蓝牙指令
  if (Serial.available()) {
    char cmd = Serial.read();
    Serial.print("I received: ");
    Serial.println(cmd);
    if (cmd == 'h'){
      digitalWrite(LED, HIGH);
      //Serial.println("The temperature now is hot");
    } else if (cmd == 's'){
      digitalWrite(LED, LOW);
      //erial.println("The temperature now is snog");
    } else if (cmd == 'c'){
      digitalWrite(LED, LOW);
      //Serial.println("The temperature now is cold");
    }
  }
    delay(20);
}
