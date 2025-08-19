from typing import Optional

from .exceptions import AdditionError, BuildError
from .logger import logger
from .utils import classproperty, all_in_list


class GeomObject:
	def __init__(self, env: 'Enviroment', *components: tuple['GeomObject']):
		self.name: str = "NONE"
		logger.debug(f"Building {repr(self)} with {components}")
		self.env: Enviroment = env
		self.relations: dict[str, list[GeomObject]] = {}
		self.env.insert(self)
		if len(components) > 0:
			self.build(*components)
			self.add_check()
		logger.info(f"New object: {repr(self)}")

	def __str__(self) -> str:
		return f"{self.classname}({self.name}, {self.relations})"

	def __repr__(self) -> str:
		return f"{self.classname}({self.name})"

	@classproperty
	def classname(self) -> str:
		return self.__name__

	def ensure_class(self, obj: 'GeomObject') -> bool:
		if obj.classname not in self.relations:
			self.relations[obj.classname] = []
			return False
		else:
			return True

	def get_list(self, obj: 'GeomObject') -> list['GeomObject']:
		if obj.classname in self.relations:
			return self.relations[obj.classname]
		else:
			return []

	def insert(self, obj: 'GeomObject') -> 'GeomObject':
		self.ensure_class(obj)
		obj_list: list['GeomObject'] = self.get_list(obj)
		if obj not in obj_list:
			logger.info(f"Adding {repr(obj)} to {repr(self)}, is not in {obj_list}")
			obj_list.append(obj)
		return obj

	def add(self, obj: 'GeomObject') -> 'GeomObject':
		logger.debug(f"Adding {repr(obj)} to {repr(self)}")
		self.insert(obj)
		obj.insert(self)
		return obj

	def build(self):
		raise NotImplementedError

	def add_check(self):
		pass

	#
	# def find(self, *components: tuple['Object']) -> 'Object':
	# 	logger.debug(f"{repr(self)} looking for an object that has {components}...")
	# 	object_list: list[Object] = []
	# 	for component in components:
	# 		object_list += self.get_list(component)
	# 	# input(f"{repr(self)} has {object_list}...")
	# 	# for obj in object_list:
	# 	# 	same_class_components: list[Object] = []
	# 	# 	for component in components:
	# 	# 		same_class_components += component.get_list(component)
	# 	# 	input(f"Looking through {same_class_components}...")
	# 	# 	if all_in_list(components, same_class_components):
	# 	# 		input(f"Found {obj}")
	# 	# 		return obj
	# 	input(f"Found nothing")
	# 	return None

	def find_that_has(self, obj_class: 'GeomObject', *components: tuple['GeomObject']) -> Optional['GeomObject']:
		logger.debug(f"{repr(self)} looking for an object of class {obj_class.classname} that has {components}...")
		objects: list[GeomObject] = self.get_list(obj_class)
		for obj in objects:
			logger.debug(f"Knows {obj}...")
			inner_components: list[GeomObject] = []
			for component in components:
				for inner_component in obj.get_list(component):
					if inner_component not in inner_components:
						inner_components.append(inner_component)
			if all_in_list(components, inner_components):
				logger.debug(f"{obj} fits the description")
				return obj
		logger.debug(f"Found nothing")
		return None

	def build_if_has_not(self, obj_class: 'GeomObject', *components: tuple['GeomObject']) -> Optional['GeomObject']:
		obj: GeomObject = self.env.find_that_has(obj_class, *components)
		if obj is None:
			obj = obj_class(self.env, *components)
		return obj


class Point(GeomObject):
	# def is_connected(self, point: 'Point') -> bool:
	# 	logger.debug(f"Checking if {repr(self)} is connected to {repr(point)}")
	# 	if self.env.find(self, point):
	# 		return True
	# 	else:
	# 		return False

	def is_connected(self, point: 'Point') -> Optional['Edge']:
		edges: list[Edge] = self.env.get_list(Edge)
		for edge in edges:
			points: list[Point] = edge.get_list(Point)
			if self in points and point in points:
				return edge
		return None

	# def connect(self, point: 'Point') -> 'edge':
	# 	edge: edge = self.env.find(self, point)
	# 	if edge is None:
	# 		edge: edge = edge(self.env, self, point)
	# 	return edge

	def connect(self, point: 'Point') -> 'Edge':
		edge: Edge = self.is_connected(point)
		if edge is None:
			edge: Edge = Edge(self.env, self, point)
		return edge


