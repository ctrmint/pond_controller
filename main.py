# Mark Rodman
# ------------------------------------------------------
# Description
# Pond Controller as an API
# ------------------------------------------------------
from phew import server, connect_to_wifi
import network, socket, struct, time, ubinascii
import dht, machine, onewire, ds18x20, ujson
from pico_hardware import OnboardTemp
from machine import Pin
import json
import time


# Configuration Files
WIFI_SETTINGS_FILE = 'wifi_settings.txt'
SENSOR_FILE = 'sensors.txt'

# Onboard sensor ref
OPERATING_VOLTAGE = 3.3
BIT_RANGE = 65535
REF_TEMP = 27
# Example alarm thresholds - external sensors
LOW_ALARM_TEMP = 20.0  # Example low alarm threshold in Celsius
HIGH_ALARM_TEMP = 25.0  # Example high alarm threshold in Celsius
#
LOOP_SLEEP_SECS = 1
TYPE_HARDWARE = "Hardware"
led = Pin("LED", Pin.OUT)
led.off()
#led_green = machine.Pin(0, machine.Pin.OUT)
#led_red = machine.Pin(1, machine.Pin.OUT)

ABOUT = {"About": {"Author": "Mark Rodman", "Build": 1.0, "Documentation": "https://some.github.repo"}}

def get_value_from_dict(dictionary, key):
    """
    Retrieve the value from a dictionary using the provided key.
    :param dictionary: The dictionary to search.
    :param key: The key to look up in the dictionary.
    :return: The value associated with the key, or None if the key is not found.
    """
    return dictionary.get(key, None)


def external_sensors(roms, ds_sensor):
    """
    Get measurements from ds18x20 external sensors
    """
    measures = []
    for rom in roms:
        tempC = ds_sensor.read_temp(rom)
        if tempC < LOW_ALARM_TEMP or tempC > HIGH_ALARM_TEMP:
            alarm = True
        else:
            alarm = False
        measurement = {
            "type": TYPE_HARDWARE,
            "value": tempC,
            "sensor": rom_to_hex(rom),
            "location": str(get_value_from_dict(sensor_placement, rom_to_hex(rom))),
            "time": get_epoch_time(),
            "resolution_raw": get_resolution(ds_sensor, rom),
            "resolution_bits": (get_resolution(ds_sensor, rom)) * 9 + 9,
            "alarm": alarm
        }
        measures.append(measurement)
    return measures


# Function to get the current epoch time
def get_epoch_time():
    t = time.localtime()
    return time.mktime(t)


# Convert byte array to human-readable hex string
def rom_to_hex(rom):
    return ubinascii.hexlify(rom).decode('utf-8')


# Initialize the DS18X20 sensor
def init_sensor(pin_number):
    ds_pin = machine.Pin(pin_number)
    return ds18x20.DS18X20(onewire.OneWire(ds_pin))


# Function to get sensor resolution
def get_resolution(sensor, rom):
    return sensor.read_scratch(rom)[4] & 0x60 >> 5


def avg_from_json(json_array, key, condition_key, condition_val):
    """
    Calculates average value from JSON array.
    :json_array: JSON data structure (array), contains key value pairs from which the avg will be calculated
    :key: The key which contains the value to be averaged.
    :condition: The filter condition
    """
    average = 0
    # Filter the records for "Pond" and extract the celsius values
    values = [entry[key] for entry in json_array if entry.get(condition_key) == condition_val]
    # Calculate the average
    average = sum(values) / len(values) if values else 0
    return average


def gen_full_data():
    ds_sensor.convert_temp()
    measures = external_sensors(roms, ds_sensor)
    # Internal sensor
    onboard_temp_sensor.get_reading(verbose=False)
    measures.append({"location": "onboard", "type": TYPE_HARDWARE, "sensor": "default", "value": onboard_temp_sensor.current_temp, "max_c": onboard_temp_sensor.maximum, "min_C": onboard_temp_sensor.minimum, "time": get_epoch_time()})
    # Get average Pond temp from Pond results for each probe and append to JSON array
    average_pond_temp = avg_from_json(measures, "value", "location", "Pond")
    average_pond_housing = avg_from_json(measures, "value", "location", "Pump housing")
    measures.append({"location": "Pond", "value": average_pond_temp, "type": "avg_temp", "time": get_epoch_time()})
    #print(average_pond_housing)
    return measures, average_pond_temp, onboard_temp_sensor.current_temp, average_pond_housing


def str_roms(roms):
    """
    Stringify those ROM values and return in a JSON object for display
    """
    rom_json = {}
    rom_array = []
    for r in roms:
        rom_array.append(rom_to_hex(r))
    return {"roms": rom_array}


def exec_action(action):
    """
    Function to process action commands sent via a POST.
    Filters action type (atype) and call relevant functions based on name,
    This needs to be refactored so that its more sophisticated. 
    """
    if action.get('type'):
        atype = action['type']
    
        if action.get('params'):
            params = action['params']
        else:
            params = None
        
        if atype == "onboard_led":
            response = onboardLED(params)
    
    else:
        print("no action")
    
    return


