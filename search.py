# define search algorithms here
import time
from GraphNode import Graph, Node
from queue import PriorityQueue
import itertools


def build_min_path(curr: Node):
    path = [curr]
    while curr.parent:
        curr = curr.parent
        path.append(curr)
    path.reverse()
    return path


def get_path_info(curr):
    node_path = [curr.label]
    edge_path = []
    weights = []
    obstacles = []
    landmarks = []
    while curr.parent:
        edge = curr.preceding_edge
        curr = curr.parent
        node_path.append(curr.label)
        edge_path.append(edge["name"])
        weights.append(edge["weight"])
        obstacles.extend(edge["obstacles"])
        landmarks.extend(edge["landmarks"])

    return {
        "nodes": node_path[::-1],
        "edges": edge_path[::-1],
        "path": get_joined_path(node_path, edge_path)[::-1],
        "weights": weights[::-1],
        "obstacles": obstacles[::-1],
        "landmarks": landmarks[::-1],
        "total_weight": sum(weights),
        "time": 0,
    }


def get_joined_path(nodes: list[str], edges: list[str]):
    """returns an array of nodes followed on the path interspersed with the
    edges between them. Main component is achieved using generator object
    returned by join_path"""
    return [x for x in join_path(nodes, edges)]


def join_path(nodes: list[str], edges: list[str]):
    """bit of generator magic to intersperse the"""
    node_iter = iter(nodes)
    edge_iter = iter(edges)
    yield next(node_iter)
    for node in node_iter:
        yield f"{next(edge_iter)}"
        yield node


def aSTAR_helper(start: Node, end: Node):
    open = PriorityQueue()

    # counter for prio queue consistency
    # discovered this one while implementing CONTRACTION
    # HIERARCHIES
    counter = itertools.count()
    start.g = 0  # g(n) is cost of path so far to reach n
    start.f = start.h  # f(n) = g(n) + h(n)
    open.put((start.f, next(counter), start))

    while not open.empty():
        _, _, curr = open.get()
        if curr == end:
            return curr

        for edge in curr.get_out_edges():
            g_temp = curr.g + edge["weight"]
            neighbour = edge["endpoint"]
            if g_temp < neighbour.g:
                neighbour.parent = curr
                neighbour.preceding_edge = edge
                neighbour.g = g_temp
                neighbour.f = g_temp + neighbour.h
                if neighbour.status == "closed":
                    neighbour.status = "open"
                    open.put((neighbour.f, next(counter), neighbour))

    # goal was not reached
    return None


def aSTAR(G: Graph, start: Node, end: Node, heuristic: str):
    for node in G.nodes.values():
        node.h = node.calc_h(end, heuristic)

    start_time = time.perf_counter_ns()
    end_node = aSTAR_helper(start, end)
    end_time = time.perf_counter_ns()

    if end_node is None:
        return None

    path_info = get_path_info(end_node)
    path_info["time"] = abs(start_time - end_time) / 10000
    return path_info
