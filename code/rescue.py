
#vision sensor and proximity sensor script for the quadcopter

# dependencies: pyzmq, cbor2
#py -m pip install pyzmq cbor2

def sysCall_init():
    sim = require('sim')

    # Initialize Vision Sensor
    global vision
    vision = sim.getObject('/Quadcopter/Vision_sensor')

    # Initialize Vision Graph
    global graph
    global graph_red
    graph = sim.getObject('/VisionGraph')
    graph_red = sim.addGraphStream(graph, 'red', '-', 0, [1,0,0])

    # Initialize Proximity Sensor and Graph
    global proximity_sensor
    global proximity_graph
    global proximity_stream
    proximity_sensor = sim.getObject('/Quadcopter/Proximity_sensor')
    proximity_graph = sim.getObject('/ProximityGraph')
    proximity_stream = sim.addGraphStream(proximity_graph, 'proximity', '-', 0, [0,1,0])

def sysCall_actuation():
    # Actuation code here
    pass

def sysCall_sensing():
    # Vision sensor code
    result,packet1,packet2 = sim.readVisionSensor(vision)
    avg_red = packet1[11]
    avg_green = packet1[12]
    avg_blue = packet1[13]

    # Normalize the values
    avg = (avg_red * avg_red + avg_green * avg_green + avg_blue * avg_blue)
    
    red = avg_red / avg
    green = avg_green / avg
    blue = avg_blue / avg
    
    # Print red, green, blue values
    print("Red: ", red, "Green: ", green, "Blue: ", blue)
    
    # Plot red value on VisionGraph
    sim.setGraphStreamValue(graph, graph_red, red)

    # Proximity sensor code
    proximity_state, proximity_distance = sim.readProximitySensor(proximity_sensor)
    
    if proximity_state > 0:  # If the proximity sensor detects something
        # Plot the proximity sensor value
        sim.setGraphStreamValue(proximity_graph, proximity_stream, proximity_distance)
        print("Proximity Detected, Distance: ", proximity_distance)
    else:
        # No detection, plot a default value
        sim.setGraphStreamValue(proximity_graph, proximity_stream, 0)
        print("No Proximity Detection")

def sysCall_cleanup():
    # Clean-up code here
    pass
