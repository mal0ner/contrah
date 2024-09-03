from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypedDict
from heuristics import euclidean_distance, manhattan_distance
import math


@dataclass
class Graph:
    nodes: dict[str, Node]

    def add_node(self, key: str, node: Node) -> None:
        """add new node to graph node list"""
        self.nodes[key] = node

    def add_edge(
        self,
        v: Node,
        u: Node,
        name: str,
        weight: int,
        landmarks: list[str] | None = None,
        obstacles: list[str] | None = None,
    ) -> None:
        """add bi-directional weighted edge between graph vertexes"""
        if landmarks is None:
            landmarks = []
        if obstacles is None:
            obstacles = []
        v.add_neighbour(name, u, weight, landmarks, obstacles)
        u.add_neighbour(name, v, weight, landmarks, obstacles)

    def add_dir_edge(
        self,
        u: Node,
        v: Node,
        name: str,
        weight: int,
        landmarks: list[str] | None = None,
        obstacles: list[str] | None = None,
    ) -> None:
        """add uni-directional weighted edge between graph vertexes"""
        if landmarks is None:
            landmarks = []
        if obstacles is None:
            obstacles = []
        u.add_neighbour(name, v, weight, landmarks, obstacles)

    def remove_node(self, node: Node):
        outgoing_references = self.get_outgoing_neighbours_with_edges(node)
        incoming_references = self.get_incoming_neighbours_with_edges(node)
        for edge in outgoing_references.values():
            node.remove_incident_edge(edge)
        for src, edge in incoming_references.items():
            self.nodes[src].remove_incident_edge(edge)
        self.nodes.pop(node.label)

    def remove_edge(self, v: Node, u: Node) -> None:
        v.remove_neighbour(u)
        u.remove_neighbour(v)

    def get_edges(self) -> list[Node]:
        edges = []
        for node in self.nodes.values():
            edges.append(node.get_neighbours())
        return edges

    def get_incoming_neighbours_with_edges(self, node: Node):
        incoming = {}
        for n in self.nodes.values():
            out = self.get_outgoing_neighbours_with_edges(n)
            if node.label in out.keys():
                incoming[n.label] = out[node.label]
        return incoming

    def get_outgoing_neighbours_with_edges(self, node: Node):
        return {e["endpoint"].label: e for e in node.get_out_edges()}

    def reset_nodes(self):
        for node in self.nodes.values():
            node.h = math.inf
            node.g = math.inf
            node.f = math.inf
            node.parent = None
            node.preceding_edge = None
            node.status = "closed"

    def __repr__(self) -> str:
        graphString = ""
        graphString += f"============={self.__class__} =============\n"
        for node in self.nodes.values():
            nbors = [e["endpoint"].label for e in node.get_out_edges()]
            graphString += f"{node.label}->({', '.join(nbors)})\n"
        return graphString


@dataclass
class Node:
    label: str
    x: int
    y: int
    h: float = math.inf
    g: float = math.inf
    f: float = math.inf
    parent: None | Node = None
    preceding_edge: NodeEdge | None = None
    neighbours: list = field(default_factory=list)
    status: str = "closed"
    estD: float = math.inf  # for dijkstra's

    def get_pos(self) -> tuple[int, int]:
        """return cartesian coordinates (x, y) of node"""
        return self.x, self.y

    def add_neighbour(
        self, name: str, endpoint: Node, weight: int, landmarks=None, obstacles=None
    ) -> None:
        if not landmarks:
            landmarks = []
        if not obstacles:
            obstacles = []
        """add new neighbour with weighted edge"""
        edge: NodeEdge = {
            "name": name,
            "weight": weight,
            "endpoint": endpoint,
            "landmarks": landmarks,
            "obstacles": obstacles,
        }
        self.neighbours.append(edge)

    def remove_neighbour(self, endpoint: Node) -> None:
        for edge in [e for e in self.neighbours if e["endpoint"] == endpoint]:
            self.neighbours.remove(edge)
        # edge_match = (e for e in self.neighbours if e["endpoint"] == endpoint)
        # self.neighbours.remove(next(edge_match))

    def remove_incident_edge(self, edge: NodeEdge):
        # matches = [e for e in self.neighbours if e == edge]
        # if len(matches) > 1:
        #     print("multiple matches found when removing edge")
        self.neighbours.remove(edge)

    def get_neighbours(self) -> list[Node]:
        """get list of valid neighbours"""
        return [
            n["endpoint"] for n in self.neighbours if n["endpoint"].status == "open"
        ]

    def get_out_edges(self) -> list[NodeEdge]:
        """get out-edge dicts for current node"""
        return [n for n in self.neighbours]

    def calc_h(self, goal: Node, h_type: str = "manhattan") -> float:
        """
        calculates the 'h-metric' or distance measure from node position
        to the defined goal node in the graph
        """
        if h_type == "euclidean":
            return euclidean_distance((self.x, self.y), (goal.x, goal.y))
        return manhattan_distance((self.x, self.y), (goal.x, goal.y))

    def __repr__(self) -> str:
        return f"<{self.label} {self.x} {self.y}>"


class NodeEdge(TypedDict):
    name: str
    weight: int
    endpoint: Node
    landmarks: list[str]
    obstacles: list[str]
