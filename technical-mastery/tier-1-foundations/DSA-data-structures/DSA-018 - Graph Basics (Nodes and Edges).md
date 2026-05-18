---
id: DSA-018
title: Graph Basics (Nodes and Edges)
category: Data Structures & Algorithms
tier: tier-1-foundations
folder: DSA-data-structures
difficulty: ★☆☆
depends_on: DSA-015
used_by: DSA-035, DSA-036, DSA-039, DSA-052, DSA-060, DSA-063
related: DSA-015, DSA-039, DSA-052
tags:
  - data-structures
  - graph
  - nodes
  - edges
  - fundamentals
  - networks
status: complete
version: 4
layout: default
parent: "Data Structures & Algorithms"
grand_parent: "Technical Mastery"
nav_order: 18
permalink: /technical-mastery/dsa/graph-basics/
---

## TL;DR

A graph models relationships between entities as nodes
(vertices) connected by edges - the structure behind social
networks, maps, dependency trees, and the internet itself.

---

### Metadata

| Field | Value |
|-------|-------|
| **ID** | DSA-018 |
| **Difficulty** | ★☆☆ Foundational |
| **Category** | Data Structures & Algorithms |
| **Tags** | data-structures, graph, nodes, edges |
| **Prerequisites** | DSA-015 |

---

### The Problem This Solves

Trees model hierarchical relationships (one parent per node).
Many real-world relationships are non-hierarchical: a person
can know many other people; a road connects many intersections;
a package can depend on many packages. Graphs generalize
trees to arbitrary relationships.

---

### Textbook Definition

A graph G = (V, E) consists of a set of vertices V (also
called nodes) and a set of edges E connecting pairs of
vertices. Directed graphs (digraphs) have edges with
direction (source → destination). Undirected graphs have
bidirectional edges. Weighted graphs assign a cost to each
edge. Edges can be self-loops. Unlike trees, graphs can
have cycles.

---

### Understand It in 30 Seconds

Cities connected by roads. Cities = nodes (vertices).
Roads = edges. A two-way road = undirected edge.
A one-way street = directed edge. Road with a toll =
weighted edge. The entire road map = a graph.

Shortest path from A to B: a graph problem.
Can you get from A to B at all: a graph problem.

---

### How It Works

**Graph types:**

```
Undirected:         Directed:          Weighted:
A - B               A → B              A --(5)--> B
|   |               ↑   ↓              |           |
C - D               C ← D             (3)         (2)
                                       ↓           ↓
                                       C --(1)--> D
```

**Graph vocabulary:**

| Term | Definition |
|------|-----------|
| Vertex (node) | Entity in the graph |
| Edge (arc) | Connection between two vertices |
| Degree | Number of edges connected to a vertex |
| In-degree | Number of incoming edges (directed) |
| Out-degree | Number of outgoing edges (directed) |
| Path | Sequence of vertices connected by edges |
| Cycle | Path that starts and ends at same vertex |
| Connected | All vertices reachable from any vertex |
| DAG | Directed Acyclic Graph - no cycles |

**Real-world graph applications:**

| System | Vertices | Edges |
|--------|----------|-------|
| Social network | Users | Friendships |
| Internet | Servers | Connections |
| Road map | Intersections | Roads |
| Git commits | Commits | Parent-child |
| Maven deps | Libraries | Dependencies |
| Web pages | Pages | Links |

---

### Comparison Table

| Property | Tree | DAG | General Graph |
|---------|------|-----|---------------|
| Cycles | No | No | Yes |
| Multiple parents | No | Yes | Yes |
| Root required | Yes | Not necessarily | No |
| Edge direction | Parent→child | Directed | Either |
| Real-world example | File system | Build dependencies | Road map |

---

### Common Misconceptions

| Misconception | Reality |
|---------------|---------|
| "A tree is not a graph" | A tree IS a graph (connected, acyclic, undirected); all trees are graphs but not all graphs are trees |
| "Graphs are only for social networks" | Any system with relationships is a graph: packages, network topology, state machines |
| "Directed and undirected graphs are represented differently" | Both use adjacency list or matrix; directed just adds directionality to edges |

---

### Failure Modes & Diagnosis

**Failure: Infinite loop in graph traversal**
- Cause: Graph has cycles; traversal revisits nodes
- Fix: Mark visited nodes; only process unvisited nodes
  (BFS/DFS visited array)

**Failure: Treating directed graph as undirected**
- Cause: Bidirectional traversal on one-way edges
- Symptom: Reachability analysis incorrect
- Fix: Clearly model edge directionality in representation

---

### Quick Reference Card

| Concept | One-line definition |
|---------|---------------------|
| Vertex | Node/entity |
| Edge | Connection between two vertices |
| Directed | Edge has a direction (A → B) |
| Undirected | Edge is bidirectional (A <-> B) |
| Weighted | Edge has a cost/distance |
| DAG | Directed, no cycles (e.g. dependency graph) |
| Connected | Every vertex reachable from every other |

---

### Mastery Checklist

- [ ] Can explain the difference between directed and
      undirected graphs with examples
- [ ] Can identify whether a given system is best modeled
      as a tree, DAG, or general graph
- [ ] Understands the visited array requirement for graph
      traversal to prevent cycles
- [ ] Can name 5 real systems that are graphs

---

### Think About This

1. Is your project's Maven `pom.xml` a tree, DAG, or
   general graph? Can it have cycles? What would a cycle
   mean?

2. Given a graph of 1000 cities with roads, how do you
   determine if every city is reachable from the capital?
   What algorithm and what graph representation?

---

### Interview Deep-Dive

**Q1 (Easy):** What is the difference between a tree and
a graph?

> A tree is a connected acyclic undirected graph where every
> node has exactly one parent (except the root). A graph
> is more general: can have cycles, disconnected components,
> multiple edges between nodes, and self-loops. All trees are
> graphs; not all graphs are trees.

**Q2 (Medium):** When would you use a directed acyclic graph
(DAG) instead of a tree?

> A DAG is appropriate when an entity can have multiple
> parents. Build systems (a library can be a dependency of
> multiple projects), course prerequisites (a course can be
> a prerequisite for multiple courses), and version control
> merge history (a commit can have two parents) are all DAGs.
> Trees are DAGs where every node has exactly one parent.
