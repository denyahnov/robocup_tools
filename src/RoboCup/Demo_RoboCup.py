#!/usr/bin/env python3

import RoboCup as rc
from RoboCup.Menu import MenuButton,Menu

from time import sleep

robot = rc.Robot()

robot.Color('ORANGE')

robot.PrintPorts()

def close_menu_function():
	raise KeyboardInterrupt

def calibrate_function():
	robot.Color('RED')

	sleep(1)

	robot.sound.set_volume(20)
	robot.sound.play_tone(650,0.3,0,20,sound.PLAY_NO_WAIT_FOR_COMPLETE)
	robot.Color('ORANGE')

buttons = [
	MenuButton("Run Program"),
	MenuButton("Calibrate",script=calibrate_function),
	MenuButton("Connect Bluetooth"),
	MenuButton("Exit",script=close_menu_function),
]

menu = Menu([2,2],buttons)

menu.Run()

robot.CoastMotors()
robot.Color('GREEN')