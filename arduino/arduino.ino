#include <WiFiS3.h>
#include <SPI.h>
#include <MFRC522.h>
#include <DHT.h>
#include <Adafruit_NeoPixel.h>

// ======================================================
//  PIN DEFINITIONS
// ======================================================
#define DHTPIN        2
#define DHTTYPE       DHT11

#define LED_PIN       6        // WS2812 strip
#define LED_COUNT     40       // use first 20 LEDs

// Ultrasonic
#define ULTRA_TRIG    9
#define ULTRA_ECHO    10

// Wind Sensor (Modern Device Rev C)
#define WIND_RV_PIN   A1
#define WIND_TMP_PIN  A0

// ======================================================
//  OBJECTS
// ======================================================
DHT dht(DHTPIN, DHTTYPE);
Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Idle animation control
unsigned long lastIdle = 0;
uint8_t idlePhase = 0;
bool inStoryMode = false;  // Flag to disable idle animation during story


// ======================================================
//  BASIC HELPERS
// ======================================================

void setLED(int r, int g, int b) {
  r = constrain(r,0,255);
  g = constrain(g,0,255);
  b = constrain(b,0,255);

  Serial.print("🔴 setLED called: R=");
  Serial.print(r);
  Serial.print(" G=");
  Serial.print(g);
  Serial.print(" B=");
  Serial.println(b);

  for(int i=0; i<LED_COUNT; i++){
    strip.setPixelColor(i, strip.Color(r,g,b));
  }
  strip.show();
  
  Serial.println("✅ strip.show() completed");
}

void handleColorCommand(String cmd){
  Serial.print("📨 Received COLOR command: ");
  Serial.println(cmd);
  
  int bar = cmd.indexOf('|');
  if(bar<0) {
    Serial.println("❌ ERROR: No | found in command");
    return;
  }

  String rgb = cmd.substring(bar+1);
  Serial.print("📋 RGB string: ");
  Serial.println(rgb);
  
  int c1 = rgb.indexOf(',');
  int c2 = rgb.indexOf(',', c1+1);
  if(c1<0 || c2<0) {
    Serial.println("❌ ERROR: Commas not found in RGB string");
    return;
  }

  int r = rgb.substring(0,c1).toInt();
  int g = rgb.substring(c1+1,c2).toInt();
  int b = rgb.substring(c2+1).toInt();

  Serial.print("🎨 Parsed values: R=");
  Serial.print(r);
  Serial.print(" G=");
  Serial.print(g);
  Serial.print(" B=");
  Serial.println(b);

  inStoryMode = true;  // Disable idle animation
  setLED(r,g,b);
}

// ======================================================
//  IDLE LED BREATHING EFFECT
// ======================================================
void idleAnimation(){
  if(inStoryMode) return;  // Don't run during story
  
  unsigned long now = millis();
  if(now - lastIdle < 25) return;
  lastIdle = now;

  idlePhase++;
  float f = idlePhase / 255.0f;

  float bright = (f < 0.5f) ? (2*f*f) : (1 - 2*(1-f)*(1-f));
  uint8_t val = bright * 80;

  setLED(0, val, val+30);
}


// ======================================================
//  WIND SENSOR CALCULATION
// ======================================================
float readWindMPH(float &tempC) {

  int TMP_raw = analogRead(WIND_TMP_PIN);
  int RV_raw  = analogRead(WIND_RV_PIN);

  float RV_volts = RV_raw * 0.0048828125;

  float TempCtimes100 = 
      0.005 * ((float)TMP_raw * TMP_raw)
      - 16.862 * TMP_raw
      + 9075.4;

  tempC = TempCtimes100 / 100.0;

  float zeroWind = 
    -0.0006 * (TMP_raw * TMP_raw)
    + 1.0727 * TMP_raw
    + 47.172;

  float zeroWind_volts = zeroWind * 0.0048828125 - 0.2;

  float windMPH = pow(((RV_volts - zeroWind_volts) / 0.2300), 2.7265);
  if (windMPH < 0) windMPH = 0;

  return windMPH;
}


// ======================================================
//  ULTRASONIC WATER DEPTH
// ======================================================
long readUltrasonicCM(){
  digitalWrite(ULTRA_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(ULTRA_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRA_TRIG, LOW);

  long duration = pulseIn(ULTRA_ECHO, HIGH, 40000);
  if(duration == 0) return -1;

  long cm = duration / 29 / 2;
  return cm;
}


// ======================================================
//   SEND MEASUREMENTS TO PYTHON
// ======================================================
void sendEnvironment(){
  Serial.println("📊 Reading sensors...");
  
  float t = dht.readTemperature();
  float h = dht.readHumidity();

  float tWind;
  float windMPH = readWindMPH(tWind);

  long depth = readUltrasonicCM();

  Serial.print("ENV|T=");
  if(isnan(t)) Serial.print("nan"); else Serial.print(t,1);

  Serial.print("|H=");
  if(isnan(h)) Serial.print("nan"); else Serial.print(h,1);

  Serial.print("|DEPTH=");
  Serial.print(depth);

  Serial.print("|WIND=");
  Serial.println(windMPH,1);
}


// ======================================================
//  SETUP
// ======================================================
void setup() {
  Serial.begin(115200);
  while(!Serial){}

  Serial.println("🚀 Starting StoryBox...");

  dht.begin();

  pinMode(ULTRA_TRIG, OUTPUT);
  pinMode(ULTRA_ECHO, INPUT);

  Serial.println("💡 Initializing LED strip...");
  strip.begin();
  strip.setBrightness(255);
  strip.show();
  
  Serial.println("🧪 Testing LED strip with startup sequence...");
  
  // Startup test: Red
  Serial.println("Test 1: RED");
  setLED(255, 0, 0);
  delay(500);
  
  // Startup test: Green
  Serial.println("Test 2: GREEN");
  setLED(0, 255, 0);
  delay(500);
  
  // Startup test: Blue
  Serial.println("Test 3: BLUE");
  setLED(0, 0, 255);
  delay(500);
  
  // Off
  Serial.println("Test 4: OFF");
  setLED(0, 0, 0);

  Serial.println("✅ StoryBox Sensor Node Ready");
  Serial.println("📡 Commands: MEASURE | COLOR|R,G,B | OFF");
  Serial.println("Waiting for commands...");
}


// ======================================================
//  LOOP
// ======================================================
void loop(){

  // Incoming Python commands
  if(Serial.available()){
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    Serial.print("📥 Command received: '");
    Serial.print(cmd);
    Serial.println("'");

    if(cmd.equalsIgnoreCase("MEASURE")){
      inStoryMode = false;  // Re-enable idle mode after measurement
      sendEnvironment();
    }
    else if(cmd.startsWith("COLOR|")){
      handleColorCommand(cmd);
    }
    else if(cmd.equalsIgnoreCase("OFF")){
      Serial.println("🔴 Turning LEDs OFF");
      inStoryMode = false;
      setLED(0,0,0);
    }
    else {
      Serial.print("❓ Unknown command: "); 
      Serial.println(cmd);
    }
  }

  // Only run idle animation when not in story mode
  idleAnimation();
}