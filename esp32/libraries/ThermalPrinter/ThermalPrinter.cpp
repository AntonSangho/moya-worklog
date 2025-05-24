#include "ThermalPrinter.h"
#include <stdarg.h>

ThermalPrinter::ThermalPrinter() {
    serial = nullptr;
    vendorId = 0;
    productId = 0;
    connected = false;
}

ThermalPrinter::~ThermalPrinter() {
    // Cleanup if needed
}

bool ThermalPrinter::begin(HardwareSerial& serialPort, uint32_t baudRate) {
    serial = &serialPort;
    serial->begin(baudRate);
    delay(100);
    
    reset();
    connected = true;
    return true;
}

bool ThermalPrinter::begin(uint16_t vid, uint16_t pid) {
    vendorId = vid;
    productId = pid;
    
    // For ESP32-P4, use Serial for USB communication
    serial = &Serial;
    if (!serial) {
        return false;
    }
    
    // Initialize USB communication
    serial->begin(115200);
    delay(500);
    
    reset();
    connected = detectPrinter();
    return connected;
}

bool ThermalPrinter::detectPrinter() {
    if (!serial) return false;
    
    // Send printer status request
    writeCommand(DLE, 0x04, 0x01);
    delay(100);
    
    // Check for response (simplified detection)
    if (serial->available() > 0) {
        // Clear any response
        while (serial->available()) {
            serial->read();
        }
        return true;
    }
    
    // Assume printer is connected if no error
    return true;
}

void ThermalPrinter::reset() {
    if (!serial) return;
    
    // ESC @ - Initialize printer
    writeCommand(ESC, '@');
    delay(100);
    
    // Set default settings
    setDensity(14);
    setBreakTime(4);
    resetFormatting();
}

void ThermalPrinter::writeBytes(const uint8_t* data, size_t length) {
    if (!serial || !connected) return;
    
    serial->write(data, length);
    serial->flush();
}

void ThermalPrinter::writeCommand(uint8_t cmd) {
    if (!serial || !connected) return;
    
    serial->write(cmd);
    serial->flush();
}

void ThermalPrinter::writeCommand(uint8_t cmd, uint8_t arg) {
    if (!serial || !connected) return;
    
    uint8_t buffer[] = {cmd, arg};
    writeBytes(buffer, 2);
}

void ThermalPrinter::writeCommand(uint8_t cmd, uint8_t arg1, uint8_t arg2) {
    if (!serial || !connected) return;
    
    uint8_t buffer[] = {cmd, arg1, arg2};
    writeBytes(buffer, 3);
}

void ThermalPrinter::writeCommand(uint8_t cmd, uint8_t arg1, uint8_t arg2, uint8_t arg3) {
    if (!serial || !connected) return;
    
    uint8_t buffer[] = {cmd, arg1, arg2, arg3};
    writeBytes(buffer, 4);
}

void ThermalPrinter::print(const char* text) {
    if (!serial || !connected || !text) return;
    
    serial->print(text);
    serial->flush();
}

void ThermalPrinter::print(const String& text) {
    print(text.c_str());
}

void ThermalPrinter::println(const char* text) {
    print(text);
    writeCommand(0x0A); // Line feed
}

void ThermalPrinter::println(const String& text) {
    println(text.c_str());
}

void ThermalPrinter::printf(const char* format, ...) {
    char buffer[512];
    va_list args;
    va_start(args, format);
    vsnprintf(buffer, sizeof(buffer), format, args);
    va_end(args);
    print(buffer);
}

void ThermalPrinter::setBold(bool enable) {
    writeCommand(ESC, 'E', enable ? 1 : 0);
}

void ThermalPrinter::setUnderline(bool enable) {
    writeCommand(ESC, '-', enable ? 1 : 0);
}

void ThermalPrinter::setDoubleHeight(bool enable) {
    if (enable) {
        writeCommand(ESC, '!', PRINT_MODE_DOUBLE_H);
    } else {
        writeCommand(ESC, '!', PRINT_MODE_NORMAL);
    }
}

void ThermalPrinter::setDoubleWidth(bool enable) {
    if (enable) {
        writeCommand(ESC, '!', PRINT_MODE_DOUBLE_W);
    } else {
        writeCommand(ESC, '!', PRINT_MODE_NORMAL);
    }
}

void ThermalPrinter::setTextSize(uint8_t size) {
    if (size < 1) size = 1;
    if (size > 8) size = 8;
    
    uint8_t sizeCmd = ((size - 1) << 4) | (size - 1);
    writeCommand(GS, '!', sizeCmd);
}

void ThermalPrinter::setAlignment(uint8_t alignment) {
    writeCommand(ESC, 'a', alignment);
}

void ThermalPrinter::setLineSpacing(uint8_t spacing) {
    writeCommand(ESC, '3', spacing);
}

void ThermalPrinter::resetFormatting() {
    writeCommand(ESC, '@'); // Reset all formatting
}

