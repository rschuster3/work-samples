#include <stdio.h> 
#include <stdlib.h> 
#include<time.h>
#include <FastLED.h>


//*** Define constants ***//

// LED data output pin and clock
#define LED_PIN_1 9

// Sparkfun redboard = 19, arduino uno = 13
#define CLK_PIN 13

// Total number of 12V LED strands
#define NUM_LEDS 10  // 30

// LEDs per pentagon facce
#define NUM_SUBFACES 5  // 6

// Pentagon faces
#define NUM_FACES 2 // 5

// Number of brightness factors
#define NUM_FACTORS 10
int FACTORS[NUM_FACTORS]{0, 26, 51, 77, 102, 128, 154, 179, 205, 230};

// Filler index
#define FILLER 99

// LED type
//#define LED_TYPE WS2812
#define LED_TYPE WS2801

// Strand array memory allocation
CRGB leds_1[NUM_LEDS];

// Empty array of len NUM_LEDs
#define fake_array[NUM_LEDS]

// Map LEDs to a 2D grid layout; e.g. leds_1[MAP_ARR[0][0]]
#define ROWS 5
#define COLS 9
int MAP_ARR[ROWS][COLS]{
  {99, 23, 19, 29, 25, 99, 99, 99, 99},
  {99, 22, 18, 20, 28, 24, 26, 99, 99},
  {99, 13, 21, 7, 27, 1, 99, 99, 99},
  {17, 12, 14, 11, 6, 8, 5, 0, 2},
  {99, 16, 15, 10, 9, 4, 3, 99, 99}
};


void setup() {  
  pinMode(LED_PIN_1, OUTPUT);

  FastLED.addLeds<LED_TYPE, LED_PIN_1, CLK_PIN, RGB, DATA_RATE_KHZ(250)>(leds_1, NUM_LEDS);
  //FastLED.addLeds<LED_TYPE, LED_PIN_1>(leds_1, NUM_LEDS);

  Serial.begin(9600);
}


void loop() {
  //sweep_l2r();
  //sweep_r2l();
  //sweep_t2b();
  //sweep_b2t();
  
  //randomly_show_faces();
  randomly_show_individuals();
  randomly_show_groups();
}



// Given an two arrays of large faces and small faces, give the corresponding
// LED array indexes in order when those face arrays are iterated over.
int *get_led_indexes(int large_face_array[NUM_FACES], int sub_face_array[NUM_SUBFACES], int boolean_flag) {
  int *led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
  int i, j, led_index;

  for (i=0; i < NUM_FACES; i++) {
    for (j=0; j < NUM_SUBFACES; j++) {
      led_index = (NUM_SUBFACES * i) + j;

      if (boolean_flag)
      {
        if (large_face_array[i] == 1 && sub_face_array[j] == 1) {
          led_indexes[led_index] = led_index;
        } else {
          led_indexes[led_index] = FILLER;
        }
      } else {
        led_indexes[led_index] = large_face_array[i]*NUM_SUBFACES + sub_face_array[j];
      }
    }
  }

  return led_indexes;
}


// Colors
int COLOR_INDEX = 0;
const int NUM_COLORS = 10;
const int NUM_SCHEMES = 4;

// Color schemes. Each 2D array is a single color (R, G, or B).
// Each row in each array represents a different color scheme.
int R[NUM_SCHEMES][NUM_COLORS]{
  {128, 102, 255, 255, 255, 121, 255, 179, 191, 255},  // Air
  {128, 255, 204, 230, 255, 255, 255, 204, 255, 128},  // Fire
  {0, 0, 0, 0, 204, 204, 0, 0, 0, 0},  // Forest
  {0, 51, 0, 0, 0, 0, 0, 0, 51, 0}  // Water
};
int G[NUM_SCHEMES][NUM_COLORS]{
  {255, 255, 153, 255, 102, 166, 204, 255, 128, 184},  // Air
  {0, 0, 92, 115, 204, 204, 115, 82, 0, 0},  // Fire
  {51, 102, 153, 204, 255, 255, 204, 153, 102, 51}, // Forest
  {51, 102, 153, 153, 255, 255, 153, 153, 102, 51}  // Water
};
int B[NUM_SCHEMES][NUM_COLORS]{
  {255, 153, 255, 77, 102, 210, 102, 102, 255, 77},  // Air
  {0, 0, 0, 0, 0, 0, 0, 0, 0, 0},  // Fire
  {0, 0, 0, 102, 102, 102, 102, 0, 0, 0},  // Forest
  {153, 204, 204, 255, 255, 255, 255, 204, 204, 153}  // Water
};

