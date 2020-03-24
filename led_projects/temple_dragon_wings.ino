#include <FastLED.h>


//*** Define constants ***//
// The input pin listening for synchronized heart rates
#define HEART_RATE_PIN 5

// LED data output pins; LEDs are arranged two mirrored strands per pin
// where the data wire is split into the two strands;
#define LED_PIN_1 6
#define LED_PIN_2 7
#define LED_PIN_3 8
#define LED_PIN_4 9
#define LED_PIN_5 10

// Total number of LEDs per strand
#define NUM_LEDS 100

// LED type
#define LED_TYPE WS2812

// Strand array memory allocation
CRGB leds_1[NUM_LEDS];
CRGB leds_2[NUM_LEDS];
CRGB leds_3[NUM_LEDS];
CRGB leds_4[NUM_LEDS];
CRGB leds_5[NUM_LEDS];


void setup() {
  pinMode(HEART_RATE_PIN, INPUT);
  
  pinMode(LED_PIN_1, OUTPUT);
  pinMode(LED_PIN_2, OUTPUT);
  pinMode(LED_PIN_3, OUTPUT);
  pinMode(LED_PIN_4, OUTPUT);
  pinMode(LED_PIN_5, OUTPUT);

  // Remember: 2 mirrored LED strands per pin!
  FastLED.addLeds<LED_TYPE, LED_PIN_1>(leds_1, NUM_LEDS);
//  FastLED.addLeds<LED_TYPE, LED_PIN_2>(leds_2, NUM_LEDS);
//  FastLED.addLeds<LED_TYPE, LED_PIN_3>(leds_3, NUM_LEDS);
//  FastLED.addLeds<LED_TYPE, LED_PIN_4>(leds_4, NUM_LEDS);
//  FastLED.addLeds<LED_TYPE, LED_PIN_5>(leds_5, NUM_LEDS);

  Serial.begin(9600);
}

void loop() {
  // 1 = syncrhonized; 0 = not synchronized; change to match your setup
  int heart_rate_sync;
  heart_rate_sync = 1;

  // Rainbow heartbeat constants
  int num_colors;
  num_colors = 5;
  int rainbow_heartbeat_colors[num_colors][3] = {
    {0, 0, 255},  // blue
    {102, 0, 102},  // purple
    {255, 0, 0},  // red
    {255, 153, 0},  // orange
    {255, 255, 0}  // yellow
  };
  
  // Check if heart rates are synchronized;
  if (digitalRead(HEART_RATE_PIN) == heart_rate_sync)
  {
    // jackpot
    Serial.print("Jackpot");
  }

  //*** Normal LED behavior loop ***//
  // Fire colors, pulsating
  rainbow_heartbeat(num_colors, rainbow_heartbeat_colors);

  // Sparkles followed by shooting lines of flame colors
  sparkle_flames();
}


// Fire colors (blue to yellow) pulsating like a heartbeat
void rainbow_heartbeat(int num_colors, int color_array[5][3])
{
  int brightness_factor, h, i, j, count;

  count = 0;

  // 50 heartbeats
  while (count < 5000) {
    for (h=1; h<101; h++) {
      for (i=1; i<num_colors+1; i++) {
        for (j=(NUM_LEDS/num_colors)*(i-1); j<(NUM_LEDS/num_colors)*i; j++)
        {
          if (h < 40) 
          {
            brightness_factor = 40 - h;
          } else if (h >= 40 && h < 50) {
            brightness_factor = h - 39;
          } else if (h >= 50 && h < 60) {
            brightness_factor = 60 - h;
          } else {
            brightness_factor = h - 59;
          }

          leds_1[j].red = color_array[i-1][0]/brightness_factor;
          leds_1[j].green = color_array[i-1][1]/brightness_factor;
          leds_1[j].blue = color_array[i-1][2]/brightness_factor;
          
// Uncomment as new LED strands are added
//          leds_2[j].red = color_array[i-1][0]/brightness_factor;
//          leds_2[j].green = color_array[i-1][1]/brightness_factor;
//          leds_2[j].blue = color_array[i-1][2]/brightness_factor;
//  
//          leds_3[j].red = color_array[i-1][0]/brightness_factor;
//          leds_3[j].green = color_array[i-1][1]/brightness_factor;
//          leds_3[j].blue = color_array[i-1][2]/brightness_factor;
//  
//          leds_4[j].red = color_array[i-1][0]/brightness_factor;
//          leds_4[j].green = color_array[i-1][1]/brightness_factor;
//          leds_4[j].blue = color_array[i-1][2]/brightness_factor;
//  
//          leds_5[j].red = color_array[i-1][0]/brightness_factor;
//          leds_5[j].green = color_array[i-1][1]/brightness_factor;
//          leds_5[j].blue = color_array[i-1][2]/brightness_factor;
        }
      }
      FastLED.show();
      delay(10);

      count += 1;
    }
  }
}


