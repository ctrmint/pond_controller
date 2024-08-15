class OnboardTemp(object):
    """
    Class or onboard temperature sensor
    """
    def __init__(self, name=None, machine=None, ref_temp=None, bit_range=None, operating_voltage=None):
        self.name = name
        self.sensor = machine
        self.ref_temp = ref_temp
        self.bit_range = bit_range
        self.operating_voltage = operating_voltage
        self.maximum = 0.0
        self.minimum = 0.0
        self.current_temp = 0.0
        self.previous_temp = 0.0
        self.setup = True
        self.reading_available = False
        self.max_change = True
        self.min_change = True

        if self.operating_voltage and self.bit_range:
            self.conversion_factor = self.operating_voltage / self.bit_range

    def reset_reading(self):
        self.reading_available = False
        self.max_change = False
        self.min_change = False
        return
    
    def get_reading(self, verbose=True):
        msg_str = ""
        reading = (self.sensor.read_u16()) * self.conversion_factor
        self.current_temp = self.ref_temp - ( reading - 0.706)/0.001721
        self.current_temp = round(self.current_temp,1)
        
        if bool(self.setup):
            msg_str = ("| -----  First run, initial max and min set.\n")
            self.maximum = self.current_temp
            self.minimum = self.current_temp
            self.setup = False
        
        else:
            if self.current_temp != self.previous_temp:
                self.reading_available = True
                self.previous_temp = self.current_temp
            
                if (self.current_temp > self.maximum):
                    self.maximum = self.current_temp
                    self.max_change = True
                    msg_str += ("| -----  Updating maximum: {}!!\n".format(self.maximum))
            
                if (self.current_temp < self.minimum):
                    self.minimum = self.current_temp
                    self.min_change = True
                    msg_str += ("| -----  Updating minimum: {}!!\n".format(self.minimum))
        
        
        if verbose and len(msg_str) >0:
            print(msg_str)

            
            
