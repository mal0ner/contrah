# Dijkstra's algorithm
from GraphNode import Node, Graph
from queue import PriorityQueue
import itertools
import math
from search import aSTAR

import copy


class clr:
    H = "\033[95m"
    BL = "\033[94m"
    CY = "\033[96m"
    GR = "\033[92m"
    WR = "\033[93m"
    F = "\033[91m"
    END = "\033[0m"
    BLD = "\033[1m"
    UDL = "\033[4m"


def dijkstra(
    G: Graph,
    start: Node,
    end: Node | None = None,
    exclude=None,
    threshold=None,
    direction: str | None = None,
    contraction_order=None,
) -> list[Node] | None:
    """
    Simple Dijkstra's algorithm: returns path using
    node object's 'previous' attr.

    Source: [Russel, Norvig and Al. 2010, p. 91]
    """
    for node in G.nodes.values():
        node.estD = math.inf

    start.estD = 0
    frontier = PriorityQueue()
    reached = [start]

    # counter is an iterator that we can use as a hacky solution for prio-queue
    # comparison when node.estD already exists in the priority queue (since tuple-tuple
    # comparison falls to next element when the first two (estD) are equal, and Node
    # instances are not comparable.
    counter = itertools.count()

    # use the counter to ensure comparison will work if a node with estD already
    # exists in the queue
    frontier.put((start.estD, next(counter), start))

    while not frontier.empty():
        dist, _, node = frontier.get()
        if end and node == end:
            return node

        for edge in node.get_out_edges():
            nbor = edge["endpoint"]

            if exclude and nbor in exclude:
                continue

            if nbor in reached:
                continue

            if contraction_order and direction and direction == "UP":
                if contraction_order.index(start.label) > contraction_order.index(
                    nbor.label
                ):
                    continue

            if contraction_order and direction and direction == "DOWN":
                if contraction_order.index(node) > contraction_order.index(nbor):
                    continue

            if dist + edge["weight"] < nbor.estD:
                updated_dist = dist + edge["weight"]
                nbor.estD = updated_dist
                nbor.parent = node
                nbor.preceding_edge = edge
                reached.append(nbor)
                frontier.put((nbor.estD, next(counter), nbor))

                if threshold and updated_dist > threshold:
                    return None

    # solution either not reached, or target unspecified
    return reached


def contract(G: Graph, node: Node) -> list:
    """
    critical component of CH and the step where we
    determine the 'shortcuts' to be added to the overlay
    graph G' of G.

    take the following sets for contraction on node v in V of G=(V,E):
        - U (set of nodes with incoming edges to v)
        - W (set of nodes with incoming edges from v)

    Finding 'shortcuts' is as simple as conducting a localised
    single-source shortest path (Dijkstra's) on all u in U (subgraph of G)
    excluding v. if no path u ->...-> w is found with
    dist(u,w) < dist(u, v) + dist(v, w) then we can create an
    artificial shortcut edge u -> w with weight dist(u, v) + dist(v, w).
    """

    U = G.get_incoming_neighbours_with_edges(node)
    # print(f"node {node.label} incoming neighbours = {U.keys()}")
    W = G.get_outgoing_neighbours_with_edges(node)
    # print(f"node {node.label} outgoing neighbours = {W.keys()}")
    # print(f"Graph before contraction: {G}")

    shortcuts = []

    for k, u_v in U.items():
        u = G.nodes[k]
        cost_incl_v = {}

        for k2, v_w in W.items():
            w = G.nodes[k2]
            cost_incl_v[(u.label, w.label)] = u_v["weight"] + v_w["weight"]
        if not cost_incl_v:
            continue
        threshold = max(cost_incl_v.values())

        # print("U is: ", u)
        dijkstra(G, u, exclude=[node], threshold=threshold)
        for k3, v_w in W.items():
            w = G.nodes[k3]
            short_cost = cost_incl_v[(u.label, w.label)]

            if w.estD > short_cost:
                lmarks = u_v["landmarks"] + v_w["landmarks"]
                obst = u_v["obstacles"] + v_w["obstacles"]
                nbors = u.neighbours
                # these lines delete duplicate shortcuts, as we may find a better one
                for nbor in nbors:
                    if nbor["endpoint"] == w and nbor["weight"] >= short_cost:
                        # print("removing duplicate")
                        u.remove_incident_edge(nbor)
                for nbor in w.neighbours:
                    if nbor["endpoint"] == u and nbor["weight"] >= short_cost:
                        w.remove_incident_edge(nbor)
                u.add_neighbour("shortcut", w, short_cost, lmarks, obst)
                # w.add_neighbour("", u, short_cost, lmarks, obst)
                shortcuts.append(
                    (u.label, w.label, "shortcut", short_cost, lmarks, obst)
                )

    print(
        f"\t\tcontracted Node {node.label}:"
        + f" added {clr.CY}{len(shortcuts)}{clr.END} shortcuts"
    )
    G.remove_node(node)

    return shortcuts


