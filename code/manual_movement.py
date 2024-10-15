import keyboard

def sysCall_init():
    sim = require('sim')
    global target
    global copter_speed
    
    copter_speed = 0.1  # Speed for movement

    # Get the target object for the quadcopter
    target = sim.getObject('/Quadcopter/target')

def sysCall_actuation():
    global target
    global copter_speed

    position = sim.getObjectPosition(target, -1)

    # Use 'keyboard' to capture input
    if keyboard.is_pressed('w'):  # Move forward
        position[0] += copter_speed
    elif keyboard.is_pressed('s'):  # Move backward
        position[0] -= copter_speed
    elif keyboard.is_pressed('a'):  # Move left
        position[1] += copter_speed
    elif keyboard.is_pressed('d'):  # Move right
        position[1] -= copter_speed
    elif keyboard.is_pressed('q'):  # Move up
        position[2] += copter_speed
    elif keyboard.is_pressed('e'):  # Move down
        position[2] -= copter_speed

    sim.setObjectPosition(target, -1, position)
    print(f"Target position: {position}")

def sysCall_cleanup():
    pass
