#vision sensor script for the quadcopter

# dependencies: pyzmq, cbor2
#py -m pip install pyzmq cbor2

def sysCall_init():
    sim = require('sim');

    # do some initialization here
    #
    # Instead of using globals, you can do e.g.:
    # self.myVariable = 21000000
    global vision;
    vision = sim.getObject('/Quadcopter/Vision_sensor');
    pass

def sysCall_actuation():
    # put your actuation code here
    pass

def sysCall_sensing():
    # put your sensing code here
    #packet1: default auxiliary packet of 15 auxiliary values: the minimum of [intensity red green blue depth], the maximum of [intensity red green blue depth], and the average of [intensity red green blue depth]
    #int result, list packet1, list packet2, etc. = sim.readVisionSensor(int visionSensorHandle)

    result,packet1,packet2= sim.readVisionSensor(vision);
    avg_red = packet1[11];
    print(avg_red);
    pass

def sysCall_cleanup():
    # do some clean-up here
    pass

# See the user manual or the available code snippets for additional callback functions and details
