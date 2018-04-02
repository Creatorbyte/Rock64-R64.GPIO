#!/usr/bin/env python

# Allison Creely, 2018, LGPLv3 License
# Rock 64 GPIO Library for Python

# Import modules
import os.path
from multiprocessing import Process
from time import time
from time import sleep
#from array import array

# Define static module variables
var_gpio_root = '/sys/class/gpio'
ROCK = 'ROCK'
BOARD = 'BOARD'
BCM = 'BCM'
HIGH = 1
LOW = 0
OUT = 'out'
IN = 'in'
PUD_UP = 0
PUD_DOWN = 1
VERSION = '0.6.3'
RPI_INFO = {'P1_REVISION': 3, 'RAM': '1024M', 'REVISION': 'a22082', 'TYPE': 'Pi 3 Model B', 'PROCESSOR': 'BCM2837', 'MANUFACTURER': 'Embest'}

# Define GPIO arrays
ROCK_valid_channels = [27, 32, 33, 34, 35, 36, 37, 38, 64, 65, 67, 68, 69, 76, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 96, 97, 98, 100, 101, 102, 103, 104]
BOARD_to_ROCK = [0, 0, 0, 89, 0, 88, 0, 0, 64, 0, 65, 0, 67, 0, 0, 100, 101, 0, 102, 97, 0, 98, 103, 96, 104, 0, 76, 68, 69, 0, 0, 0, 38, 32, 0, 33, 37, 34, 36, 0, 35, 0, 0, 81, 82, 87, 83, 0, 0, 80, 79, 85, 84, 27, 86, 0, 0, 0, 0, 0, 0, 89, 88]
BCM_to_ROCK = [68, 69, 89, 88, 81, 87, 83, 76, 104, 98, 97, 96, 38, 32, 64, 65, 37, 80, 67, 33, 36, 35, 100, 101, 102, 103, 34, 82]

# Define dynamic module variables
gpio_mode = ROCK
warningmode = 1

# GPIO Functions
def setmode(mode):
    if mode in ['ROCK','BOARD','BCM']:
        global gpio_mode
        gpio_mode = mode
    else:
        print("An invalid mode ({}) was passed to setmode(). Use one of the following: ROCK, BOARD, BCM").format(mode)

def getmode():
    if gpio_mode in ['ROCK','BOARD','BCM']:
        return gpio_mode
    else:
        print("Error: An invalid mode ({}) is currently set").format(gpio_mode)

def get_gpio_number(channel):
    if gpio_mode in ['ROCK','BOARD','BCM']:
        # Convert to ROCK GPIO
        if gpio_mode == BOARD:
            newchannel = BOARD_to_ROCK[channel]
        if gpio_mode == BCM:
            newchannel = BCM_to_ROCK[channel]
        if gpio_mode == ROCK:
            newchannel = channel
        # Check that the GPIO is valid
        if newchannel in ROCK_valid_channels:
            return newchannel
        else:
            print("Error: GPIO not supported on {0} {1}").format(gpio_mode, newchannel)
            return 'none'
    else:
        print("Error: An invalid mode ({}) is currently set").format(gpio_mode)
        return 'none'

def setwarnings(state=True):
    if state in [0,1]:
        global warningmode
        warningmode = state
    else:
        print("Error: {} is not a valid warning mode. Use one of the following: True, 1, False, 0").format(state)

def setup(channel, direction, pull_up_down=PUD_DOWN, initial=LOW):
    # Translate the GPIO based on the current gpio_mode
    channel = get_gpio_number(channel)
    if channel == 'none':
        return
    # Check if GPIO export already exists
    var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/value"
    var_gpio_exists = os.path.exists(var_gpio_filepath)
    if var_gpio_exists == 1:
        if warningmode == 1:
            print("This channel (ROCK {}) is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.").format(channel)
    # Export GPIO
    else:
        try:
            var_gpio_filepath = var_gpio_root + "/export"
            with open(var_gpio_filepath, 'w') as file:
                file.write(str(channel))
        except:
            print("Error: Unable to export GPIO")
    # Set GPIO direction (in/out)
    try:
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/direction"
        with open(var_gpio_filepath, 'w') as file:
            file.write(str(direction))
    except:
        print("Error: Unable to set GPIO direction")
        return
    # If GPIO direction is out, set initial value of the GPIO (high/low)
    if direction == 'out':
        try:
            var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/value"
            with open(var_gpio_filepath, 'w') as file:
                file.write(str(initial))
        except:
            print("Error: Unable to set GPIO initial state")
    # If GPIO direction is in, set the state of internal pullup (high/low)
    if direction == 'in':
        try:
            var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/active_low"
            with open(var_gpio_filepath, 'w') as file:
                file.write(str(pull_up_down))
        except:
            print("Error: Unable to set internal pullup resistor state")

def output(channel, var_state):
    # Translate the GPIO based on the current gpio_mode
    channel = get_gpio_number(channel)
    if channel == 'none':
        return
    # Get direction of requested GPIO
    try:
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/direction"
        with open(var_gpio_filepath, 'r') as file:
            direction = file.read(1)
    except:
        direction = 'none'
    # Perform sanity checks
    if (direction != 'o') and (direction != 'i'):
        print("You must setup() the GPIO channel first")
        return
    if direction != 'o':
        print("The GPIO channel has not been set up as an OUTPUT")
        return
    # Set the value of the GPIO (high/low)
    try:
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/value"
        with open(var_gpio_filepath, 'w') as file:
            file.write(str(var_state))
    except:
        print("Error: Unable to set GPIO output state")

