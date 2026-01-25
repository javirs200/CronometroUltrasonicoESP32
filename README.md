# CronometroUltrasonicoESP32
based on the repository: [CronometroUltrasonico](https://github.com/javirs200/CronometroUltrasonico) but adapted for ESP32 microcontroller.
ESP32 code for ultrasonic crono (with bluetooth later)

## Descripcion
This project is a simple ultrasonic stopwatch using an ESP32 microcontroller. It measures the time taken to a moving object to pass between ultrasonic sensor.

## Reference Code
The initial code is taken from my repository [AzureContainersApp](https://github.com/javirs200/AzureContainersApp) esp32files branch
and refactored to Standalone ESP32 project.

## Planed changes
### Changes from the original AzureContainersApp repository:
- remove wifi conections - done
- remove socket communications - done
- remove rfid reader - done
### Redo logic of time measurement 
- move logic functions - done
- refactor code - in progress 
- add bluetooth communication - done
### New features to be added:
- add bluetooth Serial Console communication - done
- configurable parameters via bluetooth - done
- new time measurement logic - in progress

## External libaries
- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble)
