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

### backlog
- at moment Bluetooth communication is mandatry , add option for start without bluetooth at certaun time after power on. 
- if no bluetooth connection after x seconds, store results in internal flash memory.

### New features to be added:
- add bluetooth Serial Console communication - done
- configurable parameters via bluetooth - done
- new time measurement logic - done
- new measurement modes implementation - done
- add internal flash memory storage of results - pending
- add option for start without bluetooth connection - pending

## External libaries
- [aioble](https://github.com/micropython/micropython-lib/tree/master/micropython/bluetooth/aioble)