// Randomly pick a color scheme row number
int get_color_scheme(){
  return rand() % ((NUM_SCHEMES - 1) + 1);
}


// Fade in and out
void fade_in_and_out(int fade_in_led_indexes[NUM_LEDS], int fade_out_led_indexes[NUM_LEDS], int fade_in_only, int scheme)
{
  int i, j, last_color_index, last_r, last_g, last_b, r, g, b;

  // Set current color index after getting the last one
  last_color_index = COLOR_INDEX;
  if (COLOR_INDEX == NUM_COLORS - 1){
    COLOR_INDEX = 0;
  } else {
    COLOR_INDEX += 1;
  }

  // Current colors
  r = R[scheme][COLOR_INDEX];
  g = G[scheme][COLOR_INDEX];
  b = B[scheme][COLOR_INDEX];

  // Last round of colors
  last_r = R[scheme][last_color_index];
  last_g = G[scheme][last_color_index];
  last_b = B[scheme][last_color_index];

  for (i=0; i < NUM_FACTORS; i++) {
    clear_leds();
    
    for (j=0; j < NUM_LEDS; j++) {
      // Fade in next set of LEDs with the current color
      if (fade_in_led_indexes[j] < FILLER) {
        leds_1[fade_in_led_indexes[j]].setRGB(r, g, b).fadeLightBy(230 - FACTORS[i]);
      }
      // Fade out last set of LEDs with the last color
      if (fade_in_only == 0 && fade_out_led_indexes[j] < FILLER) {
        leds_1[fade_out_led_indexes[j]].setRGB(last_r, last_g, last_b).fadeLightBy(FACTORS[i]);
      }
    }

    FastLED.show();
    delay(100);
  }
}


void iterate_leds(int led_indexes[NUM_LEDS])
{
  int i, j, fade_in_only;
  int scheme = get_color_scheme();
    
  for (i=0; i < NUM_LEDS; i++)
  {
    // Declare arrays of LED indexes
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    // Fill LED index arrays with filler ints
    for (j=0; j < NUM_LEDS; j++) {
      new_led_indexes[j] = FILLER;
      old_led_indexes[j] = FILLER;
    }
    
    // The LED index from the current loop
    new_led_indexes[led_indexes[i]] = led_indexes[i];

    // LED index from the last loop, if this isn't
    // the first loop.
    if (i > 0) {
      old_led_indexes[led_indexes[i-1]] = led_indexes[i-1];
    }
    
    // If this is the first index, we only need to fade in the first
    // LED index. No fade out necessary. Otherwise, we want
    // to also fade out the last LED index.
    if (i > 0) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }
    
    // Do the fade in/out and free memory for the next sets of indexes
    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
    free(new_led_indexes);
    free(old_led_indexes);
  }
}

// Show one random LED strand at a time until all strands
// are shown.
void randomly_show_individuals()
{
  int *large_face_array = (int*)malloc(sizeof(int) * NUM_FACES);
  int *sub_face_array = (int*)malloc(sizeof(int) * NUM_SUBFACES);
  int *led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
  
  large_face_array = generate_face_array(0, NUM_FACES);
  sub_face_array = generate_face_array(0, NUM_SUBFACES);
  led_indexes = get_led_indexes(large_face_array, sub_face_array, 0);
  iterate_leds(led_indexes);
  
  free(large_face_array);
  free(sub_face_array);
  free(led_indexes);
}


// Show a random group of LED strands at a time; run NUM_LED times.
void randomly_show_groups()
{
  int i, fade_in_only;
  int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
  int scheme = get_color_scheme();
  
  for (i=0; i < NUM_LEDS; i++)
  {
    int *large_face_array = (int*)malloc(sizeof(int) * NUM_FACES);
    int *sub_face_array = (int*)malloc(sizeof(int) * NUM_SUBFACES);
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    large_face_array = generate_face_array(1, NUM_FACES);
    sub_face_array = generate_face_array(1, NUM_SUBFACES);
    new_led_indexes = get_led_indexes(large_face_array, sub_face_array, 1);  // This takes care of filler

    if (i > 0) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }

    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);   

    // Generate old LED array, which is the same as the current new array
    free(old_led_indexes);
    old_led_indexes = get_led_indexes(large_face_array, sub_face_array, 1);
    
    free(large_face_array);
    free(sub_face_array);
    free(new_led_indexes);
  }
  free (old_led_indexes);
}


