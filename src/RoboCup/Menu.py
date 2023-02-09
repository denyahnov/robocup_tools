#!/usr/bin/env python3

from time import sleep

from ev3dev2.button import Button
from ev3dev2.display import Display

class MenuButton():
	def __init__(self,text:str="",icon:list=None,script:...=None):
		self.text = text
		self.icon = icon
		
		self.script = script

	def draw(self,display:Display,position=[],fill=None,button_size=[]):
		display.draw.rectangle(xy=position,fill='black' if fill else 'white')

		display.draw.text(
			text=self.text.replace(' ','\n'),
			xy=[
					position[0] + (button_size[0]//2)  - (max([len(t) for t in self.text.split(' ')])*3.25),
					position[1] + (button_size[1]//2) - (len(self.text.split(' '))*6)
				],
			fill='white' if fill else 'black',
			align='center'
		)

class Menu():
	def __init__(self,menu_size:list,buttons:list,cursor_pos:list=[0,0]):
		self.menu_size = menu_size
		self.menu_buttons = buttons
		self.cursor_pos = cursor_pos

		self.display = Display()
		self.buttons = Button()

		self.x, self.y = self.display.xres, self.display.yres
		self.button_size = [self.x/self.menu_size[0],self.y/self.menu_size[1]]

		self.RUNNING = True

	def Draw(self) -> None:
		for index,button in enumerate(self.menu_buttons):
			button.draw(
				self.display,
				position=self.GetButtonPosition(index),
				fill=self.GetTrueIndex(index) == self.cursor_pos,
				button_size=self.button_size
			)

	def Run(self) -> None:
		print("Custom Menu Running")

		self.display.clear()
		self.Draw()
		self.display.update()

		while self.RUNNING:
			try:
				if self.buttons.backspace: 
					raise KeyboardInterrupt

				if self.buttons.right and self.cursor_pos[0] < self.menu_size[0] - 1:
					self.cursor_pos[0] += 1
				if self.buttons.left and self.cursor_pos[0] > 0:
					self.cursor_pos[0] -= 1
				if self.buttons.up and self.cursor_pos[1] > 0:
					self.cursor_pos[1] -= 1
				if self.buttons.down and self.cursor_pos[1] < self.menu_size[1] - 1:
					self.cursor_pos[1] += 1

				if self.buttons.enter:
					script = self.menu_buttons[self.cursor_pos[0] + (self.menu_size[0] * self.cursor_pos[1])].script

					while self.buttons.enter:
						self.buttons.process()
						sleep(0.01)

					if callable(script): script()

				self.Draw()

				self.display.update()

				self.buttons.process()

				self.buttons.wait_for_released(self.buttons.buttons_pressed)

				self.display.clear()

			except KeyboardInterrupt:
				print("Custom Menu Closed")

				self.display.clear()

				self.RUNNING = False

	def GetTrueIndex(self,index:int) -> list:
		return [index - (index // self.menu_size[1]) * self.menu_size[0], index // self.menu_size[1]]

	def GetButtonPosition(self,index:int) -> list:
		x, y = self.GetTrueIndex(index)
		pos = [self.button_size[0] * x,self.button_size[1] * y]
		return pos + [pos[0] + self.button_size[0],pos[1] + self.button_size[1]]

if __name__ == '__main__':
	def close_menu_function():
		raise KeyboardInterrupt

	buttons = [
		MenuButton("Run Program"),
		MenuButton("Calibrate"),
		MenuButton("Connect Bluetooth"),
		MenuButton("Exit",script=close_menu_function),
	]

	menu = Menu([2,2],buttons)

	menu.Run()