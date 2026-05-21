#define OUTPUT_PIN 4

void setup() {
  pinMode(OUTPUT_PIN, OUTPUT);
}

void loop(){
  digitalWrite(OUTPUT_PIN, HIGH);
  delay(250);
  
  digitalWrite(OUTPUT_PIN, LOW);
  delay(250);  
}
