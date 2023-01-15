from ev3dev2.button import Button
from ev3dev2.sound import Sound
from ev3dev2.led import Leds
from ev3dev2.motor import SpeedPercent

from math import sin, cos, tan

# ev3dev API Reference:
# https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/spec.html
# 
# RoboCup Module Example
# ExampleProject()


class Driver:
	IR_SENSOR = "ht-nxt-ir-seek-v2"
	COMPASS_SENSOR = "ht-nxt-compass"

def Unpack(values) -> list:
	for item in values:
		try:
			yield from Unpack(item)
		except TypeError:
			yield item

def Average(values) -> float:
	return sum(values) / len(values)

class Clamper():
	def __init__(self,min_value: int,max_value: int) -> None:
		self.min_value = min_value; self.max_value = max_value

	def Clamp(self,values: int or list[int]) -> list[int]:
		values = list(Unpack(values))
		clamped = [None] * len(values)

		for i,value in enumerate(values):
			if value < self.min_value: value = self.min_value
			if value > self.max_value: value = self.max_value

			clamped[i] = value

		return clamped

class PID_Controller():
	def __init__(self,p,i,d) -> None:
		self.kp = p; self.ki = i; self.kd = d;

		self.reset()

	def reset(self) -> None:
		self.last_error = 0

	def update(self,value: float) -> float:
		error = value - self.last_error

		p = self.kp * value
		i = value * error
		d = error

		return p + (self.ki * i) + (self.kd * d)

class FilteredSensor():
	def __init__(self,difference: int = 200, outliers: int = 15) -> None:
		self.stored = []
		self.counter = 0

		self.difference = difference
		self.outliers = outliers

	def Value(self,value) -> float:
		if self.counter > self.outliers: self.stored = []

		if len(self.stored) == 0: 
			self.stored.append(value)

		change = abs(self.Average(self.stored) - value)

		if change >= self.difference:
			self.counter += 1
		else:
			self.stored.append(value)

		return self.Average(self.stored)

class Robot():
	def __init__(self) -> None:
		self.Port: dict = {
			"A": None,
			"B": None,
			"C": None,
			"D": None,
			"1": None,
			"2": None,
			"3": None,
			"4": None,
		}

		self.Leds = Leds()
		self.Sound = Sound()
		self.Buttons = Button()
		self.Speed = Clamper(-100,100)

	def CoastMotors(self) -> None:
		[self.Port[p].off(brake=False) for p in list("ABCD") if self.Port[p] != None]

	def Color(self,color) -> None:
		self.Leds.set_color('LEFT',color)
		self.Leds.set_color('RIGHT',color)

	def ScaleSpeeds(self,target_value:int,speeds:list[float]) -> list[float]:
		greatest = max([abs(speed) for speed in speeds])

		if greatest > target_value: greatest = target_value

		fix = target_value / greatest

		for i in range(len(speeds)):
			speeds[i] = round(speeds[i] * fix,2)

		return speeds

	def PrintPorts(self) -> None:
		print('\n'.join([self.Port[x] != None for x in self.Ports]))

	def AngleToXY(self,angle,speed) -> tuple[float]:
		x = speed * cos(angle)
		y = speed * sin(angle)

		return (x,y)

	def StartMotors(self,speeds) -> None:
		speeds = Unpack(speeds)
		for p in list("ABCD"):
			if self.Port[p] != None:
				self.Port[p].on(SpeedPercent(self.Speed.Clamp(speeds[0])))
				if len(speeds) > 1: speeds.pop(0)

	def SmoothAngle(self,current: float,target: float,smoothing: float=1.25) -> float:
		diff = abs(current - target)
		if diff > 270: diff -= 270

		diff /= smoothing

		if current - smoothing / 2 < target: 
		    return current + diff
		elif current + smoothing / 2 > target: 
		    return current - diff

		return current

def ExampleProject() -> None:
	with open("Demo_RoboCup.py","w+") as file:
		file.write("""import RoboCup as rc
from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C
from ev3dev2.sensor import Sensor, INPUT_1, INPUT_2, INPUT_3
from ev3dev2.sensor.lego import ColorSensor, UltrasonicSensor

robot = rc.Robot()

robot.Port['B'] = LargeMotor(OUTPUT_B)
robot.Port['C'] = LargeMotor(OUTPUT_C)

robot.Port['1'] = ColorSensor(INPUT_1)
robot.Port['2'] = UltrasonicSensor(INPUT_2)
robot.Port['3'] = Sensor(INPUT_3,driver_name=rc.Driver.IR_SENSOR)

filtered_ultrasonic = rc.FilteredSensor()

robot.Color('RED')

robot.PrintPorts()

try:
	while not robot.Buttons.any:
		color = self.Port['1'].rgb()
		distance = filtered_ultrasonic.Value(robot.Port['2'].distance_centimeters)

		if rc.Average(color) < 100:
			robot.StartMotors([50,-50])
		else:
			robot.StartMotors(50)
except KeyboardInterrupt:
	print("Interrupted")

robot.CoastMotors()
robot.Color('GREEN')""")

if __name__ == '__main__':
	ExampleProject()
