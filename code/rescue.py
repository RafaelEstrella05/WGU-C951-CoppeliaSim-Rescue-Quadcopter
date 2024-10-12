
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

    # Initialize Proximity Sensor and Graph (renamed to 'Proximity_sensor')
    global proximity_sensor
    global proximity_graph
    global proximity_stream
    proximity_sensor = sim.getObject('/Quadcopter/Proximity_sensor')  # Changed name here
    proximity_graph = sim.getObject('/ProximityGraph')
    proximity_stream = sim.addGraphStream(proximity_graph, 'proximity', '-', 0, [0,1,0])

    # Initialize Quadcopter target (position)
    global target
    target = sim.getObject('..')  # Ensuring target is set correctly

def sysCall_actuation():
    # Proximity sensor check
    proximity_result = sim.readProximitySensor(proximity_sensor)
    proximity_state = proximity_result[0]
    proximity_distance = proximity_result[1] if proximity_state > 0 else 0
    print("Proximity Detected, Distance: ", proximity_distance) if proximity_state > 0 else print("No Proximity Detection")

    if proximity_state > 0 and proximity_distance > 1.5:
        # Move forward by 0.5 units
        position = sim.getObjectPosition(target, -1)
        position[0] += 0.05  # Moving forward by 0.5 on X-axis (or adjust according to direction)
        sim.setObjectPosition(target, -1, position)
        print("Moving forward by 0.05 units. New position: ", position)
    else:
        print("Stopping movement. Proximity Distance: ", proximity_distance)

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
    #print("Red: ", red, "Green: ", green, "Blue: ", blue)
    
    # Plot red value on VisionGraph
    sim.setGraphStreamValue(graph, graph_red, red)

    # Proximity sensor graphing (proximity_distance declared here)
    proximity_result = sim.readProximitySensor(proximity_sensor)
    proximity_state = proximity_result[0]
    proximity_distance = proximity_result[1] if proximity_state > 0 else 0
    sim.setGraphStreamValue(proximity_graph, proximity_stream, proximity_distance)
    
    #print("Proximity Detected, Distance: ", proximity_distance) if proximity_state > 0 else print("No Proximity Detection")

def sysCall_cleanup():
    # Clean-up code here
    pass
