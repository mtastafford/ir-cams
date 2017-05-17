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

uint16_t blocks;

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
        
          // send message to server when Connected
        webSocket.sendTXT("Connected");
            }
            break;
        case WStype_TEXT:
            Serial.printf("[WSc] get text: %s\n", payload);

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

    webSocket.begin("192.168.1.8", 8001);
    
webSocket.onEvent(webSocketEvent); 
}

void loop() {
  webSocket.loop();
  static int i = 0;
  int j;
  char buf[32]; 
  
  // grab blocks!
  blocks = pixy.getBlocks();
  // If there are detect blocks, print them!
  if (blocks)
  {
    i++;
    
    // do this (print) every 50 frames because printing every
    // frame would bog down the Arduino
    if (i%50==0)
    {
      sprintf(buf, "Detected %d:\n", blocks);
      Serial.print(buf);
      for (j=0; j<blocks; j++)
      {
        sprintf(buf, "  block %d: ", j);
        Serial.print(buf); 
        pixy.blocks[j].print();
      }
    }
  }  
}
