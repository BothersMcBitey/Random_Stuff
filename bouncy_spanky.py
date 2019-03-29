# Brandon Mills Lab 8

from tkinter import *	 
import time
from collections import namedtuple
from random import randrange, uniform
import math
import winsound

class Vector2D():
	def __init__(self, x, y):
		self.x = x
		self.y = y
		
	def __add__(self, other):
		x = self.x + other.x
		y = self.y + other.y
		return Vector2D(x, y)
		
	def __sub__(self, other):
		x = self.x - other.x
		y = self.y - other.y
		return Vector2D(x, y)
		
	def __mul__(self, other):
		if type(other) is Vector2D:
			return self.cross(other)
		elif type(other) is float or type(other) is int:
			x = self.x * other
			y = self.y * other
			return Vector2D(x, y)
	
	def __truediv__(self, other):
		if type(other) is Vector2D:
			raise NotImplementedError
		elif type(other) is float or type(other) is int:
			x = self.x / other
			y = self.y / other
			return Vector2D(x, y)
			
	def __str__(self):
		return "[" + str(self.x) + ", " + str(self.y) + "]"
			
	def cross(self, other):
		raise NotImplementedError
		
	def dot(self, other):
		return self.x * other.x + self.y * other.y
		
	def squareDist(self, other):
		if type(other) is not Vector2D:
			raise Exception("Can't find distance between vector and non-vector")
		return ((self.x-other.x)**2 + (self.y-other.y)**2)
		
	def squareMagnitude(self):
		return ((self.x)**2 + (self.y)**2)
		
	def magnitude(self):
		return self.squareMagnitude() ** 0.5
		
	def normalised(self):
		return self / (self.squareMagnitude())**0.5
	
	def angleRad(self):
		return math.atan(self.y/self.x)
	
	def RandomDirection():
		x = uniform(-1,1)
		y = uniform(-1,1)
		return Vector2D(x,y).normalised()

	
		