//// Show entire large faces one at a time randomly.
//void randomly_show_faces()
//{
//  int i, fade_in_only;
//  int scheme = get_color_scheme();
//  int new_large_face_array[NUM_FACES] = {0, 0, 0, 0, 0};
//  int old_large_face_array[NUM_FACES] = {0, 0, 0, 0, 0};
//  int sub_face_array[NUM_SUBFACES] = {1, 1, 1, 1, 1, 1};
//
//  for (i=0; i < NUM_FACES; i++)
//  {
//    // Declare arrays of LED indexes
//    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
//    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
//
//    // "Turn on" the correct faces
//    new_large_face_array[i] = 1;
//    fade_in_only = 1;
//    if (i > 0)
//    {
//      new_large_face_array[i-1] = 0;
//      old_large_face_array[i-1] = 1;
//      fade_in_only = 0;
//    }
//    if (i > 1) {
//      old_large_face_array[i-2] = 0;
//    }
//    
//    new_led_indexes = get_led_indexes(new_large_face_array, sub_face_array, 1);
//    old_led_indexes = get_led_indexes(old_large_face_array, sub_face_array, 1);
//
//    // Do the fade in/out and free memory for the next sets of indexes
//    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
//    free(new_led_indexes);
//    free(old_led_indexes);
//  }
//}

// Set LEDs to black
void clear_leds()
{
  int i;
  
  for (i=0; i < NUM_LEDS; i++) {
    leds_1[i].setRGB(0, 0, 0);
  }
}

// General purpose fcn for generating a large face array [0:4] or
// a sub face array [0:5] either with numbered indexes or booleans.
int *generate_face_array(int boolean_flag, int num_faces)
{
  int *face_array = (int*)malloc(sizeof(int) * num_faces);
  int i, t, j;
  
  if (boolean_flag) {
    // Create array of booleans num_faces long
    for (i=0; i < num_faces; i++) {
      face_array[i] = rand() % 2;
    }
  } else {
    // Create array of randonmly shuffled face numbers
    for (i=0; i < num_faces; i++)
    {
      face_array[i] = i;
    }
    for (i = 0; i < num_faces; i++) 
    {
      j = i + rand() / (RAND_MAX / (num_faces - i) + 1);
      t = face_array[j];
      face_array[j] = face_array[i];
      face_array[i] = t;
    }
  }

  return face_array;
}


// Sweep left to right
void sweep_l2r()
{
  int i, j, fade_in_only;
  int scheme = get_color_scheme();

  for (j=0; j < COLS; j++) {
    // Declare arrays of LED indexes
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    // Fill LED index arrays with filler ints
    for (i=0; i < NUM_LEDS; i++) {
      new_led_indexes[i] = FILLER;
      old_led_indexes[i] = FILLER;
    }

    // "Turn on" the LEDs we want by assigning them their index
    for (i=0; i < ROWS; i++) {
      // These are LED indexes from the current loop that we want to
      // fade in.
      if (MAP_ARR[i][j] < FILLER) {
        new_led_indexes[MAP_ARR[i][j]] = MAP_ARR[i][j];
      }
      
      // These are LED indexes from the last loop that we want to
      // fade out.
      if (j > 0 && MAP_ARR[i][j-1] < FILLER) {
        old_led_indexes[MAP_ARR[i][j-1]] = MAP_ARR[i][j-1];
      }
    }

    // If this is the first row, we only need to fade in the first
    // set of LED indexes. No fade out necessary. Otherwise, we want
    // to also fade out the last set of LED indexes.
    if (j > 0) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }

    // Do the fade in/out and free memory for the next sets of indexes
    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
    free(new_led_indexes);
    free(old_led_indexes);
  }
}

