
#script that controls the quadcopter to detect and report people trapped in a flood disaster

# Create grid dimensions based on given x, y min and max values
def create_grid(x_min, x_max, y_min, y_max, grid_size):
    x_range = int((x_max - x_min) // grid_size) + 1
    y_range = int((y_max - y_min) // grid_size) + 1
    grid = [[{'coordinates': [x_min + i * grid_size, y_min + j * grid_size], 'status': 0} for j in range(y_range)] for i in range(x_range)]
    return grid
 

#checks if the x and y index of the coordinate grid are out of bounds
def check_if_out_of_bounds(x, y):
    return x < 0 or y < 0 or x >= len(grid) or y >= len(grid[0])


##----------------------------------------------INITIALIZATION----------------------------------------------##
def sysCall_init():
    sim = require('sim')
    

    #thesholds for narrowing the search view of the vision sensors, to get more accurate and certain results
    global red_min_thres 
    red_min_thres = 8

    global copter_speed 
    copter_speed = 0.05

    global copter_direction
    copter_direction = 0  # initialize the direction of the quadcopter to north, 0 = Front, 1 = Right, 2 = Back, 3 = Left
    
    #initialize coodinate walls for the environment (taken from scene environment coodinates)
    global x_min, x_max, y_min, y_max
    x_min = -37.250
    x_max = 2.250
    y_min = -22.250
    y_max = 17.250

    #MapTarget used to select and visualize where the quadcopter target will go to next
    global map_target
    map_target = sim.getObject('/MapTarget')

    global quadcopter
    quadcopter = sim.getObject('/Quadcopter')

    #the length of each grid cell relative to the environment (used to break down the environment into smaller grid cells)
    global grid_size
    grid_size = 3.0

    # the index of the location of the map target in the grid
    global grid_x_index
    global grid_y_index

    #get the x y location of the qudcopter and snap the coodinates to the nearest grid cell (allows the user to move the quadcopter around in the 3d scene environment to test out different starting positions)
    quadcopter_position = sim.getObjectPosition(quadcopter, -1)
    grid_x_index = int((quadcopter_position[0] - x_min) // grid_size)
    grid_y_index = int((quadcopter_position[1] - y_min) // grid_size)

    
    #coordinate grid that will be used to keep track of the visited and unvisited cells in the environment
    global grid
    grid = create_grid(x_min, x_max, y_min, y_max, grid_size)

    #now mark the grid cell as visited
    grid[grid_x_index][grid_y_index]['status'] = 1

    #initialize the map target position to the location where the grid_x_index and grid_y_index are (use the grid_size to determine the position)
    x_offset = x_min + grid_x_index * grid_size
    y_offset = y_min + grid_y_index * grid_size
    sim.setObjectPosition(map_target, -1, [x_offset, y_offset, 4])

    #keep track of the quadcopter's position and back track if no more unvisited cells are available at any direction within the current position
    global position_stack
    position_stack = []

    #push the quadcopter's index positions to the stack
    position_stack.append((grid_x_index, grid_y_index))

    #initialize the map target position to the quadcopter's position
    sim.setObjectPosition(map_target, -1, sim.getObjectPosition(quadcopter, -1))

    #example usage of grid, to set a grid cell as visited
    #grid[(x, y)] = 1  # 1 means visited, 0 means unvisited, -1 means obstacle

    global hit_threshold
    hit_threshold = 0.2

    global sensor_names
    sensor_names = ["Front", "Right", "Back", "Left"]

    global survivors
    survivors = {}

    global trigger_values
    trigger_values = [-1, -1, -1, -1] #used to capture the red value of the vision sensor when a survivor is detected

    global analyzation_duration # of iterations that the proximity sensor will be analysing the proximity sensor values after the vision sensor trigger value has been detected
    analyzation_duration = 15

    #variable that will be used to determine if the quadcopter is analysing the proximity sensor to determine the location of the survivor
    global min_proximity_mode_0, min_proximity_mode_1, min_proximity_mode_2, min_proximity_mode_3
    min_proximity_mode_0 = False
    min_proximity_mode_1 = False
    min_proximity_mode_2 = False
    min_proximity_mode_3 = False

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
    global sim
    global copter_direction
    global grid_x_index, grid_y_index

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

    map_target_position = sim.getObjectPosition(map_target, -1)

    abs_diff_x = abs(int(round(sim.getObjectPosition(quadcopter, -1)[0])) - int(round(map_target_position[0])))
    abs_diff_y = abs(int(round(sim.getObjectPosition(quadcopter, -1)[1])) - int(round(map_target_position[1])))
    
    # if the quadcopter target position is at the map target position, then try to select the next unvisited cell to move to
    if abs_diff_x <= hit_threshold and abs_diff_y <= hit_threshold:
        #print("Target Position Reached")
        dir_update_count = 0
        hyp_direction = copter_direction + 0; #hypothetical direction that the quadcopter could move to

        # print current index of the quadcopter
        #print("Current Index: ", grid_x_index, grid_y_index)

        found_unvisited = False #the goal is to find an unvisited cell to move to

        #check all directions to see if there are any unvisited cells that are within bounds, and have no obstacles in the way
        while dir_update_count < 4:
            
            hyp_x_index = grid_x_index + 0
            hyp_y_index = grid_y_index + 0

            #update the hypothetical index based on the hypothetical direction
            if hyp_direction == 0 :
                hyp_x_index += 1
            elif hyp_direction == 1:
                hyp_y_index -= 1
            elif hyp_direction == 2:
                hyp_x_index -= 1
            elif hyp_direction == 3:
                hyp_y_index += 1
            else:
                pass

            
            #first thing to check if the hypothetical index is out of bounds
            out_of_bounds = check_if_out_of_bounds(hyp_x_index, hyp_y_index)

            #check if there is an obstacle in front of the hypothetical direction
            obstacle_detected = distance_to_compare[hyp_direction] != 0 and distance_to_compare[hyp_direction] < grid_size + 2

            #if the hypothetical location is out of bounds, or has an obstacle, or has already been visited, then change the direction of the quadcopter to the next direction clockwise
            if out_of_bounds or obstacle_detected or grid[hyp_x_index][hyp_y_index]['status'] == 1:
                hyp_direction = (hyp_direction + 1) % 4
                dir_update_count += 1
                continue

            #if the hypothetical location is unvisited, then move the map target to the hypothetical location so that the quadcopter can start moving to that location
            if grid[hyp_x_index][hyp_y_index]['status'] == 0:
                    
                found_unvisited = True

                #push the current position to the stack
                position_stack.append((grid_x_index, grid_y_index))

                #print("Moving to Position: ", hyp_x_index, hyp_y_index)

                #update the grid_x_index and grid_y_index to the previously hypothetical index
                grid_x_index = hyp_x_index + 0
                grid_y_index = hyp_y_index + 0

                #mark the grid cell as visited
                grid[hyp_x_index][hyp_y_index]['status'] = 1

                #move the map target to the new target position
                new_target_position = [
                    grid[hyp_x_index][hyp_y_index]['coordinates'][0],
                    grid[hyp_x_index][hyp_y_index]['coordinates'][1],
                    4
                ]

                sim.setObjectPosition(map_target, -1, new_target_position)

                #print moving to coordinates
                print(f"Moving to Position: ({grid[hyp_x_index][hyp_y_index]['coordinates'][0]}, {grid[hyp_x_index][hyp_y_index]['coordinates'][1]}), Prox: {round(distance_to_compare[hyp_direction], 2)}, Dir: {sensor_names[hyp_direction]}, Stack Size: {len(position_stack)}")
                
                break;

                

        #if all directions are either visited or have obstacles, then back track to the previous position
        if not found_unvisited:
            #print("No Possible Directions to Move, Backtracking")

            #print("Backtracking, Stack Size: ", len(position_stack))

            if position_stack:
                #print(f"Backtracking to Position: ({grid_x_index}, {grid_y_index}), ", " Stack Size: ", len(position_stack), ", Stack Top: ", position_stack[-1])
                print(f"Backtracking to Position: ({grid[grid_x_index][grid_y_index]['coordinates'][0]}, {grid[grid_x_index][grid_y_index]['coordinates'][1]}), Stack Size: {len(position_stack)}")

                # pop the last position from the stack
                last_position = position_stack.pop()

                # update the grid_x_index and grid_y_index to the last position
                grid_x_index = last_position[0]
                grid_y_index = last_position[1]

                # move the map target to the new target position
                new_target_position = [
                    grid[grid_x_index][grid_y_index]['coordinates'][0],
                    grid[grid_x_index][grid_y_index]['coordinates'][1],
                    4
                ]

                sim.setObjectPosition(map_target, -1, new_target_position)

                if not position_stack:
                    print("MISSION COMPLETE: No More Unvisited Cells to Move To")
       
    else:
        #print("Moving to Target Position")

        #move the quadcopter to the map target position by the copter_speed
        new_quad_position = sim.getObjectPosition(target, -1)
        new_quad_position[0] = new_quad_position[0] + copter_speed if new_quad_position[0] < map_target_position[0] else new_quad_position[0] - copter_speed if new_quad_position[0] > map_target_position[0] else new_quad_position[0]
        new_quad_position[1] = new_quad_position[1] + copter_speed if new_quad_position[1] < map_target_position[1] else new_quad_position[1] - copter_speed if new_quad_position[1] > map_target_position[1] else new_quad_position[1]
        sim.setObjectPosition(target, -1, new_quad_position)


def sysCall_sensing():

    global survivors
    global red_min_thres
    global sensor_names
    global hit_threshold
    

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


    global min_proximity_mode_0, min_proximity_mode_1, min_proximity_mode_2, min_proximity_mode_3
    global count_0, count_1, count_2, count_3
    global min_0, min_1, min_2, min_3

    min_proximity_mode = [min_proximity_mode_0, min_proximity_mode_1, min_proximity_mode_2, min_proximity_mode_3]
    counts = [count_0, count_1, count_2, count_3]
    mins = [min_0, min_1, min_2, min_3]
    proximities = [proximity_distance, proximity_distance1, proximity_distance2, proximity_distance3]
    reds = [red, red1, red2, red3]
    greens = [green, green1, green2, green3]
    blues = [blue, blue1, blue2, blue3]

    # for every direction, check if the vision sensor has detected a survivor
    for i in range(4):
        if min_proximity_mode[i]:
            #print(f"Analysing Proximity {i}: {counts[i]}")
            counts[i] += 1

            # give the proximity sensor some time to analyse the proximity sensor values to determine the smallest proximity value (mitigates false positives)
            if counts[i] < analyzation_duration:
                
                if mins[i] == -1 and proximities[i] != 0:
                    mins[i] = proximities[i]
                else: 
                    # if the proximity sensor value is less than the current minimum value, then update the minimum value
                    if proximities[i] < mins[i] and proximities[i] != 0:
                        mins[i] = proximities[i]
            else:
                min_proximity_mode[i] = False
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

                        #now check if there aren't any other survivors detected within x units of radius. if so, then don't add the survivor
                        # this is to prevent the same survivor from being detected multiple times because of slight variations in the sensor values
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
                            #print(f"Survivor Added - Loc: ({new_x}, {new_y}) from {sensor_names[i]} sensor, prox: {mins[i]}, trig: {trigger_values[i]}, Pos: {quadcopter_position}")

                            #print survivor found at coordinates x, y
                            print(f"--------------Survivor Found at Coordinates: ({new_x}, {new_y}) from {sensor_names[i]} sensor, Prox: {round(mins[i], 2)}, Trig: {round(trigger_values[i], 2)}--------------")
                        else:
                            print(f"Survivor(s) Already Detected within the Area {i}: {new_x}, {new_y}")

                    else:
                        print(f"Survivor(s) Already Detected within the Area {i}: {new_x}, {new_y}")

                    mins[i] = -1

        if not min_proximity_mode[i]:

            if is_red_detected(reds[i], greens[i], blues[i]):

                trigger_values[i] = reds[i]
                min_proximity_mode[i] = True

    # Update global variables
    min_proximity_mode_0, min_proximity_mode_1, min_proximity_mode_2, min_proximity_mode_3 = min_proximity_mode
    count_0, count_1, count_2, count_3 = counts
    min_0, min_1, min_2, min_3 = mins
            
def is_red_detected(red, green, blue):
    return red >= red_min_thres and green < red * 0.5 and blue < red * 0.5

def sysCall_cleanup():
    # Clean-up code here
    pass

#----------------------------------------------HASH MAP 
class HashMap:
    def __init__(self):
        # Use a set to store the hashed values for quick lookup
        self.map = set()

    # create a unique key from x, y coordinates
    def _hash(self, x, y):
        return hash((x, y))

    # add (x, y) coordinates to the HashMap
    def add(self, x, y):
        hashed_value = self._hash(x, y)
        if hashed_value not in self.map:
            self.map.add(hashed_value)
            return True  # Indicates the pair was added successfully
        return False  # Indicates the pair was already in the map

    # check if (x, y) coordinates are already in the HashMap
    def contains(self, x, y):
        return self._hash(x, y) in self.map

    # remove (x, y) coordinates from the HashMap (optional)
    def remove(self, x, y):
        hashed_value = self._hash(x, y)
        if hashed_value in self.map:
            self.map.remove(hashed_value)
            return True  # Indicates the pair was removed successfully
        return False  # Indicates the pair was not in the map
    

