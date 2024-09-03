from GraphNode import Graph, Node

from search import aSTAR

# from contractionHierarchy import get_contraction_order
# from contractionHierarchy import build_g_prime
# from contractionHierarchy import query_graph
from contractionHierarchy import run_CH

nodes = {}

nodes_arr = [
    ["A", -38.1417, 145.1473],
    ["B", -38.1422, 145.1461],
    ["C", -38.1435, 145.1453],
    ["D", -38.1479, 145.1440],
    ["E", -38.1388, 145.1532],
    ["F", -38.1446, 145.1506],
    ["G", -38.1463, 145.1499],
    ["H", -38.1472, 145.1495],
    ["I", -38.1494, 145.1485],
    ["J", -38.1409, 145.1561],
    ["K", -38.1471, 145.1533],
    ["L", -38.1457, 145.1556],
    ["M", -38.1477, 145.1547],
    ["N", -38.1478, 145.1546],
    ["O", -38.1489, 145.1541],
    ["P", -38.1494, 145.1539],
    ["Q", -38.1516, 145.1529],
    ["R", -38.1483, 145.1563],
    ["S", -38.1433, 145.1600],
    ["T", -38.1486, 145.1573],
    ["U", -38.1497, 145.1568],
    ["V", -38.1464, 145.1648],
    ["W", -38.1486, 145.1638],
    ["X", -38.1469, 145.1652],
    ["Y", -38.1494, 145.1657],
    ["Z", -38.1512, 145.1652],
    ["AA", -38.1541, 145.1623],
    ["AB", -38.1548, 145.1697],
    ["AC", -38.1532, 145.1656],
    ["AD", -38.1421, 145.1582],
    ["AE", -38.1499, 145.1656],
]


edges_arr = [
    ["A", "B", "ashleigh", 120],
    ["A", "E", "ashleigh", 740],
    ["A", "J", "brentwood", 920],
    ["B", "C", "ashleigh", 160],
    ["B", "K", "wangarra", 1060],
    ["C", "D", "ashleigh", 500],
    ["C", "F", "coral", 440],
    ["D", "I", "cranbourne", 440],
    ["E", "J", "karingal", 340],
    ["F", "G", "kareela", 200],
    ["G", "K", "ellis", 320],
    ["G", "H", "kareela", 110],
    ["H", "I", "kareela", 270],
    ["H", "P", "coprosma", 440],
    ["I", "Q", "cranbourne", 450],
    ["J", "AD", "karingal", 230],
    ["K", "M", "wangarra", 130],
    ["AD", "L", "lindrum", 450],
    ["AD", "S", "karingal", 210],
    ["L", "M", "lindrum", 230],
    ["L", "R", "meerlu", 360],
    ["M", "N", "lindrum", 10],
    ["N", "O", "lindrum", 190],
    ["N", "R", "benanee", 160],
    ["O", "P", "lindrum", 180],
    ["O", "U", "banyan", 240],
    ["P", "Q", "lindrum", 260],
    ["Q", "AA", "cranbourne", 890],
    ["R", "T", "benanee", 80],
    ["S", "T", "belar", 690],
    ["S", "V", "karingal", 700],
    ["T", "U", "belar", 190],
    ["T", "W", "ballam park", 790],
    ["V", "W", "naranga", 225],
    ["V", "X", "karingal", 50],
    ["W", "Y", "naranga", 225],
    ["X", "Y", "karingal", 300],
    ["Y", "AE", "karingal", 20],
    ["AE", "Z", "karingal", 160],
    ["Z", "AA", "karingal", 420],
    ["Z", "AC", "k-hub", 220],
    ["AA", "AB", "cranbourne", 220],
    ["AB", "AC", "k-hub", 190],
]
for node in nodes_arr:
    label, x, y = node
    nodes[label] = Node(label, x, y)

G = Graph(nodes)
# G_prime = Graph(nodes)
# print(G is G_prime)
#
# print(G.nodes is G_prime.nodes)

for edge in edges_arr:
    src, dest, name, weight = edge
    G.add_edge(nodes[src], nodes[dest], name, weight)

# G_prime = copy.deepcopy(G)
# print("now running ASTAR using euclidean distance heuristic")
#
# path_info = aSTAR(G, nodes["A"], nodes["AD"], "euclidean")
# if path_info:
#     for k, v in path_info.items():
#         print(f"{k:13}:\t {v}")
#
# if path_info:
#     print(" --> ".join(path_info["path"]))

run_CH(G, G.nodes["B"], G.nodes["X"])
