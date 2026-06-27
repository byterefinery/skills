# Graph Classes

## Core Classes

| Class | Description |
|---|---|
| `nx.Graph` | Undirected, no parallel edges. Self-loops allowed. |
| `nx.DiGraph` | Directed, no parallel edges. Self-loops allowed. Inherits from `Graph`. |
| `nx.MultiGraph` | Undirected, allows parallel (multi) edges. Each edge has a key. |
| `nx.MultiDiGraph` | Directed, allows parallel edges. Combines `MultiGraph` and `DiGraph`. |

## Construction

```python
G = nx.Graph()
G = nx.Graph(incoming_graph_data)  # from dict-of-dicts, edgelist, etc.
G = nx.Graph(name="my graph")      # keyword attrs stored in G.graph
```

All classes accept `incoming_graph_data` in multiple formats: another NetworkX graph, dict-of-dicts, dict-of-lists, edge list (iterable of 2-tuples or 3-tuples), NumPy array, SciPy sparse matrix.

## Node Operations

```python
G.add_node(1)
G.add_node(1, color="red", weight=5)
G.add_nodes_from([1, 2, 3])
G.add_nodes_from([(n, {"color": "blue"}) for n in range(5)])
G.remove_node(1)
G.remove_nodes_from([1, 2, 3])
G.has_node(1)
list(G.nodes())                   # node labels
list(G.nodes(data=True))          # [(node, attr_dict), ...]
list(G.nodes(data="color"))       # [(node, color_value), ...]
```

### Node Attributes

```python
G.nodes[1]["color"] = "red"       # set attribute
G.nodes[1]["weight"]              # get attribute
nx.set_node_attributes(G, values={"color": "blue"}, name="color")
# or from a dict of dicts
nx.set_node_attributes(G, {0: {"x": 1}, 1: {"x": 2}})
attrs = nx.get_node_attributes(G, "color")
```

## Edge Operations

```python
G.add_edge(1, 2)
G.add_edge(1, 2, weight=3.0)
G.add_edges_from([(1, 2), (2, 3)])
G.add_edges_from([(1, 2, {"w": 1}), (2, 3, {"w": 2})])
G.remove_edge(1, 2)
G.remove_edges_from([(1, 2), (2, 3)])
G.has_edge(1, 2)
list(G.edges())                   # [(u, v), ...]
list(G.edges(data=True))          # [(u, v, attr_dict), ...]
list(G.edges(data="weight"))      # [(u, v, weight_value), ...]
G[1][2]                           # edge attribute dict
G[1][2]["weight"] = 5.0           # modify edge attribute
```

### MultiGraph Edge Keys

```python
MG = nx.MultiGraph()
key1 = MG.add_edge(1, 2, weight=1)  # returns key (int, starts at 0)
key2 = MG.add_edge(1, 2, weight=2)  # parallel edge, key=1
MG.edges(keys=True, data=True)      # [(1, 2, 0, {...}), (1, 2, 1, {...})]
MG.remove_edge(1, 2, key=key1)      # remove specific edge
```

### DiGraph Direction-Specific APIs

```python
DG = nx.DiGraph()
DG.add_edge(1, 2)
list(DG.successors(1))              # nodes with edges FROM 1
list(DG.predecessors(1))            # nodes with edges TO 1
list(DG.out_edges(1))               # outgoing edges from 1
list(DG.in_edges(1))                # incoming edges to 1
DG.out_degree(1)                    # number of outgoing edges
DG.in_degree(1)                     # number of incoming edges
```

## Graph-Level Attributes

```python
G.graph["name"] = "my graph"        # store metadata on the graph itself
G.graph                              # dict of graph attributes
```

## Degree Views

```python
G.degree()                          # DegreeView: iterable of (node, degree)
G.degree(1)                         # int: degree of node 1
G.degree([1, 2])                    # degrees of specific nodes
G.degree(weight="weight")           # weighted degree
```

## Views and Subgraphs

```python
# Read-only views — reflect changes in original graph
H = G.subgraph([1, 2, 3])           # induced subgraph
H = nx.graphviews.subgraph_view(G, filter_nodes=lambda n: n > 0)

# Restricted view (no structural modification, but attrs changeable)
V = nx.restricted_view(G, nodes_to_remove=[0], edges_to_remove=[(1, 2)])

# Type conversion views
DG = G.to_directed()                # Graph -> DiGraph
UG = DG.to_undirected()             # DiGraph -> Graph
```

## Copying

```python
H = G.copy()                        # shallow copy (node/edge attrs shared)
H = G.copy(as_view=True)            # view, not a copy
H = G.subgraph(G.nodes()).copy()    # deep-ish copy of all nodes/edges
```

Use `deepcopy` from the `copy` module for full deep copies.

## Iteration and Membership

```python
for node in G:                      # iterates over nodes
for node, data in G.nodes(data=True):
for u, v in G.edges():
for u, v, data in G.edges(data=True):
for neighbor in G.neighbors(1):
1 in G                              # same as G.has_node(1)
(1, 2) in G.edges()                 # edge membership check
```

## Clearing and Freezing

```python
G.clear()                           # remove all nodes and edges
G.clear_edges()                     # keep nodes, remove edges
G.clear_nodes()                     # remove nodes and edges
nx.freeze(G)                        # make graph immutable
nx.is_frozen(G)                     # check if frozen
```

## Useful Utility Functions

```python
nx.common_neighbors(G, u, v)        # nodes connected to both u and v
nx.all_neighbors(G, n)              # neighbors including self-loops (undirected)
nx.non_neighbors(G, n)              # nodes not adjacent to n
nx.non_edges(G)                     # all non-edge pairs
nx.selfloop_edges(G)                # edges that are self-loops
nx.nodes_with_selfloops(G)
nx.number_of_selfloops(G)
nx.is_weighted(G, weight="weight")
nx.is_negatively_weighted(G, weight="weight")
nx.is_empty(G)                      # no nodes or no edges
nx.density(G)                       # edge density (0 to 1 for simple graphs)
```
