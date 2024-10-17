from hashlib import sha256

#script that controls the quadcopter to detect survivors of a flood disaster

# dependencies: pyzmq, cbor2
#py -m pip install pyzmq cbor2

def sysCall_init():
    sim = require('sim')


    global manual_mode #moves by itself or moved by the user with wsad keys
    manual_mode = True

    global x_min, x_max, y_min, y_max
    x_min = -37.250
    x_max = 2.250
    y_min = -22.250
    y_max = 17.250

    global wall_dist_threshold
    wall_dist_threshold = 1


    global survivors
    

    global sensor_names
    sensor_names = ["Front", "Right", "Back", "Left"]

    global survivors
    survivors = {}

    global trigger_values
    trigger_values = [-1, -1, -1, -1] #this is for the red value that was chosen to trigger the proximity sensor to start analysing the proximity sensor values

    global analyzation_duration
    analyzation_duration = 15

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

    #thesholds for narrowing the search view of the vision sensors, to get more accurate and certain results
    global red_min_thres 
    red_min_thres = 8

    global copter_speed 
    copter_speed = 0.05

    global copter_direction
    copter_direction = 0  # initialize the direction of the quadcopter to north, 0 = North, 1 = East, 2 = South, 3 = West

    # Initialize Vision Sensors
    global vision, vision1, vision2, vision3
    vision = sim.getObject('/Quadcopter/Vision_sensor')
    vision1 = sim.getObject('/Quadcopter/Vision_sensor[1]')  # Front sensor
    vision2 = sim.getObject('/Quadcopter/Vision_sensor[2]')  # Side sensor 1
    vision3 = sim.getObject('/Quadcopter/Vision_sensor[3]')  # Side sensor 2

    # Initialize Vision Graphs
    global graph, graph_1, graph_2, graph_3, graph_red, graph_red1, graph_red2, graph_red3
    graph = sim.getObject('/Graphs/VisionGraph')
    graph_1 = sim.getObject('/Graphs/VisionGraph[1]')
    graph_2 = sim.getObject('/Graphs/VisionGraph[2]')
    graph_3 = sim.getObject('/Graphs/VisionGraph[3]')
                            

    graph_red = sim.addGraphStream(graph, 'Vision Front Red', '-', 0, [1, 0, 0])   # Front sensor red
    graph_red1 = sim.addGraphStream(graph_1, 'Vision Left Red', '-', 0, [1, 0, 0])   # Left sensor red
    graph_red2 = sim.addGraphStream(graph_2, 'Vision Right Red', '-', 0, [1, 0, 0])  # Right sensor red
    graph_red3 = sim.addGraphStream(graph_3, 'Vision Back Red', '-', 0, [1, 0, 0])   # Back sensor red

    #graph the green values
    global graph_green, graph_green1, graph_green2, graph_green3
    graph_green = sim.addGraphStream(graph, 'Vision Front Green', '-', 0, [0, 1, 0])   # Front sensor green
    graph_green1 = sim.addGraphStream(graph_1, 'Vision Left Green', '-', 0, [0, 1, 0])   # Left sensor green
    graph_green2 = sim.addGraphStream(graph_2, 'Vision Right Green', '-', 0, [0, 1, 0])  # Right sensor green
    graph_green3 = sim.addGraphStream(graph_3, 'Vision Back Green', '-', 0, [0, 1, 0])   # Back sensor green

    #graph the blue values
    global graph_blue, graph_blue1, graph_blue2, graph_blue3
    graph_blue = sim.addGraphStream(graph, 'Vision Front Blue', '-', 0, [0, 0, 1])   # Front sensor blue
    graph_blue1 = sim.addGraphStream(graph_1, 'Vision Left Blue', '-', 0, [0, 0, 1])   # Left sensor blue
    graph_blue2 = sim.addGraphStream(graph_2, 'Vision Right Blue', '-', 0, [0, 0, 1])  # Right sensor blue
    graph_blue3 = sim.addGraphStream(graph_3, 'Vision Back Blue', '-', 0, [0, 0, 1])   # Back sensor blue



    # Initialize Proximity Sensors
    global proximity_sensor, proximity_sensor1, proximity_sensor2, proximity_sensor3
    global proximity_graph, proximity_graph_1, proximity_graph_2, proximity_graph_3, proximity_stream, proximity_stream1, proximity_stream2, proximity_stream3
    proximity_sensor = sim.getObject('/Quadcopter/Proximity_sensor')  # Front sensor
    proximity_sensor1 = sim.getObject('/Quadcopter/Proximity_sensor[1]')  # Left sensor
    proximity_sensor2 = sim.getObject('/Quadcopter/Proximity_sensor[2]')  # Right sensor
    proximity_sensor3 = sim.getObject('/Quadcopter/Proximity_sensor[3]')  # Back sensor

    # Initialize Proximity Graphs
    proximity_graph = sim.getObject('/Graphs/ProximityGraph')
    proximity_graph_1 = sim.getObject('/Graphs/ProximityGraph[1]')
    proximity_graph_2 = sim.getObject('/Graphs/ProximityGraph[2]')
    proximity_graph_3 = sim.getObject('/Graphs/ProximityGraph[3]')

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

        if not manual_mode:
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

    global survivors
    global red_min_thres
    global sensor_names
    global wall_dist_threshold
    

    # if survivors has not been initialized, then initialize it
    if not survivors:
        survivors = HashMap()

    # Vision sensor code for front sensor
    result, packet1, packet2 = sim.readVisionSensor(vision)
    avg_red = packet1[11]
    avg_green = packet1[12]
    avg_blue = packet1[13]

    avg = (avg_red * avg_red + avg_green * avg_green + avg_blue * avg_blue)
    avg = avg if avg != 0 else 0.00001  # to avoid division by zero

    red = avg_red / avg
    green = avg_green / avg
    blue = avg_blue / avg

    # Plot red value on VisionGraph for the front sensor
    sim.setGraphStreamValue(graph, graph_red, red)
    sim.setGraphStreamValue(graph, graph_green, green)
    sim.setGraphStreamValue(graph, graph_blue, blue)

    # Plot for other vision sensors
    result1, packet11, packet21 = sim.readVisionSensor(vision1)
    red1 = packet11[11] / (packet11[11] * packet11[11] + packet11[12] * packet11[12] + packet11[13] * packet11[13] + 0.00001)
    green1 = packet11[12] / (packet11[11] * packet11[11] + packet11[12] * packet11[12] + packet11[13] * packet11[13] + 0.00001)
    blue1 = packet11[13] / (packet11[11] * packet11[11] + packet11[12] * packet11[12] + packet11[13] * packet11[13] + 0.00001)
    sim.setGraphStreamValue(graph_1, graph_red1, red1)
    sim.setGraphStreamValue(graph_1, graph_green1, green1)
    sim.setGraphStreamValue(graph_1, graph_blue1, blue1)

    result2, packet12, packet22 = sim.readVisionSensor(vision2)
    red2 = packet12[11] / (packet12[11] * packet12[11] + packet12[12] * packet12[12] + packet12[13] * packet12[13] + 0.00001)
    green2 = packet12[12] / (packet12[11] * packet12[11] + packet12[12] * packet12[12] + packet12[13] * packet12[13] + 0.00001)
    blue2 = packet12[13] / (packet12[11] * packet12[11] + packet12[12] * packet12[12] + packet12[13] * packet12[13] + 0.00001)
    sim.setGraphStreamValue(graph_2, graph_red2, red2)
    sim.setGraphStreamValue(graph_2, graph_green2, green2)
    sim.setGraphStreamValue(graph_2, graph_blue2, blue2)

    result3, packet13, packet23 = sim.readVisionSensor(vision3)
    red3 = packet13[11] / (packet13[11] * packet13[11] + packet13[12] * packet13[12] + packet13[13] * packet13[13] + 0.00001)
    green3 = packet13[12] / (packet13[11] * packet13[11] + packet13[12] * packet13[12] + packet13[13] * packet13[13] + 0.00001)
    blue3 = packet13[13] / (packet13[11] * packet13[11] + packet13[12] * packet13[12] + packet13[13] * packet13[13] + 0.00001)
    sim.setGraphStreamValue(graph_3, graph_red3, red3)
    sim.setGraphStreamValue(graph_3, graph_green3, green3)
    sim.setGraphStreamValue(graph_3, graph_blue3, blue3)

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

    analysing_proximity = [analysing_proximity_0, analysing_proximity_1, analysing_proximity_2, analysing_proximity_3]
    counts = [count_0, count_1, count_2, count_3]
    mins = [min_0, min_1, min_2, min_3]
    proximities = [proximity_distance, proximity_distance1, proximity_distance2, proximity_distance3]
    reds = [red, red1, red2, red3]
    greens = [green, green1, green2, green3]
    blues = [blue, blue1, blue2, blue3]

    for i in range(4):
        if analysing_proximity[i]:
            #print(f"Analysing Proximity {i}: {counts[i]}")
            counts[i] += 1


            if counts[i] < analyzation_duration:
                
                if mins[i] == -1 and proximities[i] != 0:
                    mins[i] = proximities[i]
                else: 
                    # if the proximity sensor value is less than the current minimum value, then update the minimum value
                    if proximities[i] < mins[i] and proximities[i] != 0:
                        mins[i] = proximities[i]
            else:
                analysing_proximity[i] = False
                counts[i] = 0

                if mins[i] != -1:
                    quadcopter_position = sim.getObjectPosition(target, -1)

                    if i == 0:
                        new_x = round(quadcopter_position[0] + mins[i])
                        new_y = round(quadcopter_position[1])
                    elif i == 1:
                        new_y = round(quadcopter_position[1] - mins[i])
                        new_x = round(quadcopter_position[0])
                    elif i == 2:
                        new_x = round(quadcopter_position[0] - mins[i])
                        new_y = round(quadcopter_position[1])
                    elif i == 3:
                        new_y = round(quadcopter_position[1] + mins[i])
                        new_x = round(quadcopter_position[0])
                
                    
                    if not survivors.contains(new_x, new_y):

                        #now check if there aren't any other survivors detected within 3 units of radius. if so, then don't add the survivor
                        #this is to avoid multiple "ghost" survivors being detected at the same location
                        survivor_detected = False
                        survivor_area_radius = 2
                        for dx in range(-survivor_area_radius, survivor_area_radius + 1):
                            for dy in range(-survivor_area_radius, survivor_area_radius + 1):
                                if survivors.contains(new_x + dx, new_y + dy):
                                    survivor_detected = True
                                    break
                            if survivor_detected:
                                break

                        if not survivor_detected:
                            survivors.add(new_x, new_y)
                            print(f"Survivor Added - Loc: ({new_x}, {new_y}) from {sensor_names[i]} sensor, prox: {mins[i]}, trig: {trigger_values[i]}, Pos: {quadcopter_position}")
                        else:
                            print(f"Survivor(s) Already Detected within the Area {i}: {new_x}, {new_y}")

                    else:
                        print(f"Survivor(s) Already Detected within the Area {i}: {new_x}, {new_y}")

                    mins[i] = -1

        if not analysing_proximity[i]:
            if reds[i] >= red_min_thres and greens[i] < reds[i] * 0.5 and blues[i] < reds[i] * 0.5:

                trigger_values[i] = reds[i]
                analysing_proximity[i] = True

    # Update global variables
    analysing_proximity_0, analysing_proximity_1, analysing_proximity_2, analysing_proximity_3 = analysing_proximity
    count_0, count_1, count_2, count_3 = counts
    min_0, min_1, min_2, min_3 = mins
            
    

def sysCall_cleanup():
    # Clean-up code here
    pass

#----------------------------------------------HASH MAP 
class HashMap:
    def __init__(self):
        # Use a set to store the hashed values for quick lookup
        self.map = set()

    # Hash function to create a unique key from x, y coordinates
    def _hash(self, x, y):
        return hash((x, y))

    # Method to add (x, y) coordinates to the HashMap
    def add(self, x, y):
        hashed_value = self._hash(x, y)
        if hashed_value not in self.map:
            self.map.add(hashed_value)
            return True  # Indicates the pair was added successfully
        return False  # Indicates the pair was already in the map

    # Method to check if (x, y) coordinates are already in the HashMap
    def contains(self, x, y):
        return self._hash(x, y) in self.map

    # Method to remove (x, y) coordinates from the HashMap (optional)
    def remove(self, x, y):
        hashed_value = self._hash(x, y)
        if hashed_value in self.map:
            self.map.remove(hashed_value)
            return True  # Indicates the pair was removed successfully
        return False  # Indicates the pair was not in the map

# Example Usage:
#hash_map = HashMap()
