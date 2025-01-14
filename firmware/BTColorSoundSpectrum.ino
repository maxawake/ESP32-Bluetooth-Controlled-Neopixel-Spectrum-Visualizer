#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif
#include "BluetoothSerial.h"

String device_name = "ESP32-BT-Slave";

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#if !defined(CONFIG_BT_SPP_ENABLED)
#error Serial Bluetooth not available or not enabled. It is only available for the ESP32 chip.
#endif


#define MIN_PIXEL_RANGE 0
#define MAX_PIXEL_RANGE 143

#define NUMPIXELS_HALF 72

// Which pin on the Arduino is connected to the NeoPixels?
#define PIN 4 

// How many NeoPixels are attached to the Arduino?
#define NUMPIXELS 144

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);

int colors_left[NUMPIXELS_HALF][3] = {0};
int colors_right[NUMPIXELS_HALF][3] = {0};

String inputString = "0 0 0\n";

BluetoothSerial SerialBT;

void setup()
{
    // put your setup code here, to run once:
    pixels.begin();
    Serial.begin(115200);
    SerialBT.begin(device_name); //Bluetooth device name
    Serial.printf("The device with name \"%s\" is started.\nNow you can pair it with Bluetooth!\n", device_name.c_str());
}


String getValue(String data, char separator, int index)
{
    int found = 0;
    int strIndex[] = { 0, -1 };
    int maxIndex = data.length() - 1;

    for (int i = 0; i <= maxIndex && found <= index; i++) {
        if (data.charAt(i) == separator || i == maxIndex) {
            found++;
            strIndex[0] = strIndex[1] + 1;
            strIndex[1] = (i == maxIndex) ? i+1 : i;
        }
    }
    return found > index ? data.substring(strIndex[0], strIndex[1]) : "";
}


void loop()
{       
        if (SerialBT.available()) {
            inputString = SerialBT.readStringUntil('\n');
            //Serial.println(inputString);

            String red_s = getValue(inputString, ' ', 0);
            String green_s = getValue(inputString, ' ', 1);
            String blue_s = getValue(inputString, ' ', 2); 
    
            int red = red_s.toInt();
            int green = green_s.toInt();
            int blue = blue_s.toInt();

            Serial.printf("red: \"%i\"", red);
            Serial.printf("green: \"%i\"", blue);
            Serial.printf("blue: \"%i\"", green);
            Serial.print("\n");

            // FROM THE MIDDLE
            colors_left[0][0] = red;
            colors_left[0][1] = green;
            colors_left[0][2] = blue;

            colors_right[0][0] = red;
            colors_right[0][1] = green;
            colors_right[0][2] = blue;

            for (int i=NUMPIXELS_HALF-1; i>0; i--) {              
              colors_left[i][0] = colors_left[i-1][0];
              colors_left[i][1] = colors_left[i-1][1];
              colors_left[i][2] = colors_left[i-1][2];
            }

            for (int i=NUMPIXELS_HALF-1; i>0; i--) {              
              colors_right[i][0] = colors_right[i-1][0];
              colors_right[i][1] = colors_right[i-1][1];
              colors_right[i][2] = colors_right[i-1][2];
            }
            
            for (int i=0; i<NUMPIXELS_HALF; i++) {
               pixels.setPixelColor(i, colors_left[NUMPIXELS_HALF-i-1][0], colors_left[NUMPIXELS_HALF-i-1][1], colors_left[NUMPIXELS_HALF-i-1][2]);
            }

            for (int i=0; i<NUMPIXELS_HALF; i++) {
               pixels.setPixelColor(i + NUMPIXELS_HALF, colors_right[i][0], colors_right[i][1], colors_right[i][2]);
            }

            pixels.show();

            inputString = "0 0 0\n";

            // LEFT TO RIGHT
            /*colors[0][0]=red;
            colors[0][1]=green;
            colors[0][2]=blue;

            for(int i=NUMPIXELS-1; i>0; i--) { 
                colors[i][0] = colors[i-1][0];
                colors[i][1] = colors[i-1][1];
                colors[i][2] = colors[i-1][2];
            }
    
            
            for (int i=0; i<NUMPIXELS; i++) {
               pixels.setPixelColor(i, colors[i][0], colors[i][1], colors[i][2]);
               /*Serial.printf("index: \"%i\"", i);
               Serial.printf("red: \"%i\"", colors[i][0]);
               Serial.printf("green: \"%i\"", colors[i][1]);
               Serial.printf("blue: \"%i\"", colors[i][2]);
               Serial.print("\n");
               //pixels.show();
            }*/

            // FIXED COLOR
            /*pixels.fill(pixels.Color(red, green, blue));*/
        }
}
