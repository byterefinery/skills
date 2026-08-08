# DiGraph

## Overview

`DiGraph` is schedula's directed graph implementation. It stores the Dispatcher's dataflow model with nodes (data, function, dispatcher) and weighted edges.

## Construction

```python
from schedula import DiGraph

graph = DiGraph()
```

## Nodes

### Adding Nodes

```python
graph.add_node('node_id', type='data', weight=1.0, **attrs)
```

### Node Access

```python
# Check existence
'node_id' in graph.nodes

# Get node attributes
attrs = graph.nodes['node_id']

# Iterate nodes
for node_id, attrs in graph.nodes.items():
    pass

# Node count
len(graph.nodes)
```

### Removing Nodes

```python
graph.remove_node('node_id')
graph.remove_nodes_from(['a', 'b', 'c'])
```

## Edges

### Adding Edges

```python
graph.add_edge('src', 'dst', weight=1.0, **attrs)
graph.add_edge_fw('src', 'dst', value=data, **attrs)  # Forward edge with value
```

### Edge Access

```python
# Successors (outgoing edges)
for neighbor, edge_data in graph.succ['node_id'].items():
    pass

# Predecessors (incoming edges)
for neighbor, edge_data in graph.pred['node_id'].items():
    pass

# Check edge existence
graph.has_edge('src', 'dst')

# Get edge data
edge_data = graph.succ['src']['dst']

# Iterate edges
for (src, dst), data in graph.edges.items():
    pass
```

### Removing Edges

```python
graph.remove_edge('src', 'dst')
graph.remove_edges_from([('a', 'b'), ('c', 'd')])
```

## Subgraph

```python
# Induced subgraph (nodes and edges between them)
sub = graph.subgraph(['node_a', 'node_b', 'node_c'])
```

Returns a new `DiGraph` containing only the specified nodes and edges between them. Node/edge attributes reference the original graph.

## Node Iteration

```python
# Neighbors of a node (successors)
for neighbor in graph['node_id']:
    pass

# All neighbors (dict of edge data)
neighbors = graph['node_id']  # {neighbor: edge_data, ...}
```
