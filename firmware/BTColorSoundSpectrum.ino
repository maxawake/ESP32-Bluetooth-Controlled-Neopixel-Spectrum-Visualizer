#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>
#endif
#include "BluetoothSerial.h"

#define PIN 4
#define NUMPIXELS 144
#define NUMPIXELS_HALF 72

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
BluetoothSerial SerialBT;

int colors_left[NUMPIXELS_HALF][3] = {0};
int colors_right[NUMPIXELS_HALF][3] = {0};

void setup() {
    pixels.begin();
    Serial.begin(115200);
    SerialBT.begin("ESP32-BT-Slave");
    Serial.println("Bluetooth device started. You can pair it now!");
}

void updateColors(int red, int green, int blue) {
    // Shift left and right arrays
    for (int i = NUMPIXELS_HALF - 1; i > 0; i--) {
        memcpy(colors_left[i], colors_left[i - 1], sizeof(colors_left[i]));
        memcpy(colors_right[i], colors_right[i - 1], sizeof(colors_right[i]));
    }

    // Update center pixel colors
    colors_left[0][0] = colors_right[0][0] = red;
    colors_left[0][1] = colors_right[0][1] = green;
    colors_left[0][2] = colors_right[0][2] = blue;

    // Set pixel colors for LEDs
    for (int i = 0; i < NUMPIXELS_HALF; i++) {
        pixels.setPixelColor(i, pixels.Color(colors_left[NUMPIXELS_HALF - i - 1][0], colors_left[NUMPIXELS_HALF - i - 1][1], colors_left[NUMPIXELS_HALF - i - 1][2]));
        pixels.setPixelColor(i + NUMPIXELS_HALF, pixels.Color(colors_right[i][0], colors_right[i][1], colors_right[i][2]));
    }

    pixels.show();
}

void loop() {
    if (SerialBT.available()) {
        String inputString = SerialBT.readStringUntil('\n');
        int red = 0, green = 0, blue = 0;

        // Efficiently parse input using sscanf
        if (sscanf(inputString.c_str(), "%d %d %d", &red, &green, &blue) == 3) {
            updateColors(red, green, blue);
        }
    }
}
