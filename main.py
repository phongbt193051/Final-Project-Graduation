import cv2
import RPi.GPIO as GPIO
from flask import Flask, render_template, Response, jsonify
import threading
from time import sleep, time

app = Flask(__name__)

# GPIO setup
GPIO.setwarnings(False)  # Vô hiệu hóa cảnh báo GPIO
GPIO.setmode(GPIO.BCM)

# Khai báo các chân GPIO
in1_motor1 = 24
in2_motor1 = 23
en_motor1 = 25
in1_motor2 = 22
in2_motor2 = 27
en_motor2 = 17
sensor_left = 19
sensor_right = 6

GPIO.setup([in1_motor1, in2_motor1, en_motor1, in1_motor2, in2_motor2, en_motor2], GPIO.OUT)
GPIO.setup([sensor_left, sensor_right], GPIO.IN)
GPIO.output([in1_motor1, in2_motor1, in1_motor2, in2_motor2], GPIO.LOW)

pwm_motor1 = GPIO.PWM(en_motor1, 1000)
pwm_motor2 = GPIO.PWM(en_motor2, 1000)
pwm_motor1.start(40)
pwm_motor2.start(40)

# Global variables
auto_mode = False
auto_thread = None
robot_position = {'x': 5, 'y': 5}  # Vị trí khởi tạo của robot (ở giữa bản đồ)


# GPIO functions for motor control
def move_forward():
    GPIO.output(in1_motor1, GPIO.HIGH)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.HIGH)
    GPIO.output(in2_motor2, GPIO.LOW)


def move_backward():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.HIGH)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.HIGH)


def turn_left():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.HIGH)
    GPIO.output(in1_motor2, GPIO.HIGH)
    GPIO.output(in2_motor2, GPIO.LOW)


def turn_right():
    GPIO.output(in1_motor1, GPIO.HIGH)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.HIGH)


def stop_motors():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.LOW)


# Auto mode logic
def auto_mode_logic():
    global auto_mode, robot_position
    while auto_mode:
        left = GPIO.input(sensor_left)
        right = GPIO.input(sensor_right)

        if left == GPIO.HIGH and right == GPIO.HIGH:
            move_forward()
            robot_position['x'] = max(0, robot_position['x'] - 1)  # Tiến lên
        elif left == GPIO.LOW and right == GPIO.HIGH:
            turn_left()
            robot_position['y'] = max(0, robot_position['y'] - 1)  # Quẹo trái
        elif left == GPIO.HIGH and right == GPIO.LOW:
            turn_right()
            robot_position['y'] = min(9, robot_position['y'] + 1)  # Quẹo phải
        elif left == GPIO.LOW and right == GPIO.LOW:
            stop_motors()

        sleep(0.1)
    stop_motors()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/control/<action>', methods=['GET'])
def control(action):
    global auto_mode, robot_position
    if auto_mode:
        return jsonify({"status": "error", "message": "Manual control is disabled in Auto mode"})

    if action == 'forward':
        move_forward()
        robot_position['x'] = max(0, robot_position['x'] - 1)
    elif action == 'backward':
        move_backward()
        robot_position['x'] = min(9, robot_position['x'] + 1)
    elif action == 'left':
        turn_left()
        robot_position['y'] = max(0, robot_position['y'] - 1)
    elif action == 'right':
        turn_right()
        robot_position['y'] = min(9, robot_position['y'] + 1)
    elif action == 'stop':
        stop_motors()

    return jsonify({"status": "success", "position": robot_position})


@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    global auto_mode, auto_thread
    auto_mode = not auto_mode

    if auto_mode:
        auto_thread = threading.Thread(target=auto_mode_logic)
        auto_thread.start()
        return jsonify({"status": "success", "mode": "auto"})
    else:
        auto_mode = False
        if auto_thread:
            auto_thread.join()
        return jsonify({"status": "success", "mode": "manual"})


@app.route('/update_position')
def update_position():
    return jsonify(robot_position)


def gen_frames():
    cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
    frame_count = 0
    start_time = time()

    while True:
        success, frame = cap.read()
        if not success:
            break

        # Tính FPS
        frame_count += 1
        elapsed_time = time() - start_time
        fps = frame_count / elapsed_time if elapsed_time > 0 else 0

        # Hiển thị FPS lên khung hình
        cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Encode frame thành JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        GPIO.cleanup()
