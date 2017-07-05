#include <ArduinoJson.h>
#include <ESP8266httpUpdate.h> // For Server OTA
#include <ESP8266WiFi.h>          //https://github.com/esp8266/Arduino
//needed for library
#include <DNSServer.h>
#include <ESP8266WebServer.h>
#include <WiFiManager.h>         //https://github.com/tzapu/WiFiManager
#include <SPI.h> 
#include <Wire.h>
#include "PixySPI_SS.h"
#include <WebSocketsClient.h>

String* camID;
uint16_t blocks;
uint16_t old_blocks;

PixySPI_SS pixy(D8);

int counter=0;
char buf[10];
unsigned long timedelay =0;

String macadress = "";
IPAddress ip;
String strIP;
bool wifiConnectFailed = false;
WebSocketsClient webSocket;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t lenght) {


    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            {
                Serial.printf("[WSc] Connected to url: %s\n",  payload);
                StaticJsonBuffer<200> jsonBuffer;
                JsonObject& clientType =jsonBuffer.createObject();
                clientType["type"] = String("camera"); //make simple JSON object containing client type
                char buffer[100];
                clientType.printTo(buffer);
                webSocket.sendTXT(buffer); //send JSON 
          // send message to server when Connected
        //webSocket.sendTXT("Connected");
            }
            break;
        case WStype_TEXT:
            //Serial.printf("[WSc] get text: %s\n", payload);
            //camID = (payload);
      // send message to server
      // webSocket.sendTXT("message here");
            break;
        case WStype_BIN:
            Serial.printf("[WSc] get binary lenght: %u\n", lenght);
            hexdump(payload, lenght);

            // send data to server
            // webSocket.sendBIN(payload, lenght);
            break;
    }

}

void setup() {
  // put your setup code here, to run once:
    delay(6000);
    Serial.begin(9600);
    Serial.println("VR SYSTEM alpha V0.01");
  
  // Initialize camera
    pixy.init();

    byte mac[6];
    WiFi.macAddress(mac);
    char macadd[7];
    for(int i=0; i<6; i++){
        macadd[i] = (char)mac[i];
    }
    macadress = String(macadd[0],HEX) + String(macadd[1],HEX) + String(macadd[2],HEX) + String(macadd[3],HEX) + String(macadd[4],HEX) + String(macadd[5],HEX);


//
// DynamicJsonBuffer  jsonBuffer;
    
    WiFiManager wifiManager;
    //wifiConnectFailed = true; 
    //wifiManager.resetSettings();
    wifiManager.autoConnect("VR Tracker CAMERA", "vrtracker");
    Serial.println("Wifi connection established");

    /*char* buffer;
    ip = WiFi.localIP();
    sprintf(buffer,"%d:%d:%d:%d", ip[0],ip[1],ip[2],ip[3]);*/
    
    strIP = WiFi.gatewayIP().toString();
    Serial.println("My IP : " + WiFi.localIP().toString());
    Serial.println("Gateway IP : " + strIP);

    webSocket.begin("vr.gateway", 8001);
    webSocket.onEvent(webSocketEvent); 
}

void loop() {
  webSocket.loop();
  old_blocks = blocks;
  blocks = pixy.getBlocks();
  counter += 1;
    //////////////////////////////////////////
// Memory pool for JSON object tree.
// Inside the brackets, 200 is the size of the pool in bytes.
// If the JSON object is more complex, you need to increase that value.
  StaticJsonBuffer<1424> jsonBuffer;
// StaticJsonBuffer allocates memory on the stack, it can be
// replaced by DynamicJsonBuffer which allocates in the heap.
// It's simpler but less efficient.
// Create the root of the object tree.
//
// It's a reference to the JsonObject, the actual bytes are inside the
// JsonBuffer with all the other nodes of the object tree.
// Memory is freed when jsonBuffer goes out of scope.
  JsonObject& root = jsonBuffer.createObject();
  
// Add values in the object
//
// Most of the time, you can rely on the implicit casts.
// In other case, you can do root.set<long>("time", 1351824120);  
  root["type"] = String("point2D");
  root["frame"] = counter;
  JsonArray& blobs = root.createNestedArray("blobs");
///////////////////////////////////////////
//Look for new Blocks & Add to Array root
  if (blocks && (old_blocks != blocks))
  { 
      for (int j=0; j<blocks; j++)
      {  
      //if(pixy.blocks[j].width < 30 && pixy.blocks[j].height < 30){
        JsonObject& data = blobs.createNestedObject();
        data["sig"] = pixy.blocks[j].signature;
        data["xloc"] = pixy.blocks[j].x;
        data["yloc"] = pixy.blocks[j].y;
        data["width"] = pixy.blocks[j].width;
        data["height"] = pixy.blocks[j].height;
      //}
      } 
      char buffer[1000]; //Be sure your buffer is large enough to hold the string
      root.printTo(buffer); //sizeof(buffer)); write the json object to the string
      webSocket.sendTXT(buffer); //pass the string to websocket's function  
      //root.prettyPrintTo(Serial);
  }  
  
  else {
      delayMicroseconds(20);
} 
}
