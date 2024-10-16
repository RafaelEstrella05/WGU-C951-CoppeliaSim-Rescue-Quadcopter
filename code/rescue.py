#vision sensor and proximity sensor script for the quadcopter

# dependencies: pyzmq, cbor2
#py -m pip install pyzmq cbor2

def sysCall_init():
    sim = require('sim')

    #variable that will be used to determine if the quadcopter is analysing the proximity sensor to determine the location of the survivor
    global analysing_proximity_0 
    analysing_proximity_0 = False

    global analysing_proximity_1
    analysing_proximity_1 = False

    global analysing_proximity_2
    analysing_proximity_2 = False

    global analysing_proximity_3
    analysing_proximity_3 = False

    global min_0, min_1, min_2, min_3
    min_0 = -1
    min_1 = -1
    min_2 = -1
    min_3 = -1

    global count_0, count_1, count_2, count_3
    count_0 = 0
    count_1 = 0
    count_2 = 0
    count_3 = 0



    global copter_speed 
    copter_speed = 0.05

    global copter_direction
    copter_direction = 1  # initialize the direction of the quadcopter to north, 0 = North, 1 = East, 2 = South, 3 = West

    # Initialize Vision Sensors
    global vision, vision1, vision2, vision3
    vision = sim.getObject('/Quadcopter/Vision_sensor')
    vision1 = sim.getObject('/Quadcopter/Vision_sensor[1]')  # Front sensor
    vision2 = sim.getObject('/Quadcopter/Vision_sensor[2]')  # Side sensor 1
    vision3 = sim.getObject('/Quadcopter/Vision_sensor[3]')  # Side sensor 2

    # Initialize Vision Graphs
    global graph, graph_1, graph_2, graph_3, graph_red, graph_red1, graph_red2, graph_red3
    graph = sim.getObject('/VisionGraph')
    graph_1 = sim.getObject('/VisionGraph[1]')
    graph_2 = sim.getObject('/VisionGraph[2]')
    graph_3 = sim.getObject('/VisionGraph[3]')
                            

    graph_red = sim.addGraphStream(graph, 'Vision Front', '-', 0, [1, 0, 0])   # Front sensor red
    graph_red1 = sim.addGraphStream(graph_1, 'Vision Left', '-', 0, [1, 0, 0])   # Left sensor red
    graph_red2 = sim.addGraphStream(graph_2, 'Vision Right', '-', 0, [1, 0, 0])  # Right sensor red
    graph_red3 = sim.addGraphStream(graph_3, 'Vision Back', '-', 0, [1, 0, 0])   # Back sensor red

    # Initialize Proximity Sensors
    global proximity_sensor, proximity_sensor1, proximity_sensor2, proximity_sensor3
    global proximity_graph, proximity_graph_1, proximity_graph_2, proximity_graph_3, proximity_stream, proximity_stream1, proximity_stream2, proximity_stream3
    proximity_sensor = sim.getObject('/Quadcopter/Proximity_sensor')  # Front sensor
    proximity_sensor1 = sim.getObject('/Quadcopter/Proximity_sensor[1]')  # Left sensor
    proximity_sensor2 = sim.getObject('/Quadcopter/Proximity_sensor[2]')  # Right sensor
    proximity_sensor3 = sim.getObject('/Quadcopter/Proximity_sensor[3]')  # Back sensor

    # Initialize Proximity Graphs
    proximity_graph = sim.getObject('/ProximityGraph')
    proximity_graph_1 = sim.getObject('/ProximityGraph[1]')
    proximity_graph_2 = sim.getObject('/ProximityGraph[2]')
    proximity_graph_3 = sim.getObject('/ProximityGraph[3]')

    proximity_stream = sim.addGraphStream(proximity_graph, 'Proximity Front', '-', 0, [0, 1, 0])   # Front sensor graph
    proximity_stream1 = sim.addGraphStream(proximity_graph_1, 'Proximity Left', '-', 0, [0, 1, 0])   # Left sensor graph
    proximity_stream2 = sim.addGraphStream(proximity_graph_2, 'Proximity Right', '-', 0, [0, 1, 0])  # Right sensor graph
    proximity_stream3 = sim.addGraphStream(proximity_graph_3, 'Proximity Back', '-', 0, [0, 1, 0])   # Back sensor graph

    # Initialize Quadcopter target (position)
    global target
    target = sim.getObject('..')  # Ensuring target is set correctly

def sysCall_actuation():
    global copter_direction

    # Proximity sensor check for front
    proximity_result = sim.readProximitySensor(proximity_sensor)
    proximity_state = proximity_result[0]
    proximity_distance = proximity_result[1] if proximity_state > 0 else 0
    #print("Proximity Detected (Front), Distance: ", proximity_distance) if proximity_state > 0 else print("No Proximity Detection (Front)")

    # Repeat for other proximity sensors
    proximity_result1 = sim.readProximitySensor(proximity_sensor1)
    proximity_distance1 = proximity_result1[1] if proximity_result1[0] > 0 else 0

    proximity_result2 = sim.readProximitySensor(proximity_sensor2)
    proximity_distance2 = proximity_result2[1] if proximity_result2[0] > 0 else 0

    proximity_result3 = sim.readProximitySensor(proximity_sensor3)
    proximity_distance3 = proximity_result3[1] if proximity_result3[0] > 0 else 0


    distance_to_compare = [proximity_distance, proximity_distance1, proximity_distance2, proximity_distance3]


    # Print copter direction
    #print("Copter Direction: ", copter_direction)
    #print distance to compare
    #print("Distance to Compare: ", distance_to_compare[copter_direction])

    if (distance_to_compare[copter_direction] < 300 and distance_to_compare[copter_direction] > 1.5) or distance_to_compare[copter_direction] == 0:
        
        # Move forward by 0.5 units
        position = sim.getObjectPosition(target, -1)
        #position[0] += 0.02

        '''...'''
        # Change position based on the orientation of the quadcopter
        if copter_direction == 0:  # North
            position[0] += copter_speed
        elif copter_direction == 1:  # East
            position[1] -= copter_speed
        elif copter_direction == 2:  # South
            position[0] -= copter_speed
        elif copter_direction == 3:  # West
            position[1] += copter_speed
        

        sim.setObjectPosition(target, -1, position)
        
    else:
        #print("Stopping movement. Proximity Distance (Front): ", proximity_distance)

        # Set the new direction of the quadcopter
        copter_direction = (copter_direction + 1) % 4

        # print new direction
        #print("New Copter Direction: ", copter_direction)