// Sparkles fading to flame-colored lines running up the wings randomly
void sparkle_flames(void)
{
  int i, count;
  int random_num_1, random_num_2, random_num_3, random_num_4, random_num_5;

  count = 0;

  // Sparkles for 500 sec
  while (count < 5000)
  {
    for (i=0; i<NUM_LEDS; i++) {
      random_num_1 = rand() % 2;
      random_num_2 = rand() % 2;
      random_num_3 = rand() % 2;
      random_num_4 = rand() % 2;
      random_num_5 = rand() % 2;
      
      if (random_num_1 == 1) {
        leds_1[i].setRGB(255, 255, 255);
      } else {
        leds_1[i].setRGB(0, 0, 0);
      }
      
// Uncomment as new LED strands are added
//
//      if (random_num_2 == 1) {
//        leds_2[i].setRGB(255, 255, 255);
//      } else {
//        leds_2[i].setRGB(0, 0, 0);
//      }
//
//
//      if (random_num_3 == 1) {
//        leds_3[i].setRGB(255, 255, 255);
//      } else {
//        leds_3[i].setRGB(0, 0, 0);
//      }
//
//      if (random_num_4 == 1) {
//        leds_4[i].setRGB(255, 255, 255);
//      } else {
//        leds_4[i].setRGB(0, 0, 0);
//      }
//
//      if (random_num_5 == 1 {
//        leds_5[i].setRGB(255, 255, 255);
//      } else {
//        leds_5[i].setRGB(0, 0, 0);
//      }
    }
    FastLED.show();
    delay(100);

    count += 1;
  }

  // Flame lines for 10 sec
  int flame_1_start, flame_2_start, flame_3_start, flame_4_start, flame_5_start;
  int flame_length, flame_end;
  flame_length = 10;

  // initialize flames
  flame_1_start = 90;
  flame_2_start = 0;
  flame_3_start = 50;
  flame_4_start = 20;
  flame_5_start = 70;

  // One minute
  count = 0;
  while (count < 6000) {
    // Strand 1
    flame_length = get_flame_length(flame_1_start, flame_length);
    if (flame_1_start == NUM_LEDS) {
      flame_1_start = 0;
    }
    flame_end = flame_1_start + flame_length;
    flame_1_start = progress_flame(flame_1_start, flame_end, leds_1, 255, 153, 0);
    
// Uncomment as new LED strands are added
//    // Strand 2
//    flame_length = get_flame_length(flame_2_start, flame_length);
//    if (flame_2_start == NUM_LEDS) {
//      flame_2_start = 0;
//    }
//    flame_end = flame_2_start + flame_length;
//    flame_2_start = progress_flame(flame_2_start, flame_end, leds_2, 255, 0, 0);
//
//    // Strand 3
//    flame_length = get_flame_length(flame_3_start, flame_length);
//    if (flame_3_start == NUM_LEDS) {
//      flame_3_start = 0;
//    }
//    flame_end = flame_3_start + flame_length;
//    flame_3_start = progress_flame(flame_3_start, flame_end, leds_3, 255, 255, 0);
//
//    // Strand 4
//    flame_length = get_flame_length(flame_4_start, flame_length);
//    if (flame_4_start == NUM_LEDS) {
//      flame_4_start = 0;
//    }
//    flame_end = flame_4_start + flame_length;
//    flame_4_start = progress_flame(flame_4_start, flame_end, leds_4, 255, 153, 0);
//
//    // Strand 5
//    flame_length = get_flame_length(flame_5_start, flame_length);
//    if (flame_5_start == NUM_LEDS) {
//      flame_5_start = 0;
//    }
//    flame_end = flame_5_start + flame_length;
//    flame_5_start = progress_flame(flame_5_start, flame_end, leds_5, 255, 255, 0);
    FastLED.show();
    delay(10);
    count += 1;
  }
}

int get_flame_length(int flame_start, int flame_length) {
  if (flame_start == NUM_LEDS) {
    flame_length = 1;
  } else if (flame_length < 10) {
    flame_length += 1;
  } else if ((flame_start + flame_length) >= NUM_LEDS) {
    flame_length = ((flame_start + flame_length) + 1) - NUM_LEDS;
  }

  return flame_length;
}

int progress_flame(int flame_start, int flame_end, CRGB leds[NUM_LEDS], int r, int g, int b) {
  int i;
  
  for (i=0; i < NUM_LEDS; i ++) {
    if (i >= flame_start && i < flame_end) {
      leds_1[i].setRGB(r, g, b);
    } else {
      leds_1[i].setRGB(0, 0, 0);
    }
  }

  flame_start += 1;
  
  return flame_start;
}


