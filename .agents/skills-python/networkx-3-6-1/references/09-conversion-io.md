# Conversion and I/O

## NumPy Arrays

```python
# Graph → adjacency matrix
A = nx.to_numpy_array(G, nodelist=None, weight="weight", dtype=float)
A = nx.to_numpy_array(G, weight=None)            # binary (0/1)

# Adjacency matrix → graph
G = nx.from_numpy_array(A, create_using=nx.Graph)
G = nx.from_numpy_array(A, create_using=nx.DiGraph)
```

For `MultiGraph`, parallel edge weights are summed by default. Use `parallel_edge="replace"` or custom reduction.

## Pandas DataFrames

### Edge Lists

```python
# Graph → DataFrame
df = nx.to_pandas_edgelist(G, source="src", target="tgt", edge_attr=["weight"])

# DataFrame → graph
G = nx.from_pandas_edgelist(df, source="src", target="tgt",
                            edge_attr=["weight"], create_using=nx.Graph)
```

### Adjacency

```python
df = nx.to_pandas_adjacency(G, weight="weight")
G = nx.from_pandas_adjacency(df, create_using=nx.Graph)
```

## SciPy Sparse Arrays

```python
# Graph → sparse matrix
sparse_A = nx.to_scipy_sparse_array(G, nodelist=None, weight="weight", format="csr")

# Sparse matrix → graph
G = nx.from_scipy_sparse_array(sparse_A, create_using=nx.Graph)
```

Supported formats: `csr`, `csc`, `coo`, `bsr`, `lil`, `dok`, `dia`.

## Dict-of-Dicts / Dict-of-Lists

```python
# Graph → dict
dod = nx.to_dict_of_dicts(G, weight="weight")
dol = nx.to_dict_of_lists(G)

# Dict → graph
G = nx.from_dict_of_dicts(dod)
G = nx.from_dict_of_lists(dol)
```

## Edge Lists

```python
edges = list(nx.to_edgelist(G))                  # [(u, v), ...]
G = nx.from_edgelist(edges, create_using=nx.Graph)
```

## Relabeling Nodes

```python
# Mapping dict
H = nx.relabel_nodes(G, {0: "a", 1: "b", 2: "c"})
H = nx.relabel_nodes(G, lambda x: x * 2)        # function mapping

# In-place
nx.relabel_nodes(G, mapping, copy=False)

# Sequential integer labels
H = nx.convert_node_labels_to_integers(G, first_label=0, ordering="sorted")
```

## File Formats

### GraphML (XML-based, preserves attributes)

```python
nx.write_graphml(G, "graph.graphml")
G = nx.read_graphml("graph.graphml")
G = nx.read_graphml("graph.graphml", node_type=str)   # control node type
```

### GEXF (Gephi format)

```python
nx.write_gexf(G, "graph.gexf")
G = nx.read_gexf("graph.gexf")
```

### Edge List Files

```python
# Write
nx.write_edgelist(G, "edges.txt", delimiter=" ", data=False)
nx.write_edgelist(G, "edges.txt", delimiter=",", data=["weight"])  # with attrs

# Read
G = nx.read_edgelist("edges.txt", delimiter=" ", nodetype=int, create_using=nx.Graph)
```

### Pajek (.net)

```python
nx.write_pajek(G, "graph.net")
G = nx.read_pajek("graph.net")
```

### GML

```python
nx.write_gml(G, "graph.gml")
G = nx.read_gml("graph.gml")
```

### Sparse6 / Graph6 (compact text encoding)

```python
s6 = nx.to_sparse6_bytes(G).decode()             # string
G = nx.from_sparse6_bytes(s6.encode())            # from string
g6 = nx.to_graph6_bytes(G).decode()               # undirected only
G = nx.from_graph6_bytes(g6.encode())
```

### JSON (via json_graph)

```python
import json
from networkx.readwrite import json_graph

# Node-link format (most common, for D3.js)
data = json_graph.node_link_data(G)
json_str = json.dumps(data)
G = json_graph.node_link_graph(json.loads(json_str))

# Other formats
data = json_graph.adjacency_data(G)
data = json_graph.edge_data(G)
data = json_graph.cytoscape_data(G)              # Cytoscape.js format
```

## Key Gotchas

- **`to_numpy_array` ordering:** pass `nodelist` to control row/column order. Without it, order follows `G.nodes()` which may not be sorted.
- **`read_edgelist` with `nodetype`:** by default nodes are strings. Pass `nodetype=int` for integer labels.
- **GraphML node types:** `read_graphml` tries to infer node label types but defaults to strings. Use `node_type=str` or `node_type=int` explicitly.
- **Sparse6 preserves direction** and attributes minimally. Graph6 is undirected only with no attributes.
- **JSON node-link format** stores all node and edge attributes, making it the most complete for serialization.
- **SciPy sparse conversion** sums parallel edge weights in multigraphs. Use `G.to_directed().to_undirected()` to collapse before converting if needed.
