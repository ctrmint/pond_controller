# Pond Pico Controller
## About
A Raspberry Pico based controller for a pond.  
The controller provides an API for specific tasks or readings based on connected hardware.  The connected hardware must be built and connected for the software to operate correctly.   Details of the hardware are described below. 
The API has been designed in a RESTful manner, with specific consideration of Home Assistant as a client, thus enabling the integration of the controller into Home Assistant.
 
## Requirements

### Hardware
The following hardware items are required
* Raspberry Pico W
* x3 DS18x20 temperature sensors (supported number can be changed)
* WLAN (obviously)

### Custom Hardware
#### Temperature Sensors
A single 4.7kΩ pull up resistor is required, along with 3 DS18x20 temperature sensors. 
Wiring is as follows; 
The DS18x20 sensor has three pins: VCC, GND, and Data.
Connect the VCC pin of the DS18x20 to the 3.3V pin on the Pico (e.g., Pin 36).
Connect the GND pin of the DS18x20 to one of the GND pins on the Pico (e.g., Pin 38) (see temp_sense_pin)
Connect the Data pin of the DS18x20 to a GPIO pin on the Pico (e.g., GPIO 16).
Place the 4.7kΩ resistor between the VCC and Data pins of the DS18x20.

The DS18x20 connection pin is specified within ``sensor.txt`` as ``temp_sense_pin``