def simulate_contraction(G: Graph, node: Node) -> int:
    edges = node.get_out_edges()

    # list of nodes directly adjacent to v (node we wish to contract)
    U = {e["endpoint"].label: (e["endpoint"], e["weight"]) for e in edges}

    # we assume the graph is fully bi-directional here
    original_edges = 2 * len(edges)
    shortcut_edges = 0

    # shortcuts = []  # for printing to stdout only
    for u, cost_u_to_v in U.values():
        cost_incl_v = {}

        for w, cost_v_to_w in U.values():
            cost_incl_v[(u.label, w.label)] = cost_u_to_v + cost_v_to_w
        # the threshold is the maximum cost of any path u->v->w for all w in W,
        # where W is the set of nodes adjacent to v with incoming edges from v
        threshold = max(cost_incl_v.values())

        # run localised dijkstra on subgraph distance bounded by the threshold
        dijkstra(G, u, exclude=[node], threshold=threshold)

        for w, _ in U.values():
            inclusive_cost = cost_incl_v[(u.label, w.label)]  # cost of path u->w via v
            if w.estD > inclusive_cost:  # if cost u->w via v is min, make shortcut
                # shortcuts.append(f"({u.label}->{w.label}, {inclusive_cost})")
                shortcut_edges += 1

    labels = "[" + ", ".join([u[0].label for u in U.values()]) + "]"
    print(
        f"\t\t{clr.BLD}{clr.H}SIM_CONTRACT* node: {clr.GR}{node.label:2}{clr.END}"
        + f" on subg {labels:8}->"
        + f" simulating {clr.WR}{shortcut_edges//2:2}{clr.END} shortcuts"
    )

    # compute the edge diff
    return shortcut_edges - original_edges


def get_contraction_order(G: Graph):
    """
    Simulate contraction for each node in the graph.
    Lowest edge-difference maintains top position in
    prio-queue which is used as an initial node-ordering
    for later contraction. During the actual pre-processing
    stage and node-contraction these edge differences will
    be lazily re-evaluated.
    """
    contraction_queue = PriorityQueue()
    # counter for similar trick used in simulate_contraction
    counter = itertools.count()
    for node in G.nodes.values():
        edge_diff = simulate_contraction(G, node)
        contraction_queue.put((edge_diff, next(counter), node))
    return contraction_queue


def contract_graph(G: Graph, hierarchy: PriorityQueue):
    """
    MAKE SURE TO PASS IN A DEEPCOPY OF ORIGINAL G TO THIS METHOD
    Contract nodes in graph according to order provided
    by contraction simulation. Because the edge difference
    of nodes can change during the process, we will
    lazily re-evaluate each node's edge difference as
    they are popped from the queue. If they still have
    the smallest edge difference, then we proceed.

    [Geisberger et al., 2012]
    [Lazarsfeld 2018]
    link^: https://jlazarsfeld.github.io/ch.150.project/sections/12-node-order/
    """

    final_contraction_order = []
    shortcuts = []

    while not hierarchy.empty():
        lowest_diff = False
        # we only want the node with the minimum edge difference
        # if that property still holds, so we check iteratively.
        # this is the lazy evaluation.
        num_iters = 1
        print("\n\t\tEXEC LAZY RE-EVALUALTION OF CONTRACTION ORDER:")
        while not lowest_diff:
            old_diff, counter, node = hierarchy.get()
            print(f"\t\treceived Node<{node.label}>")
            new_diff = simulate_contraction(G, node)

            # check if the new diff is still the lowest compared to
            # what's currently in 1st queue position
            if not hierarchy.empty() and new_diff > hierarchy.queue[0][0]:
                hierarchy.put((new_diff, counter, node))
            else:
                hierarchy.put((old_diff, counter, node))
                lowest_diff = True
            num_iters += 1
        print(f"\t\tRE-EVALUATED NODE EDGE DIFFERENCE <{num_iters}> TIMES")

        _, _, node = hierarchy.get()
        final_contraction_order.append(node.label)
        node_shortcuts = contract(G, node)
        shortcuts.append(node_shortcuts)

    # return a list of tuples containing the shortcuts we added to
    # G' so we can easily add them to G.
    return shortcuts, final_contraction_order


