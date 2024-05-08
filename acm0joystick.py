from evdev import InputDevice, categorize, ecodes, KeyEvent 
gamepad = InputDevice('/dev/input/event1') 
last = {
    "ABS_RZ": 128,
    "ABS_Z": 128
}

import serial
positions = {}
ser = serial.Serial('/dev/ttyACM0', 9600)

current_speeds = [0, 0]
def serial_out(axis, value):
    if axis not in (1, 4): return
    forward = value < 32768
    press_length = (value - 32768) if value >= 32768 else 32768 - value
    motor_value = int(press_length / 32767 * 255)
    if (press_length < 1000): press_length = 0
    if (press_length > 31000): press_length = 32767
    motor_speed = str(motor_value)
    command = ("L" if axis == 1 else "R") + ("r" if forward else "f") + motor_speed.zfill(3)
    #print(forward, press_length, motor_speed, command, " "*10, end = '\r')
    delta = abs(current_speeds[0 if axis == 1 else 1] - motor_value)
    if (delta > 5):
        current_speeds[0 if axis == 1 else 1] = motor_value
        #print(command)
        ser.write(command.encode('utf_8'))


for event in gamepad.read_loop(): 
    if event.type == ecodes.EV_ABS:
        absevent = categorize(event) 
        #print(absevent.event.code, absevent.event.value, end="\r")
        #if (absevent.event.code in positions):
            #delta = absevent.event.value - positions[absevent.event.code]
            #if abs(delta) > 255:
        positions[absevent.event.code] = absevent.event.value
        serial_out(absevent.event.code, absevent.event.value)
        #print(positions, " " * 10, end = "\r")
