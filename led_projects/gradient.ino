#include <Adafruit_NeoPixel.h>
// ######################################//
// ## NeoPixel Variables ## //
// ######################################//
// the data pin for the NeoPixels
int neoPixelPin1 = 21;
int neoPixelPin2 = 20;
//int neoPixelPin3 = 19;

// How many NeoPixels we will be using, charge accordingly
int NUM_PIXELS = 16;

// Keeps track of what pixel we're on for animated dipslays
int START_PIXEL = 0;

// Instatiate the NeoPixel from the ibrary
Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(NUM_PIXELS, neoPixelPin1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(NUM_PIXELS, neoPixelPin2, NEO_GRB + NEO_KHZ800);
//Adafruit_NeoPixel strip3 = Adafruit_NeoPixel(NUM_PIXELS, neoPixelPin3, NEO_GRB + NEO_KHZ800);

// Put lighting fixures in an array
const int NUM_FIXTURES = 2;
Adafruit_NeoPixel fixtures[NUM_FIXTURES] = {strip1, strip2};//, strip3};

// ######################################//
// ## Lighting Effect Variables ## //
// ######################################//
const int NUM_BUTTONS = 2;

// Button pins
int BUTTONS[NUM_BUTTONS] = {9, 10};

// Keep track of what button was pressed
boolean BUTTON_PRESSED[NUM_BUTTONS] = {false, false};

// Gradient color schemes
int COLOR_SCHEMES[NUM_BUTTONS][2][3] = {
  {{105, 51, 0}, {120, 180, 0}},  // FOREST
  {{153, 0, 204}, {204, 51, 0}}  // SUNSET
};

// Brightness array
int MAX_BRIGHTNESS_DIFF = 255;
int MIN_BRIGHTNESS_DIFF = 0;
int BRIGHTNESS_INC = 1;
int FIXTURE_BRIGHTNESS_DIFF[NUM_FIXTURES] = {
  MAX_BRIGHTNESS_DIFF,
  MAX_BRIGHTNESS_DIFF
};
bool BRIGHTNESS_INCREASING[NUM_FIXTURES] = {false, false};

// ######################################//
// ## Layered Effect Timing Variables ## //
// ######################################//
// Animated gradient effect
#define GRADIENT_DELAY_TIME (15)
unsigned long GRADIENT_START_TIME;

// Staggered fixture effect
#define FIXTURE_DELAY_TIME (2000)
unsigned long FIXTURE_START_TIME;

// Brightness effect
#define BRIGHTNESS_DELAY_TIME (10)
unsigned long BRIGHTNESS_START_TIME;

// Which lighting fixture are we lighting up now?
int ON_FIXTURE;


// ######################################//
// ## Start Program ## //
// ######################################//
void setup() {
  for (int i=0; i < NUM_BUTTONS; i++) {
    pinMode(BUTTONS[i], INPUT);
  }
  
  // Initialize start times of lighting effects
  GRADIENT_START_TIME = millis();
  FIXTURE_START_TIME = millis();
  BRIGHTNESS_START_TIME = millis();

  init_fixtures();
  set_button_press(0);
}


void loop() {
  int current_button;
  
  for (int i=0; i < NUM_BUTTONS; i++) {
    // This fires when a button is pressed.
    if (digitalRead(BUTTONS[i]) == LOW) {
      // Note what button was pressed
      set_button_press(i);

      // Turn all the lights off
      all_off();

      // Reset effects
      START_PIXEL = 0;  // Gradient effect
      ON_FIXTURE = 0;  // Staggered fixture effect
      for (int j=0; j < NUM_FIXTURES; j++) { // Brightness effect
        FIXTURE_BRIGHTNESS_DIFF[j] = MAX_BRIGHTNESS_DIFF;
        BRIGHTNESS_INCREASING[j] = false;
      }
      FIXTURE_START_TIME = millis();
    }

    // Get the current button
    if (BUTTON_PRESSED[i] == true) {
      current_button = i;
    }
  }

  if (FIXTURE_START_TIME + FIXTURE_DELAY_TIME < millis()) {
    if (ON_FIXTURE < NUM_FIXTURES - 1) {
      ON_FIXTURE ++;
      FIXTURE_BRIGHTNESS_DIFF[ON_FIXTURE] = MAX_BRIGHTNESS_DIFF;
      BRIGHTNESS_INCREASING[ON_FIXTURE] = false;
    }

    FIXTURE_START_TIME = millis();
  }

  if (BRIGHTNESS_START_TIME + BRIGHTNESS_DELAY_TIME < millis()) {
    update_brightness();
    BRIGHTNESS_START_TIME = millis();
  }

  if (GRADIENT_START_TIME + GRADIENT_DELAY_TIME < millis()) {
    activate(COLOR_SCHEMES[current_button]);
    GRADIENT_START_TIME = millis();
  }
}


void init_fixtures() {  
  for (int i = 0; i < NUM_FIXTURES; i++) {
    fixtures[i].begin();  // initialize the strip
    fixtures[i].show();  // make sure it is visible
    fixtures[i].clear();  // Initialize all pixels to 'off'
  }
}


void all_off() {
  for (int i = 0; i < NUM_FIXTURES; i++) {
    fixtures[i].clear();
    fixtures[i].show();
  }
}


void set_button_press(int button_index){
  // Given an index, set that button to true and all
  // other buttons to false
  for (int i = 0; i < NUM_BUTTONS; i++) {
    if (i == button_index) {
      BUTTON_PRESSED[i] = true;
    } else {
      BUTTON_PRESSED[i] = false;
    }
  }
}


void update_brightness() {
  // Update the global fixture brightness
  for (int j=0; j < NUM_FIXTURES; j++){
    if (!BRIGHTNESS_INCREASING[j]) {
      if (FIXTURE_BRIGHTNESS_DIFF[j] < MAX_BRIGHTNESS_DIFF) {
        FIXTURE_BRIGHTNESS_DIFF[j] ++;
     } else if (FIXTURE_BRIGHTNESS_DIFF[j] == MAX_BRIGHTNESS_DIFF) {
        BRIGHTNESS_INCREASING[j] = true;
      }
    } else if (BRIGHTNESS_INCREASING[j]) {
      if (FIXTURE_BRIGHTNESS_DIFF[j] > MIN_BRIGHTNESS_DIFF) {
        FIXTURE_BRIGHTNESS_DIFF[j] --;
      } else if (FIXTURE_BRIGHTNESS_DIFF[j] == MIN_BRIGHTNESS_DIFF) {
        BRIGHTNESS_INCREASING[j] = false;
      }
    }
  }
}


void activate(int rgb_edge_values[2][3]) {
  // sp is a local variable that will be the actual
  // first pixel that we write to.
  int sp = START_PIXEL;

  // RGB values of the two colors on either side of
  // the gradient.
  int r1 = rgb_edge_values[0][0];
  int r2 = rgb_edge_values[1][0];
  int g1 = rgb_edge_values[0][1];
  int g2 = rgb_edge_values[1][1];
  int b1 = rgb_edge_values[0][2];
  int b2 = rgb_edge_values[1][2];

  int r, g, b;

  // Get RGB values at all points in the gradient and
  // assign them to the pixels in the strip.
  for (int i = 0; i < NUM_PIXELS; i++) {
    r = calculate_rgb_value(r1, r2, i);
    g = calculate_rgb_value(g1, g2, i);
    b = calculate_rgb_value(b1, b2, i);

    // Set light colors on the fixture if it's on
    for (int j = 0; j < NUM_FIXTURES; j++) {
      if (j <= ON_FIXTURE) {
        int brightness_diff = FIXTURE_BRIGHTNESS_DIFF[j];
        int adj_r = r - brightness_diff;
        int adj_g = g - brightness_diff;
        int adj_b = b - brightness_diff;

        // Adjust negative values to 0
        if (adj_r < 0) { adj_r = 0; }
        if (adj_g < 0) { adj_g = 0; }
        if (adj_b < 0) { adj_b = 0; }

        fixtures[j].setPixelColor(sp, adj_r, adj_g, adj_b);
      }
    }

    // Reset current pixel number if we've reached
    // the end of the strips.
    if (sp == NUM_PIXELS) {
      sp = 0;
    } else {
      sp++;
    }
  }

  // Turn the fixtures on one at a time
  for (int i = 0; i < NUM_FIXTURES; i++) {
    if (i <= ON_FIXTURE) {
      fixtures[i].show();
    }
  }
      
  // This is an animated gradient, so increment one pixel
  // for the next step.
  START_PIXEL++;
  if (START_PIXEL == NUM_PIXELS) {
    START_PIXEL = 0;
  }
}


int calculate_rgb_value(int v1, int v2, int i) {
  // Get RGB value at some point in a gradient between
  // two colors.
  int v;
  double diff;

  diff = floor((double)abs(v2 - v1) / (double)NUM_PIXELS);
   
  if (v2 > v1) {
    v = v1 + (i * diff);
  } else {
    v = v1 - (i * diff);
  }

  return v;
}


// Potential gradient combinations:
// # (153, 0, 204) --> (204, 51, 0)  purple and orange (sunset)
// # (255, 255, 255) --> (27, 115, 172)  blue and white (clouds)
// # (51, 204, 204) --> (255, 102, 0) teal and orange (sunset)
// # (92, 0, 230) --> (255, 0, 102) blue/purple and pink/red (passion?)
// # (102, 51, 0) --> (120, 180, 0) green and brown (forest)
// # (255, 30, 0) --> (255, 150, 0) red/yellow and orange (fire)
// # (0, 150, 70) --> (0, 153, 153) blue and blue/green (water)
