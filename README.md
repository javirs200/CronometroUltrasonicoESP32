# Ultrasonic Stopwatch for ESP32

A high-precision ultrasonic stopwatch running on the **ESP32 microcontroller**, featuring Bluetooth connectivity and configurable measurement modes. Designed for timing miniZ racecars across indoor home circuits, home rally stages, and competitive racing courses with accurate lap timing and checkpoint measurements.

**Original project:** Based on [CronometroUltrasonico](https://github.com/javirs200/CronometroUltrasonico), adapted and optimized for ESP32.

---

## Overview

This project provides a standalone, portable ultrasonic timing solution with the following capabilities:
- **Ultrasonic Sensing:** Precise time measurement using a single ultrasonic sensor to detect racecars
- **Bluetooth Communication:** Real-time data transmission and remote control via BLE
- **Configurable Parameters:** Adjust sensor behavior and timing modes via Bluetooth console
- **Internal Storage:** Flash memory storage for measurement results when offline
- **Multiple Measurement Modes:** Support for various timing scenarios

---

## Original Source

This project evolved from the [AzureContainersApp](https://github.com/javirs200/AzureContainersApp) repository (esp32files branch), which was refactored into this dedicated, standalone ESP32 application.

---

## Project Status

### ✅ Completed Features
- Removed dependencies: WiFi, socket communication, RFID reader
- Refactored logic functions for modularity and performance
- Bluetooth Serial Console communication
- Configurable parameters via Bluetooth
- New time measurement logic implementation
- Multiple measurement modes
- Code refactored as standalone ESP32 project

### 🔄 In Progress
- Code optimization and testing

### ⏳ Planned Features
- Internal flash memory storage of results
- Standalone operation mode (start without Bluetooth after power-on delay)
- Optional Bluetooth requirement (fallback to offline mode after timeout)

---

## Project Structure

```
Esp32Files/
├── boot.py              # Entry point configuration
└── hadware/
    ├── bluetooth.py     # Bluetooth communication module
    ├── leds.py          # LED control module
    └── ultrasonic.py    # Single ultrasonic sensor interface
```

---

## Dependencies

- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble) - MicroPython Bluetooth Low Energy library

---