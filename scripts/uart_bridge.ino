/*
  UART <-> USB bridge sketch for the communication
  between Grover radar connected to Arduino and PC.
*/

void setup()
{
  delay(1000);
  SerialUSB.begin(115200);
  Serial1.begin(115200);
}

void loop()
{
  if(SerialUSB.available()){
    Serial1.write(SerialUSB.read());
  }

  if(Serial1.available()){
    SerialUSB.write(Serial1.read());
  }
}