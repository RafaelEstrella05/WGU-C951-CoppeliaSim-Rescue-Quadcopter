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

    global graph;
    global graph_red;
    global graph_green;
    global graph_blue;
    graph = sim.getObject('/Graph');
    graph_red = sim.addGraphStream(graph, 'red', '-', 0, [1,0,0])
    graph_green = sim.addGraphStream(graph, 'green', '-', 0, [0,1,0])
    graph_blue = sim.addGraphStream(graph, 'blue', '-', 0, [0,0,1])


    pass

def sysCall_actuation():
    # put your actuation code here
    pass

def sysCall_sensing():
    # put your sensing code here
    '''
    packet1: default auxiliary packet of 15 auxiliary values: the minimum of [intensity red green blue depth], the maximum of [intensity red green blue depth], and the average of [intensity red green blue depth]
    int result, list packet1, list packet2, etc. = sim.readVisionSensor(int visionSensorHandle)    
    '''
    result,packet1,packet2= sim.readVisionSensor(vision);
    avg_red = packet1[11];
    avg_green = packet1[12];
    avg_blue = packet1[13];

    #normalize the values
    avg = (avg_red * avg_red + avg_green * avg_green + avg_blue * avg_blue);

    
    red = avg_red / avg;
    green = avg_green / avg;
    blue = avg_blue / avg;
    
    #print(avg_red);
    #print red green blue values
    print("Red: ", red, "Green: ", green, "Blue: ", blue);

    #plot the values
    sim.setGraphStreamValue(graph, graph_red, red);
    sim.setGraphStreamValue(graph, graph_green, green);
    sim.setGraphStreamValue(graph, graph_blue, blue);

    pass

def sysCall_cleanup():
    # do some clean-up here
    pass

# See the user manual or the available code snippets for additional callback functions and details
