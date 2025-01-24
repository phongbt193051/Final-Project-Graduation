import RPi.GPIO as GPIO
from time import sleep


in1_motor1 = 24
in2_motor1 = 23
en_motor1 = 25


in1_motor2 = 22
in2_motor2 = 27
en_motor2 = 17


sensor_left = 19
sensor_right = 6

GPIO.setmode(GPIO.BCM)


GPIO.setup(in1_motor1, GPIO.OUT)
GPIO.setup(in2_motor1, GPIO.OUT)
GPIO.setup(en_motor1, GPIO.OUT)


GPIO.setup(in1_motor2, GPIO.OUT)
GPIO.setup(in2_motor2, GPIO.OUT)
GPIO.setup(en_motor2, GPIO.OUT)


GPIO.setup(sensor_left, GPIO.IN)
GPIO.setup(sensor_right, GPIO.IN)


GPIO.output(in1_motor1, GPIO.LOW)
GPIO.output(in2_motor1, GPIO.LOW)
GPIO.output(in1_motor2, GPIO.LOW)
GPIO.output(in2_motor2, GPIO.LOW)


pwm_motor1 = GPIO.PWM(en_motor1, 1000)  
pwm_motor2 = GPIO.PWM(en_motor2, 1000)


pwm_motor1.start(40)
pwm_motor2.start(40)


speed = 40


def set_speed(new_speed):
    global speed
    speed = new_speed
    pwm_motor1.ChangeDutyCycle(speed)
    pwm_motor2.ChangeDutyCycle(speed)


def move_forward():
    GPIO.output(in1_motor1, GPIO.HIGH)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.HIGH)
    GPIO.output(in2_motor2, GPIO.LOW)
    print("Moving forward")


def move_backward():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.HIGH)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.HIGH)
    print("Moving backward")


def turn_left():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.HIGH)
    GPIO.output(in1_motor2, GPIO.HIGH)
    GPIO.output(in2_motor2, GPIO.LOW)
    print("Turning left")


def turn_right():
    GPIO.output(in1_motor1, GPIO.HIGH)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.HIGH)
    print("Turning right")


def stop_motors():
    GPIO.output(in1_motor1, GPIO.LOW)
    GPIO.output(in2_motor1, GPIO.LOW)
    GPIO.output(in1_motor2, GPIO.LOW)
    GPIO.output(in2_motor2, GPIO.LOW)
    print("Stopping motors")


try:
    while True:
        
        left = GPIO.input(sensor_left)  
        right = GPIO.input(sensor_right)  

        print(f"Sensor Left: {left}, Sensor Right: {right}")

        
        if left == GPIO.HIGH and right == GPIO.HIGH:
            move_forward()  
        elif left == GPIO.LOW and right == GPIO.HIGH:
            turn_left()  
        elif left == GPIO.HIGH and right == GPIO.LOW:
            turn_right()  
        elif left == GPIO.LOW and right == GPIO.LOW:
            stop_motors()  

        
        sleep(0.01)

except KeyboardInterrupt:
    print("\nProgram interrupted by user.")
    GPIO.cleanup()
