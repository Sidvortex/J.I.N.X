#include <TFT_eSPI.h>

TFT_eSPI tft;

void displayInit() {
    tft.init();
    tft.setRotation(1);
    tft.fillScreen(TFT_BLACK);
}

void displayEmotion(String state) {

    uint16_t color = TFT_WHITE;

    if(state=="ALERT") color=TFT_RED;
    if(state=="ACTIVE") color=TFT_GREEN;
    if(state=="SLEEP") color=TFT_BLUE;

    tft.fillScreen(TFT_BLACK);

    tft.fillCircle(90,120,35,color);
    tft.fillCircle(230,120,35,color);
}