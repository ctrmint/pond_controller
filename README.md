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