// Sweep right to left
void sweep_r2l()
{
  int i, j, fade_in_only;
  int scheme = get_color_scheme();

  for (j=COLS - 1; j > -1; j--) {
    // Declare arrays of LED indexes
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    // Fill LED index arrays with filler ints
    for (i=0; i < NUM_LEDS; i++) {
      new_led_indexes[i] = FILLER;
      old_led_indexes[i] = FILLER;
    }

    // "Turn on" the LEDs we want by assigning them their index
    for (i=0; i < ROWS; i++) {
      // These are LED indexes from the current loop that we want to
      // fade in.
      if (MAP_ARR[i][j] < FILLER) {
        new_led_indexes[MAP_ARR[i][j]] = MAP_ARR[i][j];
      }
      
      // These are LED indexes from the last loop that we want to
      // fade out.
      if (j < COLS - 1 && MAP_ARR[i][j+1] < FILLER) {
        old_led_indexes[MAP_ARR[i][j+1]] = MAP_ARR[i][j+1];
      }
    }

    // If this is the first row, we only need to fade in the first
    // set of LED indexes. No fade out necessary. Otherwise, we want
    // to also fade out the last set of LED indexes.
    if (j < COLS - 1) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }

    // Do the fade in/out and free memory for the next sets of indexes
    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
    free(new_led_indexes);
    free(old_led_indexes);
  }
}

// Sweep top to bottom
void sweep_t2b()
{
  int i, j, fade_in_only;
  int scheme = get_color_scheme();

  for (i=0; i < ROWS; i++) {
    // Declare arrays of LED indexes
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    // Fill LED index arrays with filler ints
    for (j=0; j < NUM_LEDS; j++) {
      new_led_indexes[j] = FILLER;
      old_led_indexes[j] = FILLER;
    }

    // "Turn on" the LEDs we want by assigning them their index
    for (j=0; j < COLS; j++) {
      // These are LED indexes from the current loop that we want to
      // fade in.
      if (MAP_ARR[i][j] < FILLER) {
        new_led_indexes[MAP_ARR[i][j]] = MAP_ARR[i][j];
      }

      // These are LED indexes from the last loop that we want to
      // fade out.
      if (i > 0 && MAP_ARR[i-1][j] < FILLER) {
        old_led_indexes[MAP_ARR[i-1][j]] = MAP_ARR[i-1][j];
      }
    }

    // If this is the first row, we only need to fade in the first
    // set of LED indexes. No fade out necessary. Otherwise, we want
    // to also fade out the last set of LED indexes.
    if (i > 0) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }

    // Do the fade in/out and free memory for the next sets of indexes
    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
    free(new_led_indexes);
    free(old_led_indexes);
  }
}

// Sweep bottom to top
void sweep_b2t()
{
  int i, j, fade_in_only;
  int scheme = get_color_scheme();

  for (i=ROWS-1; i > -1; i--) {
    // Declare arrays of LED indexes
    int *new_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);
    int *old_led_indexes = (int*)malloc(sizeof(int) * NUM_LEDS);

    // Fill LED index arrays with filler ints
    for (j=0; j < NUM_LEDS; j++) {
      new_led_indexes[j] = FILLER;
      old_led_indexes[j] = FILLER;
    }

    // "Turn on" the LEDs we want by assigning them their index
    for (j=0; j < COLS; j++) {
      // These are LED indexes from the current loop that we want to
      // fade in.
      if (MAP_ARR[i][j] < FILLER) {
        new_led_indexes[MAP_ARR[i][j]] = MAP_ARR[i][j];
      }

      // These are LED indexes from the last loop that we want to
      // fade out.
      if (i < ROWS - 1 && MAP_ARR[i+1][j] < FILLER) {
        old_led_indexes[MAP_ARR[i+1][j]] = MAP_ARR[i+1][j];
      }
    }

    // If this is the first row, we only need to fade in the first
    // set of LED indexes. No fade out necessary. Otherwise, we want
    // to also fade out the last set of LED indexes.
    if (i < ROWS - 1) {
      fade_in_only = 0;
    } else {
      fade_in_only = 1;
    }

    // Do the fade in/out and free memory for the next sets of indexes
    fade_in_and_out(new_led_indexes, old_led_indexes, fade_in_only, scheme);
    free(new_led_indexes);
    free(old_led_indexes);
  }
}
