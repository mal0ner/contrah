# Contraction Hierarchies

![fig8](https://github.com/user-attachments/assets/0fdb35b5-974a-4536-915e-3bb213b0732f)

The objective of this project was to investigate informed or heuristic search strategies on a search space modelled after a real-life road network with the specific caveat that the agent be represented as someone inhibited by a wheelchair in their ability to traverse said network. The project is aimed at exploring various forms of heuristics and how their properties can affect the implementation of the common A\* heuristic search algorithm.

I also researched alternative methods for network-style pathfinding solutions; in particular, those which find common deployment in real-world scenarios for their marked improvement in runtime query costs for end users. To this end, I decided to implement and gauge the performance of the Contraction Hierarchies algorithm.

# Usage

This contraction hierarchies implementation depends on the following:

- `python 3.10.11`
- `haversine 2.8.0`

If you have conda installed on your system you can simply run the following:

```sh
conda create -y -n ch_py python=3.10.11 pip

conda activate ch_py

pip install haversine==2.8.0


# run contraction hierarchies
python main.py
```

## 1.1 Informed / Heuristic Search

In the context of search algorithms, informed refers to the ability for the problem solving agent to derive some notion of its distance from the goal. This distance measure is at the core of every informed search algorithm and is given by a heuristic function h(𝑛)

Heuristic functions come in a large variety of forms, the most recognisable of which may be the Manhattan (city-block) and Euclidean distances, known as the L1 and L2 norms respectively which describe the distance between points . [1]

## 1.2 A\* (Greedy Best-First Search)

For A\*, the evaluation function $f(n)$, by which we assign priority to the expansion of some node 𝑛 is given by $f(n) = g(n) + h(n)$. Where $𝑔(𝑛)$ is the cumulative cost of actions taken to reach the current state from the initial state, and $h(𝑛)$ is the distance to the goal state, provided by some heuristic function. [1]

## 1.3 Contraction-Hierarchies

Contraction Hierarchies is a method for quantifying some measure of a node’s importance to traversal and then ordering the nodes in a network based on that metric. In theory, if an optimal ordering of nodes can be found, then, despite the somewhat overwhelming cost of pre-processing, subsequent queries to the graph can leverage the order to drastically reduce the average search-space required to find optimal-cost routes between points.
In his excellent project paper on the subject, John Lazarsfeld [2] equates the procedure as being akin to zooming out on Google maps. As you decrease the fidelity of the picture, smaller, less relevant streets begin to fade out of view in favour of large junctions, highways, and interstate roads. These larger streets often form a large portion of the driving during an average trip and including them is usually more favourable than travelling the same distance over many much smaller roads (less capacity, lower speed
limit etc.).
In practice, categorising the importance of nodes in a network and creating Google’s ‘Big yellow roads’ comes down artificially reducing the search space of a network by adding additional edges between nodes in a process known as contraction.

## 1.4 Node Contraction

Given a graph $𝐺 = (𝑉,𝐸)$ and a vertex $v \in V$, we can **contract v** by:

1. Denoting the sets $𝑈$, the set of vertices adjacent to 𝑣 which have outgoing edges to $𝑣$,
   and $𝑊$, the set of vertices which $𝑣$ has outgoing edges to.
2. For all $𝑢$ in $𝑈$ do:
   a. Find the maximum cost of a path $𝑢 \rightarrow 𝑣 \rightarrow 𝑤$ for all $w \in W$.
   b. Run a Dijkstra’s search on the localised subgraph starting a $𝑢$, which finds the cost of paths to all $𝑤$ in $𝑊$ excluding $𝑣$, which terminates upon reaching a node
   with a path score higher than the maximum found earlier.
3. If a path $𝑢 \rightarrow 𝑤$ excluding $𝑣$ exists such that the cost $d(u, w)$ is less than the cost of travelling → 𝑣 → 𝑤, then we can add a shortcut edge 𝑢 → 𝑤 with weight 𝑑(𝑢, 𝑤).
   (i.e. there is a better option than including 𝑣.)
4. Remove 𝑣 and all its incident edges from the graph.

## 1.5 Querying

This process is repeated until all nodes in the graph have been contracted and removed. The leftover product is then a set of shortcuts known as an overlay graph, which can be used in the search process (modified bi-directional Dijkstra’s) for more efficient querying.

The **order** in which the nodes were contracted dictates their relative importance and is calculated by simulating contraction without directly modifying the graph, then noting the number of shortcuts that would have been added (edge difference). Generally, we aim to prioritise and thus contract early in the process nodes which have a lower edge difference.

Complete node contraction on the graph concludes the pre-processing segment of CH. Querying the resulting graph (union of the original graph 𝐺 and overlay graph 𝐺′ containing the shortcuts) is then a matter of running two complete Dijkstra’s on following modified sub-graphs of 𝐺′: [2]

- $G'_D$: Downward graph from vertex $v$ containing only nodes and edges towards nodes where $v$ contracted earlier.
- $G'_U$: Upward graph from vertex $v$ containing only nodes and edges towards nodes which were contracted before $v$.

**Note:** unique ordering of nodes means that $G'_D \cup G'_U$ contains the whole search space of $G'$ [2].
**Note:** For a fully bi-directional / symmetric $G'$ starting at vertex $v$, $G'_D = G'_U$.

Once the complete searches are finished, the solution is found by taking the minimum sum of path costs across every node in the intersection of nodes reached in both searches. This node can then be used to back-trace paths in the respective search sub-graphs using parent-edge and parent-node pointers in the node objects

# 2. Approach and Challenges

My initial approach to modelling my local suburb as a network graph used OSM (Open Street Maps) data downloaded and translated to a graph through the python NetworkX interface layer OSMNX. Wheelchair accessibility data is well-supported by the OSM architecture. With custom filters applied when fetching the map, way data (ways being the OSM equivalent to edges) can be configured to include any of a wide list of ‘tags’

![fig1](https://github.com/user-attachments/assets/20acc7b1-869b-4351-9b78-b6475af6606f)

<div align="center">
  <b>Figure. 1</b> OSMNX data import and graph creation with custom way filters applied according to OSM wheelchair accessibility guidelines.
  <a href="https://wiki.openstreetmap.org/wiki/Wheelchair_routing">link</a>
</div>

<br />

![fig2](https://github.com/user-attachments/assets/cec30150-057d-444b-a918-d59ad6f2dfa5)

<div align="center">
  <b>Figure. 2</b> OSMNX Network graph output for query "Frankston, Victoria" shown in fig 1.
</div>

While visually attractive and initially very promising, the implementation encountered some impassable bottlenecks when it came time to perform edge queries and reconstruct wheelchair accessible paths. This becomes immediately clear when we take a closer look at the data.

![fig3](https://github.com/user-attachments/assets/70814d4c-09e0-4a1b-9fed-4cdf07b46447)

<div align="center">
  <b>Figure. 3</b> Summary statistics on edge Data Frame output by OSMNX.
</div>

<br />

At 12,890 ways, the resulting graph is extremely dense, and yet simultaneously devoid of any meaningful data. Without considering road surface, which is likely the least impactful metric requested in the filters, the mean percentage of populated records was 1.67%.
I was unable to resolve this issue; the sparsity of the data made it difficult to produce meaningful pathways, while the density of the overall graph made manual edge property insertion infeasible.

## 2.1 Implementation: Custom Graph Class

I decided to implement the graph, node, and edge data structures from scratch, ensuring consistency in style and behaviour.

![fig4](https://github.com/user-attachments/assets/ab7550ff-5da4-4bb9-a50f-7cd52c342467)

<div align="center">
  <b>Figure. 4</b> Custom python graph, node and edge classes attribute and method overview.</div>

The inspiration for the design of the classes was given by inspection of the source code behind the natively supported OSMNX graph and node implementations. The lightweight nature of these custom classes made modification and extension during algorithm tuning a simple task.
Between the attributes and methods shown above, all operations and features necessary to complete both A\* and Contraction Hierarchies are available.

## 2.2 A\* Heuristic Search

After encountering some difficulty in constructing a working and bug-free graph data-structure, particularly in handling the deletion of nodes and edges in the graph class, the A\* algorithm itself was surprisingly easy to implement.

Using [1]’s excellent breakdown of Greedy-Best-First search \[ch. 3.5.1, pp. 103-107\] as a foundation, A\* can be defined as a derived GBFS with an evaluation function:
$$f(n) = g(n) + h(n)$$

## 2.3 Putting it together:

Python’s built-in min-heap Priority Queue allows for simple prioritisation of appending to the frontier those nodes which minimise $f(n)$. With that, the complete algorithm can be (only slightly) simplified and expressed as:

![fig5](https://github.com/user-attachments/assets/e9c41f06-75b7-46c1-9b20-766c8d12e3f9)

<div align="center">
  <b>Figure. 5</b> Simplified A* search.
</div>

## 2.4 Heuristics: How is A\* affected by choice of heuristic?

Russell and Norvig [1] explain in their chapter on informed search algorithms that A\* is complete1, but only conditionally optimal. Complete-ness of the algorithm is evident seeing the above code – given initialisation of $g_{initial}(n) = \infty, \forall n \in V$, all nodes in a graph connected from the source node will pass the $g_{temp} < g(n)$ test at least once and be appended to the frontier. Cost-optimality is determined by the heuristic, particularly its **admissibility**,

> "an admissable heuristic is one that never over-estimates the cost to reach the goal" [1] (given existing solution or finite search space, and $\epsilon > 0$ where $\epsilon$ is lower bound for action cost [1])

I evaluated the performance of A\* using three different heuristics:

- Manhattan Distance (𝐿1 norm): $\sum^n_1 | p_i-q_i|$
- Euclidean Distance (L2 norm): $\sqrt{\sum^n_{i=1}(q_i-p_i)^2}$
- Haversine Distance (Great circle distance): $hav(\theta) = sin^2(\frac{\theta}{2}$

> Great circle distance gives the shortest distance between two points on a sphere, with <0.5% error on latitude and <0.2% error on longitude [4]

## 2.5 Graph representation of local suburb:

![fig6](https://github.com/user-attachments/assets/ece9b31c-3298-40b2-a51a-c6e15402f6da)

<div align="center">
  <b>Figure. 6</b> Abstract Representation of the graph data structure used for A* search algorithm. Latitude and Longitude coordinates in node objects reflect real positions of the
intersections, and edge weights are calculated using real distances (measured on Google Maps) scaled by a weighting factor whose value is determined by the level of observed wheelchair accessibility (according to OSM guidelines (see Fig. 1)
</div>

## 2.6 Evaluating Heuristic Error:

Heuristic error was evaluated from nodes “A to AE” on the above graph with a real observed distance of 1.84𝑘𝑚.

![fig7](https://github.com/user-attachments/assets/b0e3fe94-e9ec-4486-a9cd-6a947ef69bc7)

<div align="center">
  <b>Figure. 7</b> Error between heuristic distance predictions and measured values
</div>

Manhattan distance provides good approximations for the distance between points on grid-like networks that resemble many real-world traffic networks, and Haversine distance gives accurate measures of distance which account for the curvature of the earth.

## 2.7 Performance analysis

Tests involved first proving the correctness of the path building functionality of the A* implementation, followed by averaging the performance of the three metrics over 100 iterations of A*. The clear performance winner in this case was the haversine metric. Explanations for this could include:

- Lower observed error between measured and predicted goal distance could provide for a more optimised node expansion order. (Fig. 6)
- The function is imported as a third-party dependency and could be implemented using native C/C++ code which can leverage low-level optimisation, type safety and/or memory manipulation for drastically improved observed performance.

## 2.8 Back to Contraction Hierarchies

As explained in sections 1.3-1.5, the CH (Contraction Hierarchies) algorithm, applied on some graph $𝐺 = (𝑉, 𝐸)$ can be separated into two distinct sub-processes:

1. **Graph contraction:** contract each node $v \in V$ by order of **importance**, given by the
   simulated contraction of $G$, such that an overlay graph $G'$ is produced which persists said order through artificial subgraphs $G'_D$ and $G'_U$.
2. **Graph query**: Execute consecutive complete Dijkstra’s searches: one from source
   node 𝑠 on $G'_U$ in the **upwards** direction with respect to the contraction order; and two, from target node $t$ on $G'_D$ in the **downwards** direction with respect to the contraction order. The path is reconstructed via back-tracing from the optimal (lowest summed cost) node found in the intersection of the set of nodes reached by both searches.

## Result:

![fig8](https://github.com/user-attachments/assets/76c79b3a-9268-4188-845f-8fb58d76244b)

<div align="center">
  <b>Figure. 8</b> Shows the resulting graph after applying 45 directional shortcuts during node contraction.
</div>

## Final Performance comparison:

**A\*:** The time complexity of A* is bounded by 𝑂(𝑏^d) (b is branching factor and d is the depth) in the case of an unbounded search-space (previously mentioned to cause A* to be incomplete). In practical applications however, given an appropriately admissible heuristic and a suitable search space, A* is able to utilise the sense of direction to trim away many of the exponentially escaping branches that would have otherwise been expanded. The effective branching factor is a way to classify how effective the heuristic is and results in classifying an A* search with an admissible heuristic as in the order O(b\*)^𝑑. [1].
**Contraction Hierarchies:**
Due to the overwhelming number of variations in approaches to pre-processing and querying overlay graphs, the performance of contraction hierarchies can be difficult to categorise. For my implementation, the runtime is equally difficult to capture due to the number of steps involved in the process.
