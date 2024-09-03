# define distance heuristics here
import math


# euclidean distance
def euclidean_distance(p1, p2):
    """
    euclidean distance or l2 norm, distance between two points in euclidean space
    """
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


# manhattan distance
def manhattan_distance(p1, p2):
    """
    manhattan distance | l1 norm
    city-block style distance between two points
    """
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])
