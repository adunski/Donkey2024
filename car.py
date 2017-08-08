# -*- coding: utf-8 -*-

"""
Script to drive a donkey car using a joystick hosted on the vehicle.
And also train!

Usage:
    car.py (drive)
    car.py (train) (--tub=<tub>) (--model=<model>)

"""
import os
import docopt
import donkeycar as dk 

CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
MODELS_PATH = os.path.join(CAR_PATH, 'models')

def drive():
    #Initialized car

    V = dk.vehicle.Vehicle()

    cam = dk.parts.MockCamera()
    #cam = dk.parts.PiCamera()
    V.add(cam, outputs=['cam/image_array'], threaded=True)

    # a pilot that uses local joystick
    ctr = dk.parts.JoystickPilot()

    #ctr = dk.parts.LocalWebController()

    V.add(ctr, 
    inputs=['cam/image_array'],
    outputs=['user/angle', 'user/throttle', 'user/mode'],
    threaded=True)


    #steering_controller = dk.parts.MockController(1)
    steering_controller = dk.parts.PCA9685(1)
    steering = dk.parts.PWMSteering(controller=steering_controller,
                                left_pulse=460, right_pulse=260)

    #throttle_controller = dk.parts.MockController(0)
    throttle_controller = dk.parts.PCA9685(0)
    throttle = dk.parts.PWMThrottle(controller=throttle_controller,
                                max_pulse=500, zero_pulse=370, min_pulse=220)

    V.add(steering, inputs=['user/angle'])
    V.add(throttle, inputs=['user/throttle'])

    #add tub to save data
    inputs=['user/angle', 'user/throttle', 'cam/image_array']
    types=['float', 'float', 'image_array']

    th = dk.parts.TubHandler(path=DATA_PATH)
    tub = th.new_tub_writer(inputs=inputs, types=types)
    V.add(tub, inputs=inputs)

    #run the vehicle
    V.start(rate_hz=30)

    #you can now use joystick and drive to record images
def train(tub_name, model_name):
    
    km = dk.parts.KerasModels()
    model = km.default_linear()
    kl = dk.parts.KerasLinear(model)
    
    tub_path = os.path.join(DATA_PATH, tub_name)
    tub = dk.parts.Tub(tub_path)
    batch_gen = tub.batch_gen()
    
    X_keys = ['cam/image_array']
    Y_keys = ['user/angle', 'user/throttle']
    
    def train_gen(gen, X_keys, y_keys):
        while True:
            batch = next(gen)
            X = [batch[k] for k in X_keys]
            y = [batch[k] for k in y_keys]
            yield X, y
            
    keras_gen = train_gen(batch_gen, X_keys, Y_keys)
    
    model_path = os.path.join(MODELS_PATH, model_name)
    kl.train(keras_gen, None, saved_model_path=model_path, epochs=10)
    
if __name__ == '__main__':
    pass
