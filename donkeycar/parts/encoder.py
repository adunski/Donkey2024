"""
Rotary Encoder
"""

from datetime import datetime
from donkeycar.parts.teensy import TeensyRCin
import re
import time




# The Arduino class is for a quadrature wheel or motor encoder that is being read by an offboard microcontroller
# such as an Arduino or Teensy that is feeding serial data to the RaspberryPy or Nano via USB serial. 
# The microcontroller should be flashed with this sketch (use the Arduino IDE to do that): https://github.com/zlite/donkeycar/tree/master/donkeycar/parts/encoder/encoder
# Make sure you check the sketch using the "test_encoder.py code in the Donkeycar tests folder to make sure you've got your 
# encoder plugged into the right pins, or edit it to reflect the pins you are using.

# You will need to calibrate the mm_per_tick line below to reflect your own car. Just measure out a meter and roll your car
# along it. Change the number below until it the distance reads out almost exactly 1.0 

# This samples the odometer at 10HZ and does a moving average over the past ten readings to derive a velocity

class ArduinoEncoder(object):
    def __init__(self, mm_per_tick=0.0000599, debug=False):
        import serial
        import serial.tools.list_ports
        for item in serial.tools.list_ports.comports():
            print(item)  # list all the serial ports
        self.ser = serial.Serial('/dev/ttyACM0', 115200, 8, 'N', 1, timeout=1)
        # initialize the odometer values
        self.ser.write(str.encode('reset'))  # restart the encoder to zero
        self.ticks = 0
        self.debug = debug
        self.on = True

    def update(self):
        while self.on:
            input = self.ser.readline()
            self.temp = input.decode()
            self.temp = self.temp.strip()  # remove any whitespace
            if (self.temp.isnumeric()):
                self.ticks = int(self.temp)

    def run_threaded(self):
        return self.ticks 


    def shutdown(self):
        # indicate that the thread should be stopped
        print('stopping Arduino encoder')
        self.on = False
        time.sleep(.5)

class AStarSpeed:
    def __init__(self):
        self.speed = 0
        self.linaccel = None

        self.sensor = TeensyRCin(0)

        self.on = True

    def update(self):
        encoder_pattern = re.compile('^E ([-0-9]+)( ([-0-9]+))?( ([-0-9]+))?$')
        linaccel_pattern = re.compile('^L ([-.0-9]+) ([-.0-9]+) ([-.0-9]+) ([-0-9]+)$')

        while self.on:
            start = datetime.now()

            l = self.sensor.astar_readline()
            while l:
                m = encoder_pattern.match(l.decode('utf-8'))

                if m:
                    value = int(m.group(1))
                    # rospy.loginfo("%s: Receiver E got %d" % (self.node_name, value))
                    # Speed
                    # 40 ticks/wheel rotation,
                    # circumfence 0.377m
                    # every 0.1 seconds
                    if len(m.group(3)) > 0:
                        period = 0.001 * int(m.group(3))
                    else:
                        period = 0.1

                    self.speed = 0.377 * (float(value) / 40) / period   # now in m/s
                else:
                    m = linaccel_pattern.match(l.decode('utf-8'))

                    if m:
                        la = { 'x': float(m.group(1)), 'y': float(m.group(2)), 'z': float(m.group(3)) }

                        self.linaccel = la
                        print("mw linaccel= " + str(self.linaccel))

                l = self.sensor.astar_readline()

            stop = datetime.now()
            s = 0.1 - (stop - start).total_seconds()
            if s > 0:
                time.sleep(s)

    def run_threaded(self):
        return self.speed # , self.linaccel

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('stopping AStarSpeed')
        time.sleep(.5)


class RotaryEncoder():
    def __init__(self, mm_per_tick=0.306096, pin=13, poll_delay=0.0166, debug=False):
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin, GPIO.IN)
        GPIO.add_event_detect(pin, GPIO.RISING, callback=self.isr)

        # initialize the odometer values
        self.m_per_tick = mm_per_tick / 1000.0
        self.poll_delay = poll_delay
        self.meters = 0
        self.last_time = time.time()
        self.meters_per_second = 0
        self.counter = 0
        self.on = True
        self.debug = debug
        self.top_speed = 0
        self.prev_dist = 0.
    
    def isr(self, channel):
        self.counter += 1
        
    def update(self):
        # keep looping infinitely until the thread is stopped
        while(self.on):
                
            #save the ticks and reset the counter
            ticks = self.counter
            self.counter = 0
            
            #save off the last time interval and reset the timer
            start_time = self.last_time
            end_time = time.time()
            self.last_time = end_time
            
            #calculate elapsed time and distance traveled
            seconds = end_time - start_time
            distance = ticks * self.m_per_tick
            velocity = distance / seconds
            
            #update the odometer values
            self.meters += distance
            self.meters_per_second = velocity
            if(self.meters_per_second > self.top_speed):
                self.top_speed = self.meters_per_second

            #console output for debugging
            if(self.debug):
                print('seconds:', seconds)
                print('distance:', distance)
                print('velocity:', velocity)

                print('distance (m):', round(self.meters, 4))
                print('velocity (m/s):', self.meters_per_second)

            time.sleep(self.poll_delay)

    def run_threaded(self):
        delta = self.meters - self.prev_dist
        self.prev_dist = self.meters
        return self.meters, self.meters_per_second, delta

    def shutdown(self):
        # indicate that the thread should be stopped
        self.on = False
        print('Stopping Rotary Encoder')
        print("\tDistance Travelled: {} meters".format(round(self.meters, 4)))
        print("\tTop Speed: {} meters/second".format(round(self.top_speed, 4)))
        time.sleep(.5)
        
        import RPi.GPIO as GPIO
        GPIO.cleanup()
