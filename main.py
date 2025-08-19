from gsolver.logger import logger
from gsolver.shapes import Point, Edge, Enviroment, Triangle


class Interpreter:
	def __init__(self, env: Enviroment, commands: list[str]):
		self.env = env
		self.read(commands)

	def read(self, commands: list[str]):
		for command in commands:
			logger.info(f"Reading command: {command}")
			tokens = command.split()
			if len(tokens) > 1:
				if tokens[0] == "Point":
					self.point(tokens[1])
				elif tokens[0] == "Edge":
					self.edge(tokens[1])
				elif tokens[0] == "Triangle":
					self.triangle(tokens[1])
				else:
					logger.error(tokens[1])
			self.env.display()

	def point(self, p_name) -> Point:
		p = self.env.search(Point, p_name)
		if p is None:
			p = Point(self.env)
			p.name = p_name
		return p

	def edge(self, edge_name):
		e = self.env.search(Edge, edge_name)
		if e is None:
			points = edge_name.split('-')
			if len(points) > 2:
				raise Exception("Invalid Edge name")
			p1 = self.point(points[0])
			p2 = self.point(points[1])
			e = p1.connect(p2)
		return e

	def triangle(self, triangle_name):
		t = self.env.search(Triangle, triangle_name)
		if t is None:
			points = triangle_name.split('-')
			if len(points) > 3:
				raise Exception("Invalid Edge name")
			p1 = self.point(points[0])
			p2 = self.point(points[1])
			p3 = self.point(points[2])
			t = Triangle(self.env, p1, p2, p3)
		return t


def main(commands):
	env: Enviroment = Enviroment()
	Interpreter(env, commands)

# p4 = Point(env)
# t2 = Triangle(env, p1, p2, p4)
# env.display()


if __name__ == '__main__':
	commands = ["Point A", "Point B", "Edge A-B", "Point C", "Edge C-A", "Edge C-B", "Point D", "Triangle A-B-D"]
	main(commands)
