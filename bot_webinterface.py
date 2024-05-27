from flask import Flask, Response, redirect, jsonify, request
from flask_cors import CORS
from picamera2 import Picamera2
import cv2
import threading
import time

### You can donate at https://www.buymeacoffee.com/mmshilleh 

app = Flask(__name__)
CORS(app)

camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))
camera.camera_controls["AwbEnable"] = True
camera.start()

def generate_frames():
    while True:
        try:
            frame = cv2.cvtColor(camera.capture_array(), cv2.COLOR_BGR2RGB)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        except Exception as e:
            print(e)
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        # TODO - sleep for duration needed to cap framerate at ~20fps; add timestamp to image (?)

@app.route('/video')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Motor config

import serial
ser = serial.Serial('/dev/ttyACM0', 9600)

class Motor:
    def __init__(self, name, serial_prefix):
        self.name = name
        self.serial_prefix = serial_prefix
        self._speed = 0
        self._direction = "forward"
        self.set()

    def __repr__(self):
        return f"<Motor name={self.name} serial_prefix={self.serial_prefix} speed={self.speed} direction={self.direction}>"

    @property
    def direction(self):
        return self._direction

    @direction.setter
    def direction(self, value):
        if value not in ("forward", "reverse"):
            raise ValueError("direction must be 'forward' or 'reverse'")
        self._direction = value

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        # 0 to 100 versus motor range, 0 to 32k
        if value < 0 or value > 255:
            raise ValueError("speed must be an int between 0 and 100.")
        self._speed = int(value)

    def set(self, *, direction="forward", speed=0):
        self.direction = direction
        self.speed = speed
        #command = ("L" if axis == 1 else "R") + ("r" if forward else "f") + motor_speed.zfill(3)
        command = self.serial_prefix + self.direction[0] + str(self.speed).zfill(3)
        #print(forward, press_length, motor_speed, command, " "*10, end = '\r')
        #delta = abs(current_speeds[0 if axis == 1 else 1] - motor_value)
        #if (delta > 5):
        #    current_speeds[0 if axis == 1 else 1] = motor_value
            #print(command)

        ser.write(command.encode('utf_8'))

left_motor = Motor("left", "L")
right_motor = Motor("right", "R")

@app.route('/motors', methods=['GET', 'POST'])
def motors():
    if request.method == 'GET':
        return jsonify({"left":  {"direction": left_motor.direction,  "speed": left_motor.speed}, 
                        "right": {"direction": right_motor.direction, "speed": right_motor.speed}
                       })
    # assert request.method == "POST"
    try:
        data = request.json
        print(data)
    except:
        return jsonify({"success": False, "message": "Could not decode JSON data in POST request"})
    left_settings = data.get("left", {})
    right_settings = data.get("right", {})
    left_speed = left_settings.get("speed", left_motor.speed)
    left_direction = left_settings.get("direction", left_motor.direction)
    right_speed = right_settings.get("speed", right_motor.speed)
    right_direction = right_settings.get("direction", right_motor.direction)
    
    try:
        print(left_motor)
        print(right_motor)
        print(left_settings, left_speed, left_direction)
        print(right_settings, right_speed, right_direction)
        left_motor.set(direction = left_direction, speed = left_speed)
        right_motor.set(direction = right_direction, speed = right_speed)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})
    return jsonify({"success": True, "message": ""})

class Servo:
    def __init__(self, name, serial_prefix, min_angle=0, max_angle=180):
        self.name = name
        self.serial_prefix = serial_prefix
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.angle = (self.max_angle - self.min_angle) / 2 + self.min_angle
        self.set()

    def __repr__(self):
        return f"<Servo name={self.name} serial_prefix={self.serial_prefix} range=({self.min_angle}, {self.max_angle}) angle={self.angle}>"

    @property
    def range(self):
        return (self.min_angle, self.max_angle)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        if value < self.min_angle or value > self.max_angle:
            raise ValueError(f"angle must be between {self.min_angle} and {self.max_angle}.")
        self._angle = int(value)

    def set(self, *, direction="forward", speed=0):
        self.direction = direction
        self.speed = speed
        #command = ("L" if axis == 1 else "R") + ("r" if forward else "f") + motor_speed.zfill(3)
        command = self.serial_prefix + str(self.angle).zfill(3)

        ser.write(command.encode('utf_8'))

### LIDAR hardware-dependent section
try:
    from rplidar_tests import lidar, get_some_scans
    lidar_task = None
    lidar_data = None

    def scan_worker(scan_points):
        global lidar_data
        lidar_data = get_some_scans(scan_points)

    def start_scan(scan_points):
        global lidar_task
        global lidar_data
        lidar_task = threading.Thread(target=lambda: scan_worker(scan_points))
        lidar_task.start()

    @app.route('/lidar')
    def lidar():
        global lidar_task
        global lidar_data
        if lidar_task is None:
            start_scan(100)
            return jsonify({"status": "started"})
        elif lidar_task.is_alive():
            return jsonify({"status": "underway"})
        else:
            lidar_task = None
            prev_data = lidar_data
            lidar_data = None
            return jsonify(prev_data)
except Exception as e:
    @app.route('/lidar')
    def lidar():
        return jsonify({"status": "feature_unavailable"})

@app.route('/')
def root():
    return redirect('/video', code=307)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

