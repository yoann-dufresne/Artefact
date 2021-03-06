#include <EEPROM.h>

// 3 char ID
#define TRUE 42
#define FALSE (!42)
#define BOOL char

#define EEPROM_ID_ADDRESS 0

// Functions definitions :
void connection ();
void _connection ();


BOOL connected = FALSE;
char ledPin = 13;

void setup() {
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  connection();
}


void loop () {
  Serial.println("connected");
  delay (5000);
}

void serialFlush(){
  while(Serial.available() > 0) {
    char t = Serial.read();
  }
} 

void connection () {
  connected = FALSE;
  char ARDUINO_ID = EEPROM.read(EEPROM_ID_ADDRESS);

  // Connection
  while(!connected){
    serialFlush();
    connected = _connection(ARDUINO_ID);
    serialFlush();
  }
}  
  
BOOL _connection(char ARDUINO_ID){
  BOOL connected = FALSE; 
  int retry = 0;
  
  while (retry < 10 || connected) {
    retry++;
    BOOL part1 = FALSE;
    
    /*
    STEP 1 : wait for PC initial message
    */
    while (!Serial.available() && !part1) {
      char init_message = Serial.read();
      if(init_message == 'A')
        part1 = TRUE;
    }    
    
    
    /*
    STEP 2 : send protocol version and ID to PC
    */
    delay (1000);
    Serial.print("connection_protocol v0.0.1 ");
    Serial.println(ARDUINO_ID);

    delay(10);

    /*
    STEP 3: receive back ID and if ID is correct
    */
    BOOL response_ok = FALSE;
    while (!Serial.available()) {
      char pc_response = Serial.read();
      Serial.println(pc_response);
      if(pc_response!=ARDUINO_ID)
        response_ok = FALSE;
      else
        response_ok = TRUE;
    }
    if (!response_ok)
      continue;
    
    /*
    STEP 4: send CONNECTED string to finalize
    */
    Serial.println("CONNECTED");
    connected = TRUE;  
  }
  
  // turn the LED on when connected
  digitalWrite(ledPin, HIGH);
  return connected;
}