def input(channel):
    # Translate the GPIO based on the current gpio_mode
    channel = get_gpio_number(channel)
    if channel == 'none':
        return
    # Get direction of requested GPIO
    try:
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/direction"
        with open(var_gpio_filepath, 'r') as file:
            direction = file.read(1)
    except:
        direction = 'none'
    # Perform sanity checks
    if (direction != 'o') and (direction != 'i'):
        print("You must setup() the GPIO channel first")
        return
    # Get the value of the GPIO
    try:
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/value"
        with open(var_gpio_filepath, 'r') as file:
            return file.read(1)
    except:
        print("Error: Unable to get GPIO value")

def wait_for_edge(channel, var_edge, var_timeout):
    print("Error: Not implemented")

def event_detected(channel, var_edge):
    print("Error: Not implemented")

def add_event_detect(channel, var_edge, callback, bouncetime):
    print("Error: Not implemented")

def add_event_callback(channel, callback):
    print("Error: Not implemented")

def remove_event_detect(channel):
    print("Error: Not implemented")

def cleanup(channel='none'):
    # Translate the GPIO based on the current gpio_mode
    if channel != 'none':
        channel = get_gpio_number(channel)
        if channel == 'none':
            return
    # Cleanup all GPIOs
    if channel == 'none':
        for var_gpio_all in range(105):
            try:
                var_gpio_filepath = var_gpio_root + "/unexport"
                with open(var_gpio_filepath, 'w') as file:
                    file.write(str(var_gpio_all))
            except:
                pass
    # Cleanup specified GPIO
    elif channel in range(105):
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/value"
        var_gpio_exists = os.path.exists(var_gpio_filepath)
        if var_gpio_exists == 1:
            try:
                var_gpio_filepath = var_gpio_root + "/unexport"
                with open(var_gpio_filepath, 'w') as file:
                    file.write(str(channel))
            except:
                print("Error: Unknown Failure")
    else:
        print("Error: Invalid GPIO specified")


# PWM Class
class PWM:
    def __init__(self, channel, frequency):
        # Translate the GPIO based on the current gpio_mode
        channel = get_gpio_number(channel)
        if channel == 'none':
            return
        # Get direction of requested GPIO
        try:
            var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(channel) + "/direction"
            with open(var_gpio_filepath, 'r') as file:
                direction = file.read(1)
        except:
            direction = 'none'
        # Perform sanity checks
        if (direction != 'o') and (direction != 'i'):
            print("You must setup() the GPIO channel first")
            return
        if direction != 'o':
            print("The GPIO channel has not been set up as an OUTPUT")
            return
        if frequency <= 0.0:
            print("frequency must be greater than 0.0")
            return
        self.freq = frequency
        self.gpio = channel
        return

    def start(self, dutycycle, pwm_precision=HIGH):
        if (dutycycle < 0.0) or (dutycycle > 100.0):
            print("dutycycle must have a value from 0.0 to 100.0")
            return
        self.precision = pwm_precision
        self.dutycycle = dutycycle
        self.pwm_calc()
        self.p = Process(target=self.pwm_process, name='pwm_process')
        self.p.start()

    def stop(self):
        # ToDo: Replace with a gracefull method based on shutdown()
        self.p.terminate()

    @staticmethod
    def pwm_busywait(wait_time):
        current_time = time()
        while (time() < current_time+wait_time):
            pass

    def pwm_calc(self):
        self.sleep_low = (1.0 / self.freq) * ((100 - self.dutycycle) / 100.0)
        self.sleep_high = (1.0 / self.freq) * ((100 - (100 - self.dutycycle)) / 100.0)

    def pwm_process(self):
        var_gpio_filepath = str(var_gpio_root) + "/gpio" + str(self.gpio) + "/value"
        # Note: Low precision mode greatly reduces CPU usage, but accuracy will depend upon your kernel.
        # p.start(dutycycle, pwm_precision=GPIO.LOW)
        try:
            if self.precision == HIGH:
                while True:
                    with open(var_gpio_filepath, 'w') as file:
                        file.write('1')
                    PWM.pwm_busywait(self.sleep_high)
                    with open(var_gpio_filepath, 'w') as file:
                        file.write('0')
                    PWM.pwm_busywait(self.sleep_low)
            else:
                while True:
                    with open(var_gpio_filepath, 'w') as file:
                        file.write('1')
                    sleep(self.sleep_high)
                    with open(var_gpio_filepath, 'w') as file:
                        file.write('0')
                    sleep(self.sleep_low)
        except:
            try:
                with open(var_gpio_filepath, 'w') as file:
                    file.write('0')
            except:
                pass
            print("Warning: PWM process ended prematurely")

    def ChangeFrequency(self, frequency):
        self.freq = frequency
        self.pwm_calc()

    def ChangeDutyCycle(self, dutycycle):
        self.dutycycle = dutycycle
        self.pwm_calc()
