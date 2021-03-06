import argparse
import os
import math
from typing import List, Tuple
import numpy as np
from Plotter import Plotter
from shapely.geometry.polygon import Polygon, LineString
from itertools import combinations
from dijkstra import Graph, dijsktra
# from collections import defaultdict

def shrink_polygon(p: Polygon, rate = 0.99) -> Polygon:
    translated_vertices = [(np.array(v) - np.array(p.centroid)) for v in p.exterior.coords]
    scaled_vertices = [item*rate for item in translated_vertices]
    retranslated_vertices = [(item + np.array(p.centroid)) for item in scaled_vertices]
    return Polygon(retranslated_vertices)


def get_minkowsky_sum(original_shape: Polygon, r: float) -> Polygon:
    """
    Get the polygon representing the Minkowsky sum
    :param original_shape: The original obstacle
    :param r: The radius of the rhombus
    :return: The polygon composed from the Minkowsky sums
    """

    # find all vertices of Minkowski sum of obsticle with robot
    # (we can use .convex_hull attribute of Polygon for reducing number of points to calculate)
    # original_vertices = [x for x in original_shape.exterior.coords]
    original_vertices = [x for x in original_shape.convex_hull.exterior.coords]
    minkowski_vertices = []
    for x, y in original_vertices:
        #TODO: is it r or sqrt(2)*r?
        minkowski_vertices.append([x, y + r])
        minkowski_vertices.append([x, y - r])
        minkowski_vertices.append([x + r, y])
        minkowski_vertices.append([x - r, y])

    # once points are obtained we can create and return a new polygon
    convex_hull_minkowski = [x for x in Polygon(minkowski_vertices).convex_hull.exterior.coords]
    return Polygon(convex_hull_minkowski)


def get_visibility_graph(obstacles: List[Polygon], source=None, dest=None) -> List[LineString]:
    """
    Get The visibility graph of a given map
    :param obstacles: A list of the obstacles in the map
    :param source: The starting position of the robot. None for part 1.
    :param dest: The destination of the query. None for part 1.
    :return: A list of LineStrings holding the edges of the visibility graph
    """

    vertices = []
    line_strings = []
    if source and dest:
        vertices += [source, dest]
    for o in obstacles:
        vertices += list(o.exterior.coords)
    scaled_obstacles = [shrink_polygon(o) for o in obstacles]
    for v1, v2 in combinations(vertices, 2):
        new_edge = LineString([v1, v2])
        edge_not_intersecting = True
        for o in scaled_obstacles:
            if not(o.intersection(new_edge).is_empty):
                edge_not_intersecting = False
                break
        if edge_not_intersecting:
            line_strings.append(new_edge)

    return line_strings


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)


def get_points_and_dist(line):
    source, dist = line.split(' ')
    dist = float(dist)
    source = tuple(map(float, source.split(',')))
    return source, dist


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("Robot",
                        help="A file that holds the starting position of the robot, and the distance from the center of the robot to any of its vertices")
    parser.add_argument("Obstacles", help="A file that contains the obstacles in the map")
    parser.add_argument("Query", help="A file that contains the ending position for the robot.")
    args = parser.parse_args()
    obstacles = args.Obstacles
    robot = args.Robot
    query = args.Query
    is_valid_file(parser, obstacles)
    is_valid_file(parser, robot)
    is_valid_file(parser, query)
    workspace_obstacles = []
    with open(obstacles, 'r') as f:
        for line in f.readlines():
            points = [tuple(map(float, t.split(','))) for t in line.replace('\n', '').split(' ')]
            workspace_obstacles.append(Polygon(points))
    with open(robot, 'r') as f:
        source, dist = get_points_and_dist(f.readline())

    # step 1:
    c_space_obstacles = [get_minkowsky_sum(p, dist) for p in workspace_obstacles]
    plotter1 = Plotter()

    plotter1.add_obstacles(workspace_obstacles)
    plotter1.add_c_space_obstacles(c_space_obstacles)
    plotter1.add_robot(source, dist)

    plotter1.show_graph()

    # step 2:

    lines = get_visibility_graph(c_space_obstacles)
    plotter2 = Plotter()

    plotter2.add_obstacles(workspace_obstacles)
    plotter2.add_c_space_obstacles(c_space_obstacles)
    plotter2.add_visibility_graph(lines)
    plotter2.add_robot(source, dist)

    plotter2.show_graph()

    # step 3:
    with open(query, 'r') as f:
        dest = tuple(map(float, f.readline().split(',')))

    lines = get_visibility_graph(c_space_obstacles, source, dest)
    # TODO: fill in the next line
    graph = Graph()
    for l in lines:
        graph.add_node(l.coords[0])
        graph.add_node(l.coords[1])
        graph.add_edge(l.coords[0], l.coords[1], l.length)
        graph.add_edge(l.coords[1], l.coords[0], l.length)
    visited, path = dijsktra(graph, source)
    shortest_path = []
    curr = dest
    while True:
        shortest_path.insert(0, curr)
        if curr == source:
            break
        curr = path[curr]

    cost = visited[dest]
    # shortest_path, cost = None, None
    
    plotter3 = Plotter()
    plotter3.add_robot(source, dist)
    plotter3.add_obstacles(workspace_obstacles)
    plotter3.add_robot(dest, dist)
    plotter3.add_visibility_graph(lines)
    plotter3.add_shorterst_path(list(shortest_path))

    plotter3.show_graph()
