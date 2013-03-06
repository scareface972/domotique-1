//Include for Xbee library -> http://code.google.com/p/xbee-arduino/
#include <XBee.h>

//Definition of the pin used in program
const int _OutPinBuz = 9;
const int _OutPinLed4 = 10;
const int _InPinButton4 = 11;
const int _InPinFireDetection = 8;
const int _InPinLedMeasure = A0;

//Global variables
XBee _Xbee = XBee(); //Create Xbee object to control a Xbee
ZBRxResponse _ZbRxResp = ZBRxResponse(); //Create reusable response objects for responses we expect to handle

int _CurrentLightValue = 0;
int _CmdReceived = 0;
int _DataToSend = 0;

void flashPin(int pin, int times, int wait) 
{
  for (int i = 0; i < times; i++) {
    digitalWrite(pin, HIGH);
    delay(wait);
    digitalWrite(pin, LOW);

    if (i + 1 < times) {
      delay(wait);
    }
  }
}

void setup() 
{
  // start serial port
  Serial.begin(9600);
  // start serial
  _Xbee.begin(9600);
  
  pinMode(_OutPinLed4, OUTPUT);
  pinMode(_OutPinBuz, OUTPUT);
  
  pinMode(_InPinButton4,INPUT);
  pinMode(_InPinFireDetection,INPUT);
  
}

// continuously reads packets, looking for ZB Receive or Modem Status
void loop() {
  //Reset command to 0
  _CmdReceived = 0;
  _DataToSend = 0;

  //Read if we received an inoming message
  _Xbee.readPacket();
  if (_Xbee.getResponse().isAvailable()) {
    Serial.println("We have something on the serial");
    Serial.print("ApiId: 0x");
    Serial.println(_Xbee.getResponse().getApiId(), HEX);

    if (_Xbee.getResponse().getApiId() == ZB_RX_RESPONSE) {
      Serial.println("This is a ZB response");
      _Xbee.getResponse().getZBRxResponse(_ZbRxResp);
      _CmdReceived = _ZbRxResp.getData(0);
      Serial.print("Data0: 0x");
      Serial.println(_CmdReceived, HEX);
    }  
  }
  
  int aInputDigitalValue = digitalRead(_InPinFireDetection);

  if (aInputDigitalValue == HIGH)
  {
  flashPin(_OutPinBuz, 1, 250);
  }

  //Test if we have an action to do 
  if(_CmdReceived==4)
  {
    flashPin(_OutPinLed4, 1, 250);
  }
  else if(_CmdReceived==5)
  {
    _DataToSend=analogRead(_InPinLedMeasure);
	_DataToSend=456;
  }
  else
  {
    //Serial.print("Nothing to do...");
  }
    if(_DataToSend!=0)
  {
    uint8_t aPayload[3];

	aPayload[0] = _CmdReceived; //LSB
    Serial.print("Data0: 0x");
    Serial.println(aPayload[0], HEX);
    aPayload[1] = _DataToSend & 0xff; //LSB
    Serial.print("Data1: 0x");
    Serial.println(aPayload[1], HEX);
    aPayload[2] = (_DataToSend >> 8) & 0xff; //MSB
    Serial.print("Data2: 0x");
    Serial.println(aPayload[2], HEX);

    // Specify the address of the remote XBee (this is the SH + SL)
    XBeeAddress64 aAddr64 = XBeeAddress64(0x0013a200, 0x400a3e5e);

    // Create a TX Request
    ZBTxRequest aZbTx = ZBTxRequest(aAddr64, aPayload, sizeof(aPayload));

    // Send your request
    _Xbee.send(aZbTx);

    Serial.println("Message has been sent");

    if (_Xbee.readPacket(5000)) {
      Serial.println("We got a response to the message");

      // should be a znet tx status  

      ZBTxStatusResponse aZbTxStatus = ZBTxStatusResponse();        
      if (_Xbee.getResponse().getApiId() == ZB_TX_STATUS_RESPONSE) {
        Serial.println("It is a transmition status");
        _Xbee.getResponse().getZBTxStatusResponse(aZbTxStatus);

        // get the delivery status, the fifth byte
        if (aZbTxStatus.getDeliveryStatus() == SUCCESS) {
          Serial.println("The Trx was OK");
        } 
        else {
          Serial.println("Warning : The Trx was KO");
        }
      } 
      else{
        Serial.print("It was not a Trx status. ApiId:");
        Serial.println(_Xbee.getResponse().getApiId());
      }   
    } 
    else {
      Serial.println("Warning : This should never happen");
    }
  }
}
