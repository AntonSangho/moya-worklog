#include <WiFi.h>
#include <SPIFFS.h>
#include <ESPAsyncWebServer.h>
#include <FS.h>
#include <USB.h>
#include <USBCDC.h>
#include <ArduinoJson.h>
#include <vector>
#include <random>

// Pin definitions for ESP32-P4-Nano
const int PRINT_BUTTON_PIN = 21;
const int LED_STATUS_PIN = 2;
const int RESET_BUTTON_PIN = 3;

// Printer USB VID/PID (Sam4s Giant 100 and Bixolon)
const uint16_t SAM4S_VID = 0x1c8a;
const uint16_t SAM4S_PID = 0x3a0e;
const uint16_t BIXOLON_VID = 0x1504;
const uint16_t BIXOLON_PID = 0x006e;

// Image settings
const int IMG_WIDTH = 480;
const int IMG_HEIGHT = 1000;
const int DEBOUNCE_TIME = 2000;

// Global variables
volatile bool printRequested = false;
volatile unsigned long lastButtonPress = 0;
int printCount = 0;
std::vector<String> imageFiles;
std::mt19937 rng(esp_random());

// ESC/POS Commands
const uint8_t ESC = 0x1B;
const uint8_t GS = 0x1D;

// ESC/POS command sequences
const uint8_t CMD_INIT[] = {ESC, '@'};
const uint8_t CMD_CUT[] = {GS, 'V', 0x00};
const uint8_t CMD_FEED[] = {ESC, 'd', 0x03};

class ThermalPrinter {
private:
  bool printerConnected = false;
  uint16_t vid, pid;
  
public:
  ThermalPrinter() : vid(0), pid(0) {}
  
  bool init() {
    // Try to detect connected printer
    if (detectPrinter()) {
      printerConnected = true;
      // Initialize printer
      sendCommand(CMD_INIT, sizeof(CMD_INIT));
      delay(100);
      return true;
    }
    return false;
  }
  
  bool detectPrinter() {
    // This would need USB Host implementation
    // For now, assume Sam4s is connected
    vid = SAM4S_VID;
    pid = SAM4S_PID;
    return true;
  }
  
  void sendCommand(const uint8_t* cmd, size_t len) {
    if (printerConnected) {
      // Send via USB CDC (Serial)
      Serial.write(cmd, len);
      Serial.flush();
    }
  }
  
  void printText(const char* text) {
    if (printerConnected) {
      Serial.print(text);
      Serial.flush();
    }
  }
  
  void printImage(const uint8_t* imageData, int width, int height) {
    if (!printerConnected) return;
    
    // ESC/POS raster bit image command
    uint8_t cmd[] = {GS, 'v', '0', 0x00, 
                     (uint8_t)(width & 0xFF), (uint8_t)((width >> 8) & 0xFF),
                     (uint8_t)(height & 0xFF), (uint8_t)((height >> 8) & 0xFF)};
    
    sendCommand(cmd, sizeof(cmd));
    
    // Send image data
    int bytesPerLine = (width + 7) / 8;
    for (int y = 0; y < height; y++) {
      for (int x = 0; x < bytesPerLine; x++) {
        int byteIndex = y * bytesPerLine + x;
        if (byteIndex < (bytesPerLine * height)) {
          Serial.write(imageData[byteIndex]);
        }
      }
    }
    Serial.flush();
  }
  
  void cut() {
    sendCommand(CMD_CUT, sizeof(CMD_CUT));
    sendCommand(CMD_FEED, sizeof(CMD_FEED));
  }
};

ThermalPrinter printer;

void IRAM_ATTR buttonISR() {
  unsigned long currentTime = millis();
  if (currentTime - lastButtonPress > DEBOUNCE_TIME) {
    printRequested = true;
    lastButtonPress = currentTime;
  }
}

void setupGPIO() {
  pinMode(PRINT_BUTTON_PIN, INPUT_PULLDOWN);
  pinMode(LED_STATUS_PIN, OUTPUT);
  pinMode(RESET_BUTTON_PIN, INPUT_PULLUP);
  
  attachInterrupt(digitalPinToInterrupt(PRINT_BUTTON_PIN), buttonISR, RISING);
  
  digitalWrite(LED_STATUS_PIN, HIGH);
  delay(1000);
}

bool initSPIFFS() {
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS Mount Failed");
    return false;
  }
  
  Serial.println("SPIFFS mounted successfully");
  return true;
}

void loadImageList() {
  imageFiles.clear();
  
  // Add image files (these should be stored in SPIFFS)
  imageFiles.push_back("/w1_2022.bin");
  imageFiles.push_back("/w2_2022.bin");
  imageFiles.push_back("/w3_2022.bin");
  imageFiles.push_back("/w4_2022.bin");
  imageFiles.push_back("/w5_2022.bin");
  
  Serial.printf("Loaded %d image files\n", imageFiles.size());
}

uint8_t* loadImageFromSPIFFS(const String& filename, size_t& dataSize) {
  File file = SPIFFS.open(filename, "r");
  if (!file) {
    Serial.printf("Failed to open %s\n", filename.c_str());
    return nullptr;
  }
  
  dataSize = file.size();
  uint8_t* data = (uint8_t*)malloc(dataSize);
  
  if (data && file.readBytes((char*)data, dataSize) == dataSize) {
    file.close();
    return data;
  }
  
  if (data) free(data);
  file.close();
  return nullptr;
}

void printRandomImage() {
  if (imageFiles.empty()) {
    Serial.println("No images available");
    return;
  }
  
  // Select random image
  std::uniform_int_distribution<int> dist(0, imageFiles.size() - 1);
  int randomIndex = dist(rng);
  String selectedFile = imageFiles[randomIndex];
  
  Serial.printf("Printing image: %s\n", selectedFile.c_str());
  
  // Load image data
  size_t dataSize;
  uint8_t* imageData = loadImageFromSPIFFS(selectedFile, dataSize);
  
  if (imageData) {
    // Print the image
    printer.printImage(imageData, IMG_WIDTH, IMG_HEIGHT);
    printer.cut();
    
    free(imageData);
    printCount++;
    
    Serial.printf("Print completed. Total prints: %d\n", printCount);
  } else {
    Serial.printf("Failed to load image: %s\n", selectedFile.c_str());
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("Moya Worklog ESP32 Starting...");
  
  setupGPIO();
  
  if (!initSPIFFS()) {
    Serial.println("Critical: SPIFFS init failed");
    return;
  }
  
  loadImageList();
  
  if (!printer.init()) {
    Serial.println("Warning: Printer not detected");
  } else {
    Serial.println("Printer initialized successfully");
  }
  
  Serial.println("System ready. Press button to print worklog.");
}

void loop() {
  if (printRequested) {
    printRequested = false;
    
    digitalWrite(LED_STATUS_PIN, LOW);
    printRandomImage();
    digitalWrite(LED_STATUS_PIN, HIGH);
  }
  
  // Check for reset button
  if (digitalRead(RESET_BUTTON_PIN) == LOW) {
    Serial.println("Reset button pressed");
    ESP.restart();
  }
  
  delay(100);
}