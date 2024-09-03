from GraphNode import Graph, Node
from contractionHierarchy import clr, run_CH
from search import aSTAR
import random


def create_map_graph():
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
        ["A", "B", "ashleigh", 120, [], []],
        ["A", "E", "ashleigh", 740, ["corner store", "aged care"], []],
        ["A", "J", "brentwood", 920, ["playground"], []],
        ["B", "C", "ashleigh", 160, ["tile shop"], []],
        ["B", "K", "wangarra", 1060, ["furniture store", "ceramics shop"], []],
        ["C", "D", "ashleigh", 500, ["ritchies IGA", "doctors clinic"], []],
        ["C", "F", "coral", 440, ["Catholic church", "Coffee shop"], []],
        [
            "D",
            "I",
            "cranbourne",
            440,
            ["Pizza parlour", "Kebab shop", "Patisserie"],
            [],
        ],
        ["E", "J", "karingal", 340, ["orthodontist", "cake shop"], []],
        ["F", "G", "kareela", 200, [], []],
        ["G", "K", "ellis", 320, ["Hair salon"], []],
        ["G", "H", "kareela", 110, ["Paint shop"], []],
        ["H", "I", "kareela", 270, [], []],
        ["H", "P", "coprosma", 440, [], []],
        [
            "I",
            "Q",
            "cranbourne",
            450,
            ["Frankston RSL", "KFC", "Italian restaurant"],
            [],
        ],
        ["J", "AD", "karingal", 230, ["Construction firm", "Yoga studio"], []],
        ["K", "M", "wangarra", 130, ["Graphic design firm"], []],
        ["AD", "L", "lindrum", 450, ["Milk bar"], []],
        ["AD", "S", "karingal", 210, ["Anglican church", "Makeup shop"], []],
        ["L", "M", "lindrum", 230, ["Public garden"], []],
        ["L", "R", "meerlu", 360, ["Custom T-shirt printer"], []],
        ["M", "N", "lindrum", 10, [], []],
        ["N", "O", "lindrum", 190, [], []],
        ["N", "R", "benanee", 160, [], []],
        ["O", "P", "lindrum", 180, [], []],
        ["O", "U", "banyan", 240, ["Kites 4 Kids"], []],
        [
            "P",
            "Q",
            "lindrum",
            260,
            ["Medical supply store", "Car wash", "Fitness club", "Bowling Alley"],
            [],
        ],
        [
            "Q",
            "AA",
            "cranbourne",
            890,
            [
                "Cheesecake factory",
                "St John's Hospital",
                "Pharmacy",
                "Skatepark",
                "Dog Park",
                "Veterinary Hospital",
                "Preschool",
            ],
            ["no footpath"],
        ],
        ["R", "T", "benanee", 80, [], []],
        [
            "S",
            "T",
            "belar",
            690,
            ["Primary School", "Specialty college", "Dog park"],
            [],
        ],
        ["S", "V", "karingal", 700, ["IT repair", "Primary School"], []],
        ["T", "U", "belar", 190, [], []],
        ["T", "W", "ballam park", 790, ["Ballam Park", "Football oval"], []],
        ["V", "W", "naranga", 225, ["Preschool"], []],
        ["V", "X", "karingal", 50, [], []],
        ["W", "Y", "naranga", 225, [], []],
        ["X", "Y", "karingal", 300, ["Plumbers"], []],
        ["Y", "AE", "karingal", 20, [], []],
        [
            "AE",
            "Z",
            "karingal",
            160,
            ["Arcade", "Movie Theater", "Playground", "Cafe"],
            [],
        ],
        [
            "Z",
            "AA",
            "karingal",
            420,
            ["Dentists", "Petrol station", "Burger joint", "Red rooster"],
            [],
        ],
        ["Z", "AC", "k-hub", 220, ["Karingal Hub North"], ["stairs"]],
        ["AA", "AB", "cranbourne", 220, [], ["no footpath"]],
        ["AB", "AC", "k-hub", 190, ["Karingal Hub South"], []],
    ]
    for node in nodes_arr:
        label, x, y = node
        nodes[label] = Node(label, x, y)

    G = Graph(nodes)

    for edge in edges_arr:
        src, dest, name, weight, obst, lmarks = edge
        G.add_edge(nodes[src], nodes[dest], name, weight, obst, lmarks)

    return G


if __name__ == "__main__":
    G_astar = create_map_graph()
    G_ch = create_map_graph()

    measured_dist = 1.84
    manhattan = G_astar.nodes["A"].calc_h(G_astar.nodes["AE"], "manhattan")
    euclidean = G_astar.nodes["A"].calc_h(G_astar.nodes["AE"], "euclidean")
    h_dist = G_astar.nodes["A"].calc_h(G_astar.nodes["AE"], "haversine")
    print(f"\t{clr.WR}COMPARE HEURISTICS:{clr.END}\n")
    print(f"Manhattan distance node A -> AE: {manhattan:.2f}km")
    print(f"Euclidean distance node A -> AE: {euclidean:.2f}km")
    print(f"Haversine distance node A -> AE: {h_dist:.2f}km")
    print(f"\n\t{clr.WR}ERROR TO MEASURED DIST {measured_dist}:{clr.END}\n")
    print(f"\tmanhattan: {(abs(manhattan - measured_dist)):.2f}")
    print(f"\teuclidean: {(abs(euclidean - measured_dist)):.2f}")
    print(f"\thaversine: {(abs(h_dist - measured_dist)):.2f}")

    print("\nnow running ASTAR using haversine distance heuristic")
    path_info = aSTAR(G_astar, G_astar.nodes["A"], G_astar.nodes["AE"], "haversine")
    if path_info:
        for k, v in path_info.items():
            print(f"{k:13}:\t {v}")

    if path_info:
        print(" --> ".join(path_info["path"]))
    G_astar.reset_nodes()
    # G_prime = copy.deepcopy(G)
    nodes = [n for n in G_astar.nodes.keys()]

    print("\n")

    def run_astar_n_times(G, nodes, n, h):
        """run a* a number of times and return the average runtime in ms"""
        print(f"running: {h} {n} times")
        times = []
        for _ in range(n):
            idx1 = random.randint(0, len(nodes) - 1)
            idx2 = random.randint(0, len(nodes) - 1)
            p = aSTAR(G, G.nodes[nodes[idx1]], G.nodes[nodes[idx2]], h)
            if p:
                times.append(p["time"])
            G.reset_nodes()
        print(sum(times) / len(times))

    run_astar_n_times(G_astar, nodes, 100, "euclidean")
    run_astar_n_times(G_astar, nodes, 100, "manhattan")
    run_astar_n_times(G_astar, nodes, 100, "haversine")

    print("\n\nRUNNING CONTRACTION HIERARCHIES")
    run_CH(G_ch, G_ch.nodes["A"], G_ch.nodes["AE"])
