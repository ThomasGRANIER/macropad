const int buttonPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10};     // Pins réels
const int buttonMap[]  = {8, 9, 10, 5, 6, 7, 2, 3, 4};     // Pins câblés inversés
const int numButtons = sizeof(buttonPins) / sizeof(buttonPins[0]);

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonMap[i], INPUT_PULLUP);
  }
}

void loop() {
  for (int i = 0; i < numButtons; i++) {
    if (digitalRead(buttonMap[i]) == LOW) {
      int row = i / 3 + 1;       // Ligne (1 ou 2)
      int col = i % 3 + 1;       // Colonne (1 à 3)
      Serial.print("l");
      Serial.print(row);
      Serial.print("c");
      Serial.println(col);
      delay(300);
    }
  }
}