bool ThermalPrinter::printImage(const uint8_t* imageData, uint16_t width, uint16_t height) {
    if (!serial || !connected || !imageData) return false;
    
    // ESC/POS raster bit image command
    // GS v 0 mode width_low width_high height_low height_high data
    writeCommand(GS, 'v', '0');
    writeCommand(0x00); // Normal mode
    writeCommand(width & 0xFF);
    writeCommand((width >> 8) & 0xFF);
    writeCommand(height & 0xFF);
    writeCommand((height >> 8) & 0xFF);
    
    // Calculate bytes per line
    uint16_t bytesPerLine = (width + 7) / 8;
    uint32_t totalBytes = bytesPerLine * height;
    
    // Send image data
    writeBytes(imageData, totalBytes);
    
    // Add some feed after image
    feed(3);
    
    return true;
}

bool ThermalPrinter::printImageFromFile(const char* filename) {
    // This would need SPIFFS integration
    // For now, return false
    return false;
}

void ThermalPrinter::feed(uint8_t lines) {
    writeCommand(ESC, 'd', lines);
}

void ThermalPrinter::feedMm(uint8_t mm) {
    // Approximate: 1mm ≈ 8 dots for thermal printers
    uint8_t dots = mm * 8;
    writeCommand(ESC, 'J', dots);
}

void ThermalPrinter::cut(bool partial) {
    if (partial) {
        cutPartial();
    } else {
        cutFull();
    }
}

void ThermalPrinter::cutFull() {
    feed(3); // Feed before cut
    writeCommand(GS, 'V', 0x00);
}

void ThermalPrinter::cutPartial() {
    feed(3); // Feed before cut
    writeCommand(GS, 'V', 0x01);
}

bool ThermalPrinter::isConnected() {
    return connected;
}

void ThermalPrinter::printTestPage() {
    if (!connected) return;
    
    setAlignment(ALIGN_CENTER);
    setBold(true);
    println("=== MOYA WORKLOG TEST ===");
    setBold(false);
    println("");
    
    setAlignment(ALIGN_LEFT);
    println("Printer: Connected");
    printf("VID: 0x%04X\n", vendorId);
    printf("PID: 0x%04X\n", productId);
    println("");
    
    println("Font test:");
    setTextSize(1);
    println("Size 1: Normal text");
    setTextSize(2);
    println("Size 2: Bigger");
    setTextSize(1);
    
    println("");
    setBold(true);
    println("Bold text");
    setBold(false);
    setUnderline(true);
    println("Underlined text");
    resetFormatting();
    
    println("");
    setAlignment(ALIGN_CENTER);
    println("--- Test Complete ---");
    resetFormatting();
    
    feed(3);
    cut();
}

void ThermalPrinter::printSystemInfo() {
    if (!connected) return;
    
    setAlignment(ALIGN_CENTER);
    setBold(true);
    println("=== SYSTEM INFO ===");
    resetFormatting();
    
    setAlignment(ALIGN_LEFT);
    printf("Chip: %s\n", ESP.getChipModel());
    printf("CPU Freq: %d MHz\n", ESP.getCpuFreqMHz());
    printf("Flash: %d KB\n", ESP.getFlashChipSize() / 1024);
    printf("Free Heap: %d KB\n", ESP.getFreeHeap() / 1024);
    
    feed(2);
    cut();
}

uint8_t ThermalPrinter::getStatus() {
    if (!serial || !connected) return 0xFF;
    
    // Request printer status
    writeCommand(DLE, 0x04, 0x01);
    delay(50);
    
    if (serial->available()) {
        return serial->read();
    }
    
    return 0x00; // Assume OK if no response
}

void ThermalPrinter::printBarcode(const char* data, uint8_t type) {
    if (!data || !connected) return;
    
    // Set barcode height
    writeCommand(GS, 'h', 50);
    
    // Set barcode width
    writeCommand(GS, 'w', 2);
    
    // Print barcode
    writeCommand(GS, 'k', type);
    print(data);
    writeCommand(0x00); // Null terminator
}

void ThermalPrinter::printQR(const char* data, uint8_t size) {
    if (!data || !connected) return;
    
    // QR code implementation would go here
    // For now, print as text
    println("QR Code:");
    println(data);
}

void ThermalPrinter::setCharacterSet(uint8_t charset) {
    writeCommand(ESC, 'R', charset);
}

void ThermalPrinter::setCodePage(uint8_t codepage) {
    writeCommand(ESC, 't', codepage);
}

void ThermalPrinter::sleep() {
    writeCommand(ESC, '8', 1, 1, 1);
}

void ThermalPrinter::wake() {
    writeCommand(0xFF); // Wake up command
    delay(100);
    reset();
}

void ThermalPrinter::setDensity(uint8_t density) {
    if (density > 31) density = 31;
    
    uint8_t printDensity = density;
    uint8_t printBreakTime = 4; // Default break time
    
    writeCommand(0x12, '#', (printBreakTime << 5) | printDensity);
}

void ThermalPrinter::setBreakTime(uint8_t breakTime) {
    if (breakTime > 15) breakTime = 15;
    
    uint8_t printDensity = 14; // Default density
    writeCommand(0x12, '#', (breakTime << 5) | printDensity);
}