int dl=400;
bool lightOn = false;
bool fanOn = false;

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
  Serial.print("|");
  Serial.print(vd5);
  Serial.print("|");
  Serial.print(lightOn ? "true" : "false");
  Serial.print("|");
  Serial.print(fanOn ? "true" : "false");
  Serial.println();  

  digitalWrite(D6, fanOn ? LOW : HIGH);
  digitalWrite(D7, lightOn ? HIGH : LOW);

  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    if (command.endsWith("fan")) {
      fanOn = command.startsWith("s");
    }

    if (command.endsWith("light")) {
      lightOn = command.startsWith("s");
    }
  }
  
  delay(dl);
}
