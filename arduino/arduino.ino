int dl=400;
String command;

void setup() { 
  Serial.begin(9600);  
  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
}

void loop() {
  digitalWrite(D4, LOW);
  digitalWrite(D5, HIGH);
  delay(dl);
  
  int vd5 = analogRead(A0);
  
  digitalWrite(D4, HIGH);
  digitalWrite(D5, LOW);
  delay(dl);
  
  int vd4 = analogRead(A0);
  
  Serial.print(vd4);
  Serial.print(" - ");
  Serial.print(vd5);
  Serial.println();

  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    if (command.endsWith("fan")) {
      if (!command.startsWith("r"))
        digitalWrite(D6, HIGH);
      else
        digitalWrite(D6, LOW);
    }

    if (command.endsWith("light")) {
      if (!command.startsWith("r"))
        digitalWrite(D7, HIGH);
      else
        digitalWrite(D7, LOW);
    }
  }
  
  delay(dl);
}
