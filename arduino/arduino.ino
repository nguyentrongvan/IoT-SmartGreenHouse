void setup() { 
  Serial.begin(9600);  
  pinMode(D1, INPUT);
}
void loop() {
  int moisture = analogRead(A0);
  int temperature = digitalRead(D1);
  Serial.print(moisture);
  Serial.print(" - ");
  Serial.print(temperature);
  Serial.println();
  
  delay(500);
}
