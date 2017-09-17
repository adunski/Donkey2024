import os

#PATHS
CAR_PATH = PACKAGE_PATH = os.path.dirname(os.path.realpath(__file__))
DATA_PATH = os.path.join(CAR_PATH, 'data')
MODELS_PATH = os.path.join(CAR_PATH, 'models')

#VEHICLE
DRIVE_LOOP_HZ = 20
MAX_LOOPS = 100000

#CAMERA
CAMERA_RESOLUTION = (120,160)
CAMERA_FRAMERATE = DRIVE_LOOP_HZ

#STEERING
STEERING_CHANNEL = 1
STEERING_LEFT_PWM = 420
STEERING_RIGHT_PWM = 360

#THROTTLE
THROTTLE_CHANNEL = 0
THROTTLE_FORWARD_PWM = 390
THROTTLE_STOPPED_PWM = 360
THROTTLE_REVERSE_PWM = 290