def build_g_prime(G: Graph):
    G_prime = copy.deepcopy(G)
    G_test = copy.deepcopy(G)

    print(f"\n\t{clr.WR}EXEC CONTRACTION SIMULATION:{clr.END}")
    initial_contraction_order = get_contraction_order(G)
    print(
        f"\t{clr.WR}SIMULATED CONTRACTION OF "
        + f"{len(initial_contraction_order.queue)}"
        + f" NODES{clr.END}"
    )

    print(f"\n\t{clr.WR}CONTRACTING GRAPH: {G.__class__}{clr.END}")
    shortcuts, final_contraction_order = contract_graph(G, initial_contraction_order)
    print(
        f"\t{clr.WR}CONTRACTION COMPLETE FOUND "
        + f"<{sum(len(x) for x in shortcuts)}> SHORTCUTS{clr.END}"
    )
    print(
        "\tWITH CONTRACTION ORDER: "
        + f"{clr.CY}[{' '.join([n for n in final_contraction_order])}]{clr.END}"
    )

    # we contract G then add shortcuts from overlay to G'
    print(
        f"\n\t{clr.WR}GENERATING QUERY GRAPH"
        + f"{clr.CY}[G*]{clr.WR} FROM CONTRACTED OVERLAY GRAPH {clr.CY}[G]{clr.END}"
    )

    print("\n\t<Performing shortcut unit tests against known working a*>")
    success = test_shortcuts(G_test, shortcuts)
    print("\n\t<Adding shortcuts from overlay graph [G] to [G*]>")
    if success:
        num_shortcuts = add_shortcuts_to_overlay(G_prime, shortcuts)
        print(f"\n\t\tSuccess: added {num_shortcuts} shortcuts")
    else:
        print("FAILED UNIT TEST/S: ABORTING")

    return G_prime, final_contraction_order


def add_shortcuts_to_overlay(G: Graph, shortcuts: list):
    num_shortcuts = 0
    for sub_list in shortcuts:
        for shortcut in sub_list:
            src, dest, name, weight, lmarks, obst = shortcut
            G.add_dir_edge(G.nodes[src], G.nodes[dest], name, weight, lmarks, obst)
            num_shortcuts += 1
    return num_shortcuts


def test_shortcuts(G: Graph, shortcuts) -> bool:
    score = 0
    num_shortcuts = 0
    for sub_list in shortcuts:
        for shortcut in sub_list:
            src, dest, _, weight, _, _ = shortcut
            G.reset_nodes()
            best_path = aSTAR(G, G.nodes[src], G.nodes[dest], "euclidean")
            if best_path is not None:
                optimal = weight == best_path["total_weight"]
                print(
                    f"\t\tTesting shortcut [{src} {dest} {weight}] against eucl aSTAR*"
                    + f"--> got {best_path['total_weight']} {clr.WR}{optimal}{clr.END}"
                )
                score += 1
            else:
                print(f"Path ({src}->{dest}) did not terminate with aSTAR")
            num_shortcuts += 1
    p = score / num_shortcuts * 100
    print(
        f"\n\t{clr.WR}PASSED {clr.CY}{score}/{num_shortcuts}{clr.END} TESTS: {p:.02f}%"
    )
    if p == 100:
        return True
    return False