def onboardLED(params):
    """
    onboard LED action function call
    Do some stuff with the onboard LED.
    Used to experiment with POST functionality in the API
    """
    if params == "on":
        led.on()
    if params == "off":
        led.off()
    if params == True:
        led.on()
    if params == False:
        led.off()
        
    return

### API Endpoints
@server.route("/api/control-led", methods=["POST"])
def ledCommand(request):
    led_red.value(request.data["ledRed"])
    led_green.value(request.data["ledGreen"])
    return json.dumps({"message" : "Command sent successfully!"}), 200, {"Content-Type": "application/json"}


@server.route("/api/roms", methods=["GET"])
def roms(request):
    rom_json = str_roms(roms)
    return json.dumps(rom_json), 200, {"Content-Type": "application/json"}


@server.route("/api/sensors", methods=["GET"])
def ext_sensors(request):
    ds_sensor.convert_temp()
    measures = external_sensors(roms, ds_sensor)
    return json.dumps({"sensors": measures}), 200, {"Content-Type": "application/json"}


@server.route("/api/onboard", methods=["GET"])
def onboard(request):
    mtype = "onboard"
    onboard_temp_sensor.get_reading(verbose=False)
    measure = {"type": TYPE_HARDWARE, "sensor": "default", "value": onboard_temp_sensor.current_temp}
    return json.dumps({mtype: measure}), 200, {"Content-Type": "application/json"}


@server.route("/api/verbose", methods=["GET"])
def verbose(request):
    measures, average_pond_temp, current_onboard_temp, pump_housing_temp = gen_full_data()
    return json.dumps({"status": measures}), 200, {"Content-Type": "application/json"}


@server.route("/api/summary", methods=["GET"])
def summary(request):
    measures, average_pond_temp, current_onboard_temp, pump_housing_temp = gen_full_data()
    return json.dumps({"avg_pond": average_pond_temp, "onboard": current_onboard_temp, "housing": pump_housing_temp}), 200, {"Content-Type": "application/json"}


@server.route("/api/sensor_placements", methods=["GET"])
def sensor_placements(request):
    return json.dumps({"sensor_placements": sensor_placement}), 200, {"Content-Type": "application/json"}


@server.route("/api/about", methods=["GET"])
def about(request):
    return json.dumps(ABOUT), 200, {"Content-Type": "application/json"}


@server.route("/api/action", methods=["POST"])
def action(request):
    print("starting action")
    action_json = {None: None}
    action = request.data
    if isinstance(action, dict):
        if 'type' in action:
            action_json = action
            exec_action(action)
    return json.dumps(action_json), 200, {"Content-Type": "application/json"}


@server.route("/api/toggle_led", methods=["GET"])
def toggle_led(request):
    """
    Toggle the onboard LED on and off using the API.
    Returns JSON with state of LED, 0 = off, 1 = on. 
    """
    led.toggle()
    return json.dumps({"onboard LED state": led.value()}), 200, {"Content-Type": "application/json"}


@server.route("/api/led_endpoint", methods=["GET", "POST"])
def led_endpoint(request):
    if request.method == 'GET':
        state = led.value()
        if led.value() == 0:
            out = {"active": False}
        elif led.value() == 1:
            out = {"active": True}
        else:
            out = {"error": True}
        
    if request.method == 'POST':
        onboardLED(request.data['active'])
        out = request.data
    return json.dumps(out), 200, {"Content-Type": "application/json"}


@server.catchall()
def catchall(request):
    return json.dumps({"message" : "URL not found!"}), 404, {"Content-Type": "application/json"}


#### _____Start of main execution here____
# Get Wifi setting from file
try:
    with open(WIFI_SETTINGS_FILE, 'r') as file:
        wifi_json = json.load(file)
except Exception as e:
    print(e)
# dynamically define kv based on wifi input file keys should be wifi_ssid, wifi_password, buffer_size, and port
for key, value in wifi_json.items():
    globals()[key] = value

# Get Sensor details from file
try:
    with open(SENSOR_FILE, 'r') as file:
        sensor_json = json.load(file)
        for key, value in sensor_json.items():
            globals()[key] = value
except Exception as e:
    print(e)

try:
    ip = connect_to_wifi(wifi_ssid, wifi_password)
    #print(ip)
    time.sleep(5)
except:
    print("Failed to connect to the WiFi")

# external sensor setup
roms = None
while not roms:
    ds_sensor = init_sensor(temp_sense_pin)
    roms = ds_sensor.scan()

# onboard sensor setup
sensor_temp = machine.ADC(4)
conversion_factor = (OPERATING_VOLTAGE / BIT_RANGE)
onboard_temp_sensor = OnboardTemp(name="Onboard Sensor", machine=(machine.ADC(4)), ref_temp=REF_TEMP, bit_range=BIT_RANGE, operating_voltage=OPERATING_VOLTAGE)

# Start server
server.run()