class Edge(GeomObject):
	def insert(self, point: Point) -> Point:
		if isinstance(point, Point) and len(self.get_list(Point)) == 2:
			raise AdditionError("How can a edge include more than two points?")
		super().insert(point)
		return point

	def build(self, *points):
		if len(points) != 2:
			raise BuildError("How can a edge not include two points?")
		for point in points:
			if not isinstance(point, Point):
				raise BuildError("Trying to build not with points!")
			self.add(point)
		points[0].connect(points[1])
		self.name = '-'.join([p.name for p in points])

	def is_connected_with_point(self, point: 'Point') -> Optional['Edge']:
		pass

	# edges: list[edge] = self.env.get_list(edge)
	# for edge in edges:
	# 	points: list[Point] = edge.get_list(Point)
	# 	if self in points and point in points:
	# 		return edge
	# return None

	def add_check(self):
		logger.debug(f"{repr(self)} Self-check...")
		self_points: list[Point] = self.get_list(Point)
		logger.debug(f"{repr(self)} has points {self_points}...")
		if len(self_points) < 2:
			return
		edges2: list[Edge] = []
		for point in self_points:
			for edge in point.get_list(Edge):
				if edge != self:
					edges2.append(edge)
		logger.debug(f"{repr(self)} has neighbours {edges2}...")
		self.look_build_angles(self_points, edges2)
		self.look_build_triangle(self_points, edges2)

	def look_build_angles(self, self_points, edges2):
		for edge in edges2:
			for point in edge.get_list(Point):
				if point in self_points:
					self.build_if_has_not(Angle, point, self, edge)

	def look_build_triangle(self, self_points, edges2):
		points_paths: list[tuple[Edge, Point]] = []
		for edge in edges2:
			for point in edge.get_list(Point):
				if point not in self_points:
					points_paths.append((edge, point))
		points2: list[Point] = [points_path[1] for points_path in points_paths]
		logger.debug(f"{repr(self)} has second-neighbour points {points2}...")
		for point in list(set(points2)):
			if points2.count(point) == 2:
				reach_edges: list[Edge] = []
				reach_points: list[Point] = []
				for points_path in points_paths:
					if points_path[1] == point:
						reach_points.append(points_path[1])
						reach_edges.append(points_path[0])
				logger.debug(f"Two paths from {repr(self)} to {repr(point)} with {reach_points} then {reach_edges}, forming a Triangle")
				edge_a, edge_b = tuple(reach_edges)
				point_a, point_b = tuple(reach_points)
				triangle_by_edges: Triangle = self.env.find_that_has(Triangle, self, edge_a, edge_b)
				triangle_by_points: Triangle = self.env.find_that_has(Triangle, point, point_a, point_b)
				if triangle_by_edges is None and triangle_by_points is None:
					Triangle.build_with_edges(self.env, self, edge_a, edge_b)


class Angle(GeomObject):
	def __init__(self, env: 'Enviroment', *components: tuple['GeomObject']):
		super().__init__(env, *components)
		self.value: Optional[float] = None

	def build(self, point: Point, edge_a: Edge, edge_b: Edge):
		if not isinstance(point, Point):
			raise BuildError
		for edge in [edge_a, edge_b]:
			if not isinstance(edge, Edge):
				raise BuildError
		self.add(point)
		self.add(edge_a)
		self.add(edge_b)
		a_points = [p.name for p in edge_a.get_list(Point) if p != point]
		b_points = [p.name for p in edge_b.get_list(Point) if p != point]
		points = a_points + [point.name] + b_points
		self.name = ''.join(points)

	def assess(self):
		pass


# TODO: If three edges share a point, either the sum of two angles equals the third, or the three angles equal 360. This also makes the figure ambigious between a larger triangle and a quadrilateral.
# TODO: If three edges form a triangle, the sum of their angles should be 180


class Triangle(GeomObject):

	def build(self, point_a: Point, point_b: Point, point_c: Point):
		for point in [point_a, point_b, point_c]:
			if not isinstance(point, Point):
				raise BuildError("Trying to build not with points!")
			self.add(point)
		edge_a: Edge = point_a.connect(point_b)
		edge_b: Edge = point_b.connect(point_c)
		edge_c: Edge = point_c.connect(point_a)
		self.add(edge_a)
		self.add(edge_b)
		self.add(edge_c)
		self.name = '-'.join([p.name for p in [point_a, point_b, point_c]])

	@classmethod
	def build_with_edges(cls, env: 'Enviroment', edge_a: Edge, edge_b: Edge, edge_c: Edge):
		for edge in [edge_a, edge_b, edge_c]:
			if not isinstance(edge, Edge):
				raise BuildError("Trying to build not with edges!")
		points: list[Point] = list(set(edge_a.get_list(Point) + edge_b.get_list(Point) + edge_c.get_list(Point)))
		return cls(env, *points)

	def add_check(self):
		logger.debug(f"{repr(self)} Self-check...")
		edges: list[Edge] = self.get_list(Edge)
		for edge1 in edges:
			for edge2 in edges:
				if edge1 != edge2:
					for point1 in edge1.get_list(Point):
						for point2 in edge2.get_list(Point):
							if point1 == point2:
								angle: Angle = self.build_if_has_not(Angle, point1, edge1, edge2)
								self.add(angle)


class Enviroment(GeomObject):
	# noinspection PyMissingConstructor
	def __init__(self):
		self.name: str = "ENV"
		self.relations: dict[str, list[GeomObject]] = {}
		logger.info(f"New ENV: {repr(self)}")

	def display(self):
		logger.info(f"==={repr(self)}===")
		for classname, obj_list in self.relations.items():
			logger.info(f"-{classname}s:")
			for obj in obj_list:
				logger.info(f"--{obj}")
		logger.info(f"======")

	def insert(self, obj: 'GeomObject') -> GeomObject:
		super().insert(obj)
		obj.name = str(len(self.get_list(obj)))
		return obj

	def search(self, objclass: GeomObject, name: str):
		for clsname, objects in self.relations.items():
			for obj in objects:
				if clsname == objclass.classname and all_in_list(list(name), list(obj.name)):
					return obj
		return None