class BouncingBall():

	ballcount = 0
	massConstant = 1

	def __init__(self, x, y, r=10, speed=1, start_dir=Vector2D(1,-1)):	   
		self.pos = Vector2D(x,y)
		self.radius = r
		self.mass = 3.14 * self.radius ** 2 * BouncingBall.massConstant

		self.xPos0 = x - r
		self.xPos1 = x + r
		self.yPos0 = y - r
		self.yPos1 = y + r
		
		self.direction = start_dir * speed
		self.notified_move_update = None

		self.ballID = 1
		self.UUID = BouncingBall.ballcount
		BouncingBall.ballcount += 1		
		
		registerCollider(self)
		self.unhandledCollisions = []
		
		self.isSquish = False
		self.squishFrame = 0
		

	def updatePhys(self, bounds):		
		#print(str(self.UUID) + " moving...")
		self.move()
		#print(str(self.UUID) + " bouncing...")
		self.bounceStatic(bounds)
		#print(str(self.UUID) + " colliding...")
		self.collide()		
		#print(str(self.UUID) + " squishing...")
		self.squish()

	def move(self):
		if self.notified_move_update is not None:
			self.direction = self.notified_move_update
		self.pos = self.pos + self.direction
		self.xPos0 = self.pos.x - self.radius
		self.xPos1 = self.pos.x + self.radius
		self.yPos0 = self.pos.y - self.radius
		self.yPos1 = self.pos.y + self.radius
		#if self.UUID == 1:
	#		print("pos:" + str(self.pos) + ", x0:" + str(self.xPos0) + ", x1:" + str(self.xPos1) + ", y0:" + str(self.yPos0) + ", y1:" + str(self.yPos1))
	#		print("dir:" + str(self.direction))
	
	def notifyCollision(self, col):
		if col not in self.unhandledCollisions:
			self.unhandledCollisions.append(col)
	
	
	def collide(self):
		#check for all collisions
		for other in [x for x in getOtherColliders(self) if x not in self.unhandledCollisions]:		
			if self.pos.squareDist(other.pos) <= (self.radius + other.radius)**2:
				self.notifyCollision(other)
				other.notifyCollision(self)
		
		#handle collisions
		if 0 < len(self.unhandledCollisions):
			shiftVec = Vector2D(0,0)
			for other in self.unhandledCollisions:
				#calc direction								
				transfer = (self.direction - (self.pos - other.pos) * ((2*other.mass / (other.mass + self.mass)) * 
					(self.direction - other.direction).dot(self.pos - other.pos) / (self.pos - other.pos).squareMagnitude()))
				
				
					
				shiftVec += transfer#Vector2D(transferX, transferY)
			self.notified_move_update = shiftVec
			self.unhandledCollisions.clear()
	
	def bounceStatic(self, bounds):
		if self.pos.x - self.radius <= 0 and self.direction.x < 0:			
			self.direction.x = -self.direction.x	
		elif self.pos.x + self.radius >= bounds.windowWidth and self.direction.x > 0:
			self.direction.x = -self.direction.x	
		if self.pos.y - self.radius <= 0 and self.direction.y < 0:
			self.direction.y = -self.direction.y
		elif self.pos.y + self.radius >= bounds.windowHeight and self.direction.y > 0:
			self.direction.y = -self.direction.y

	def draw(self, canvas):
		canvas.delete(self.ballID)
		tag = "ball" + str(self.UUID)
		#print(str(self.UUID) + " drawing...")
		canvas.create_oval(self.xPos0, self.yPos0, self.xPos1, self.yPos1, fill="blue", tags=tag)
		self.ballID = canvas.find_withtag(tag)[0]	
		
	def bounce(self, bounds):
		if self.direction == "se":
			if self.xPos1 >= bounds.windowWidth:
				self.startSquish("right")
				self.direction = "sw"
			if self.yPos1 >= bounds.windowHeight:
				self.startSquish("down")
				self.direction = "ne"
		if self.direction == "sw":
			if self.xPos0 <= 0:
				self.startSquish("left")
				self.direction = "se"
			if self.yPos1 >= bounds.windowHeight:
				self.startSquish("down")
				self.direction = "nw"
		if self.direction == "ne":
			if self.xPos1 >= bounds.windowWidth:
				self.startSquish("right")
				self.direction = "nw"
			if self.yPos0 <= 0:
				self.startSquish("up")
				self.direction = "se"
		if self.direction == "nw":
			if self.xPos0 <= 0:
				self.startSquish("left")
				self.direction = "ne"
			if self.yPos0 <= 0:
				self.startSquish("up")
				self.direction = "sw"


	def startSquish(self, direction):
		if not self.isSquish:
			self.isSquish = True
			self.squishFrame = 0
			self.bounceDir = direction
	
	def squish(self):
		if self.isSquish:
			if self.squishFrame < 3:
				if self.bounceDir == "right":
					self.xPos0 = self.xPos0 + 4
					self.yPos0 = self.yPos0 - 2
					self.yPos1 = self.yPos1 + 2
				elif self.bounceDir == "left":
					self.xPos1 = self.xPos1 - 4
					self.yPos0 = self.yPos0 - 2
					self.yPos1 = self.yPos1 + 2
				elif self.bounceDir == "up":
					self.yPos1 = self.yPos1 - 4
					self.xPos0 = self.xPos0 - 2
					self.xPos1 = self.xPos1 + 2
				elif self.bounceDir == "down":
					self.yPos0 = self.yPos0 + 4
					self.xPos0 = self.xPos0 - 2
					self.xPos1 = self.xPos1 + 2
				self.squishFrame += 1
			elif self.squishFrame < 6:
				if self.bounceDir == "right":
					self.xPos0 = self.xPos0 - 4
					self.yPos0 = self.yPos0 + 2
					self.yPos1 = self.yPos1 - 2
				elif self.bounceDir == "left":
					self.xPos1 = self.xPos1 + 4
					self.yPos0 = self.yPos0 + 2
					self.yPos1 = self.yPos1 - 2
				elif self.bounceDir == "up":
					self.yPos1 = self.yPos1 + 4
					self.xPos0 = self.xPos0 + 2
					self.xPos1 = self.xPos1 - 2
				elif self.bounceDir == "down":
					self.yPos0 = self.yPos0 - 4
					self.xPos0 = self.xPos0 + 2
					self.xPos1 = self.xPos1 - 2
				self.squishFrame += 1
			else:
				self.isSquish = False
				self.squishFrame = 0

class BallFrame(Frame):
	def __init__(self):	   
		Frame.__init__(self)	
	
		self.master.title("Bouncing Ball CSC-131 Lab 7")	
	
		self.grid()	   

		self.windowWidth = 1920
		self.windowHeight = 1080
	
		self.canvas = Canvas(self, bg = "white", width = self.windowWidth, height = self.windowHeight, bd=0, highlightthickness=0, relief="ridge")
		self.canvas.grid(row = 0, column = 0)	 
		
		self.balls = []

	def updateContents(self):		
		Bounds = namedtuple("Bounds", ['windowWidth', 'windowHeight'])
		self.update()
		for ball in self.balls:
			ball.updatePhys((Bounds(self.windowWidth, self.windowHeight)))
		for ball in self.balls:
			ball.draw(self.canvas)		

			
	def addBall(self, ball):
		self.balls.append(ball)

		
##global because I'm lazy
colliders = []
def registerCollider(col):
	global colliders
	if col not in colliders:
		colliders.append(col)
		
def getOtherColliders(col):
	global colliders
	if col in colliders:
		return [x for x in colliders if x != col]
	else:
		return colliders.copy()
		
		
def main():
	frame = BallFrame()
	bb = BouncingBall(0,0)
	frame.addBall(bb)
	for i in range(0, 100):
		x = randrange(0, 750)
		y = randrange(0, 350)
		r = randrange(3, 10) 
		s = randrange(1, 5)
		dir = Vector2D.RandomDirection()
		frame.addBall(BouncingBall(x, y, r=r, speed=s, start_dir=dir))
	while True:
		frame.updateContents()
		time.sleep(0.015)

main()	
