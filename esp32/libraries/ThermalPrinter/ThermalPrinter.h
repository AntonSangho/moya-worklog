#ifndef THERMAL_PRINTER_H
#define THERMAL_PRINTER_H

#include <Arduino.h>
#include <HardwareSerial.h>
#include <USB.h>

// Printer vendor/product IDs
#define SAM4S_VID 0x1c8a
#define SAM4S_PID 0x3a0e
#define BIXOLON_VID 0x1504
#define BIXOLON_PID 0x006e

// ESC/POS Commands
#define ESC 0x1B
#define GS  0x1D
#define FS  0x1C
#define DLE 0x10

// Print modes
#define PRINT_MODE_NORMAL    0x00
#define PRINT_MODE_DOUBLE_H  0x10
#define PRINT_MODE_DOUBLE_W  0x20
#define PRINT_MODE_BOLD      0x08
#define PRINT_MODE_UNDERLINE 0x80

// Text alignment
#define ALIGN_LEFT   0x00
#define ALIGN_CENTER 0x01
#define ALIGN_RIGHT  0x02

class ThermalPrinter {
private:
    HardwareSerial* serial;
    uint16_t vendorId;
    uint16_t productId;
    bool connected;
    
    // Internal command helpers
    void writeBytes(const uint8_t* data, size_t length);
    void writeCommand(uint8_t cmd);
    void writeCommand(uint8_t cmd, uint8_t arg);
    void writeCommand(uint8_t cmd, uint8_t arg1, uint8_t arg2);
    void writeCommand(uint8_t cmd, uint8_t arg1, uint8_t arg2, uint8_t arg3);

public:
    ThermalPrinter();
    ~ThermalPrinter();
    
    // Initialization
    bool begin(HardwareSerial& serialPort, uint32_t baudRate = 9600);
    bool begin(uint16_t vid = SAM4S_VID, uint16_t pid = SAM4S_PID);
    bool detectPrinter();
    void reset();
    
    // Basic printing
    void print(const char* text);
    void print(const String& text);
    void println(const char* text);
    void println(const String& text);
    void printf(const char* format, ...);
    
    // Text formatting
    void setBold(bool enable = true);
    void setUnderline(bool enable = true);
    void setDoubleHeight(bool enable = true);
    void setDoubleWidth(bool enable = true);
    void setTextSize(uint8_t size = 1); // 1-8
    void setAlignment(uint8_t alignment);
    void setLineSpacing(uint8_t spacing = 32);
    void resetFormatting();
    
    // Image printing
    bool printImage(const uint8_t* imageData, uint16_t width, uint16_t height);
    bool printImageFromFile(const char* filename);
    
    // Paper control
    void feed(uint8_t lines = 1);
    void feedMm(uint8_t mm);
    void cut(bool partial = false);
    void cutFull();
    void cutPartial();
    
    // Status and control
    bool isConnected();
    void printTestPage();
    void printSystemInfo();
    uint8_t getStatus();
    
    // Advanced features
    void printBarcode(const char* data, uint8_t type = 73); // Code128
    void printQR(const char* data, uint8_t size = 3);
    void setCharacterSet(uint8_t charset = 0);
    void setCodePage(uint8_t codepage = 0);
    
    // Power management
    void sleep();
    void wake();
    void setDensity(uint8_t density = 14); // 0-31
    void setBreakTime(uint8_t breakTime = 4); // 0-15
};

#endif // THERMAL_PRINTER_H