def query_graph(G: Graph, s: Node, t: Node, contraction_order: list):
    upwards = copy.deepcopy(G)
    downwards = copy.deepcopy(G)

    print(f"\n\t{clr.WR}EXEC MODIFIED GRAPH QUERY USING BIDIR DIJKSTRAS:{clr.END}")
    print("\t\treceived contraction order...\n")

    print(
        "\t\t1. running complete dijkstra's search on upwards "
        + f"subgraph G*_U from source node {clr.CY}{s.label}{clr.END}"
    )
    reached_s = dijkstra(
        upwards,
        upwards.nodes[s.label],
        contraction_order=contraction_order,
        direction="UP",
    )
    print(
        "\t\t2. running complete reversed dijkstra's search on upwards "
        + f"subgraph G*_U from target node {clr.CY}{t.label}{clr.END}\n"
    )
    reached_t = dijkstra(
        downwards,
        downwards.nodes[t.label],
        contraction_order=contraction_order,
        direction="UP",
    )

    if not reached_s or not reached_t:
        raise Exception("Error in Dijkstra's search, please check")

    reached_labels_up = [n.label for n in reached_s]
    reached_labels_down = [n.label for n in reached_t]
    print(
        "\t\tSUCCESS: forward search reached nodes: "
        + f"{clr.CY}[{' '.join([n for n in reached_labels_up])}]{clr.END}"
    )
    print(
        "\t\tSUCCESS backwards search reached nodes: "
        + f"{clr.CY}[{' '.join([n for n in reached_labels_down])}]{clr.END}"
    )
    intersection = [n for n in reached_labels_up if n in reached_labels_down]

    print(
        "\n\t\tfound intersection: "
        + f"{clr.GR}[{' '.join([n for n in intersection])}{clr.END}]"
    )
    node_scores = []
    for node in intersection:
        node_scores.append(upwards.nodes[node].estD + downwards.nodes[node].estD)
    print(
        "\t\twith score(s) (cumulative est distances from "
        + f"respective search starts): {clr.F}{[s for s in node_scores]}{clr.END}"
    )
    mutual_best = intersection[node_scores.index(min(node_scores))]
    print("\t\tmutual best is: ", mutual_best)

    print(f"\n\t{clr.WR}BUILDING SEARCH PATHS USING BACKTRACE...{clr.END}")

    print("\t\tBacktracing path from mutual best to start node: ", s.label)
    path_from_s = backtrack_dijkstra_path(upwards.nodes[mutual_best], reverse=True)
    print(
        f"\t\tFOUND PATH: {clr.GR}[{' '.join(path_from_s['nodes'])}]{clr.END} "
        + f"with weight: {path_from_s['total_weight']}"
    )

    print("\t\tBacktracing path from mutual best to target node: ", t.label)
    path_to_g = backtrack_dijkstra_path(downwards.nodes[mutual_best], reverse=False)
    print(
        f"\t\tFOUND PATH: {clr.GR}[{' '.join(path_to_g['nodes'])}]{clr.END} "
        + f"with weight: {path_to_g['total_weight']}"
    )

    print(f"\n\t{clr.WR}CONCATENATING PATHS...{clr.END}")
    path = get_joined_dijkstras_paths(path_from_s, G.nodes[mutual_best], path_to_g)
    for k, v in path.items():
        print(f"\t\t{k:12}: {v}")

    # return path


def backtrack_dijkstra_path(curr: Node, reverse=False):
    node_path = [curr.label]
    edge_path = []
    weights = []
    obstacles = []
    landmarks = []
    while curr.parent:
        edge = curr.preceding_edge
        curr = curr.parent
        if edge:
            node_path.append(curr.label)
            edge_path.append(edge["name"])
            weights.append(edge["weight"])
            obstacles.extend(edge["obstacles"])
            landmarks.extend(edge["landmarks"])

    if reverse is True:
        return {
            "nodes": node_path[::-1],
            "edges": edge_path[::-1],
            "weights": weights[::-1],
            "obstacles": obstacles[::-1],
            "landmarks": landmarks[::-1],
            "total_weight": sum(weights),
        }
    return {
        "nodes": node_path,
        "edges": edge_path,
        "weights": weights,
        "obstacles": obstacles,
        "landmarks": landmarks,
        "total_weight": sum(weights),
    }


def get_joined_dijkstras_paths(src_path, mid: Node, target_path):
    return {
        "nodes": src_path["nodes"][:-1] + [mid.label] + target_path["nodes"][1:],
        "edges": src_path["edges"] + target_path["edges"],
        "weights": src_path["weights"] + target_path["weights"],
        "obstacles": src_path["obstacles"] + target_path["obstacles"],
        "landmarks": src_path["landmarks"] + target_path["landmarks"],
        "total_weight": src_path["total_weight"] + target_path["total_weight"],
    }


def run_CH(G: Graph, src: Node, target: Node):
    G_prime, order = build_g_prime(G)
    print("\n")
    try:
        path = query_graph(
            G_prime, G_prime.nodes[src.label], G_prime.nodes[target.label], order
        )
        print(path)
    except Exception as e:
        print(e)
