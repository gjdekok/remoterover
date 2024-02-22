#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, InfraredSensor
from pybricks.parameters import Port
import socket
import time

ev3 = EV3Brick()
left_motor = Motor(Port.A)
right_motor = Motor(Port.D)
ir_sensor = InfraredSensor(Port.S4)

# Initialize (default) motor speed
current_speed_percent = 50

# Define some global variables that will be used by the tasks
should_exit = False
forward_movement = False
no_movement = True

# Setting up the socket server
HOST = ''
PORT = 12345
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # TCP/IP
s.bind((HOST, PORT))
s.setblocking(False)

# Dictionary of pressed keys (to be communicated by the socket client)
keys_pressed = {'w': False, 'a': False, 's': False, 'd': False, 'up': False, 'down': False, 'left': False, 'right': False}

def update_key_state(command, state):
    key = command.split(' ')[0]
    keys_pressed[key] = state

def stop_motors_if_no_command():
    """Function to make sure all motors stop if no key is pressed."""
    if not any(keys_pressed.values()):
        left_motor.stop()
        right_motor.stop()

def execute_command(command):
    """Function to execute a command received from the socket client."""
    global current_speed_percent, should_exit, forward_movement, no_movement
    
    if command == "exit":
        should_exit = True  # Signal the program to exit
        return

    # Process speed change commands
    parts = command.split(' ')
    if parts[0].isdigit() and len(parts) == 2 and parts[1] == 'down':
        current_speed_percent = int(parts[0]) * 10 + 10
        return

    if len(parts) < 2:
        return

    key, action = parts[0], parts[-1]
    state = action == 'down'
    update_key_state(key, state)

    left_speed = right_speed = 0
    forward_movement = False
    no_movement = True

    # Forward/Backward movement
    if (keys_pressed['w'] or keys_pressed['up']):
        left_speed += current_speed_percent
        right_speed += current_speed_percent
        forward_movement = True
    if keys_pressed['s'] or keys_pressed['down']:
        left_speed -= current_speed_percent
        right_speed -= current_speed_percent

    # Turning in place
    if (keys_pressed['a'] or keys_pressed['left']) and not any(keys_pressed[k] for k in ['d', 'right', 'w', 'up', 's', 'down']):
        left_speed = -current_speed_percent
        right_speed = current_speed_percent
    if (keys_pressed['d'] or keys_pressed['right']) and not any(keys_pressed[k] for k in ['a', 'left', 'w', 'up', 's', 'down']):
        left_speed = current_speed_percent
        right_speed = -current_speed_percent

    # Adjust for turning while moving forward
    if (keys_pressed['a'] or keys_pressed['left']) and (keys_pressed['w'] or keys_pressed['up']):
        left_speed *= 0.5
    if (keys_pressed['d'] or keys_pressed['right']) and (keys_pressed['w'] or keys_pressed['up']):
        right_speed *= 0.5

    # Adjust for turning while moving backwards
    if (keys_pressed['a'] or keys_pressed['left']) and (keys_pressed['s'] or keys_pressed['down']):
        left_speed *= 0.5
    if (keys_pressed['d'] or keys_pressed['right']) and (keys_pressed['s'] or keys_pressed['down']):
        right_speed *= 0.5

    if left_speed != 0 or right_speed != 0:
        no_movement = False

    left_motor.dc(left_speed)
    right_motor.dc(right_speed)

    stop_motors_if_no_command()



def socket_task():
    """Coroutine for the socket server task."""
    s.listen(1)
    print("Waiting for a connection...")
    conn, addr = None, None

    while conn is None:
        try:
            conn, addr = s.accept()
        except OSError as e:
            if e.args[0] == 11:  # EAGAIN
                yield  
            else:
                print("Socket accept failed with error:", e) # F-strings not supported
                raise  
        yield  

    conn.setblocking(False) 

    while True:
        try:
            data = conn.recv(1024)
            if not data:
                conn.close()
                break  # Connection closed, exit the loop
            command = data.decode('utf-8')
            execute_command(command)
        except OSError as e:
            if e.args[0] == 11:  # EAGAIN
                yield 
            else:
                print("Socket recv failed with error:", e) # F-strings not supported
                conn.close()
                break  
        yield  

def sensor_task():
    """Coroutine for the sensor task."""
    global forward_movement
    last_print_time = time.time() - 1  
    while True:
        current_time = time.time()
        if current_time - last_print_time >= 1:  
            print("IR Sensor Distance:", ir_sensor.distance()) # F-strings not supported
            last_print_time = current_time 

        obstacle_distance = ir_sensor.distance()
        is_obstacle_too_close = obstacle_distance < 10
        if (is_obstacle_too_close and forward_movement) or (is_obstacle_too_close and no_movement):
            left_motor.brake()
            right_motor.brake()
        yield 


def scheduler(tasks):
    """Function to schedule the tasks."""
    while not should_exit:
        for task in tasks:
            next(task)
    print("Exiting program...")


# Run scheduler
try:
    scheduler([socket_task(), sensor_task()])
finally:
    if s: 
        s.close() 