def sysCall_sensing():

    # Vision sensor code for front sensor
    result, packet1, packet2 = sim.readVisionSensor(vision)
    avg_red = packet1[11]
    avg_green = packet1[12]
    avg_blue = packet1[13]

    avg = (avg_red * avg_red + avg_green * avg_green + avg_blue * avg_blue)
    avg = avg if avg != 0 else 0.00001  # to avoid division by zero

    red = avg_red / avg

    # Plot red value on VisionGraph for the front sensor
    sim.setGraphStreamValue(graph, graph_red, red)

    # Plot for other vision sensors
    result1, packet11, packet21 = sim.readVisionSensor(vision1)
    red1 = packet11[11] / (packet11[11] * packet11[11] + packet11[12] * packet11[12] + packet11[13] * packet11[13] + 0.00001)
    sim.setGraphStreamValue(graph_1, graph_red1, red1)

    result2, packet12, packet22 = sim.readVisionSensor(vision2)
    red2 = packet12[11] / (packet12[11] * packet12[11] + packet12[12] * packet12[12] + packet12[13] * packet12[13] + 0.00001)
    sim.setGraphStreamValue(graph_2, graph_red2, red2)

    result3, packet13, packet23 = sim.readVisionSensor(vision3)
    red3 = packet13[11] / (packet13[11] * packet13[11] + packet13[12] * packet13[12] + packet13[13] * packet13[13] + 0.00001)
    sim.setGraphStreamValue(graph_3, graph_red3, red3)

    # Proximity sensor graphing for all proximity sensors
    proximity_result = sim.readProximitySensor(proximity_sensor)
    proximity_distance = proximity_result[1] if proximity_result[0] > 0 else 0
    sim.setGraphStreamValue(proximity_graph, proximity_stream, proximity_distance)

    proximity_result1 = sim.readProximitySensor(proximity_sensor1)
    proximity_distance1 = proximity_result1[1] if proximity_result1[0] > 0 else 0
    sim.setGraphStreamValue(proximity_graph_1, proximity_stream1, proximity_distance1)

    proximity_result2 = sim.readProximitySensor(proximity_sensor2)
    proximity_distance2 = proximity_result2[1] if proximity_result2[0] > 0 else 0
    sim.setGraphStreamValue(proximity_graph_2, proximity_stream2, proximity_distance2)

    proximity_result3 = sim.readProximitySensor(proximity_sensor3)
    proximity_distance3 = proximity_result3[1] if proximity_result3[0] > 0 else 0
    sim.setGraphStreamValue(proximity_graph_3, proximity_stream3, proximity_distance3)


    #Want to now detect survivors and pin their location by using the vision sensor to detect the color red (symbolizes survivor detection) location of the quadcopter plus the value of the proximity sensor
    #If the red value is greater than 0.5, then we have detected a survivor
    #record the proximity sensor value for x iterations, and find the minimum value of the proximity sensor to determine the location of the survivor

    global analysing_proximity_0, analysing_proximity_1, analysing_proximity_2, analysing_proximity_3
    global count_0, count_1, count_2, count_3
    global min_0, min_1, min_2, min_3

    if analysing_proximity_0:
        #print("Analysing Proximity Zero: ", count_0)
        count_0 += 1

        if count_0 < 10:
            #print("Count Zero: ", count_0)
            #print("--min_0: ", min_0)


            #if min_0 is -1, then set it to the current proximity sensor value
            if min_0 == -1 and proximity_distance != 0:
                min_0 = proximity_distance

                #print("First Min_0: ", min_0)
            else:
                #if the current proximity sensor value is less than the min_0 value, then set min_0 to the current proximity sensor value
                if proximity_distance < min_0 and proximity_distance != 0:
                    min_0 = proximity_distance
                    #print("New Min_0: ", min_0)
            

        else:
            analysing_proximity_0 = False
            count_0 = 0
            ###print("Final Proximity (Min_0): ", min_0)

            if min_0 != -1 and min_0 < 7:
                #get the current position of the quadcopter
                quadcopter_position = sim.getObjectPosition(target, -1)
                #print("Quadcopter Position: ", quadcopter_position)

                new_x = quadcopter_position[0] + min_0

                min_0 = -1
                print("Survivor GPS Approximate Location Zero: ", new_x, ", ", quadcopter_position[1])

            
            

    if not analysing_proximity_0:
        #print("Red Value 0: ", red);
        if red > 1.5 and red < 4:
            #print("Potential Survivor Detected Zero, Scanning ...")
            analysing_proximity_0 = True
            
    

def sysCall_cleanup():
    # Clean-up code here
    pass
