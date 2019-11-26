import argparse
import os
import math
from typing import List, Tuple

from Plotter import Plotter
from shapely.geometry.polygon import Polygon, LineString
from itertools import combinations


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

    added_line_strings = []

    """get lines between vertices of same obstacle"""
    for o in obstacles:
        for i in range(len(o.boundary.coords) - 1):
            added_line_strings.append(LineString([o.boundary.coords[i], o.boundary.coords[i + 1]]))

    for o1, o2 in combinations(range(len(obstacles)), 2):
        for v1 in obstacles[o1].boundary.coords:
            for v2 in obstacles[o2].boundary.coords:
                new_edge = LineString([v1, v2])
                no_intersection = True
                for edge in added_line_strings:
                    if edge.intersection(new_edge):
                        if edge.intersection(new_edge).coords[0] not in [v1, v2]:
                            """interdection found"""
                            no_intersection = False
                            break
                if no_intersection:
                    added_line_strings.append(new_edge)

    print()

    return added_line_strings


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
    shortest_path, cost = None, None

    plotter3 = Plotter()
    plotter3.add_robot(source, dist)
    plotter3.add_obstacles(workspace_obstacles)
    plotter3.add_robot(dest, dist)
    plotter3.add_visibility_graph(lines)
    plotter3.add_shorterst_path(list(shortest_path))

    plotter3.show_graph()
