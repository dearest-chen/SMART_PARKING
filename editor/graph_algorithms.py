
import heapq
import math


# =====================================
# DIJKSTRA ALGORITHM
# =====================================

def dijkstra(nodes, edges, start_node_id, mode="vehicle"):

    # VALIDATE MODE

    if mode not in ("vehicle", "pedestrian"):
        raise ValueError(
            f"Invalid network mode: {mode}"
        )

    # BUILD NODE ID LIST

    node_ids = {
        node.node_id
        for node in nodes
    }

    if start_node_id not in node_ids:
        raise ValueError(
            f"Start node '{start_node_id}' not found."
        )

    # BUILD ADJACENCY LIST

    adjacency = {
        node_id: []
        for node_id in node_ids
    }

    for edge in edges:

        # Only use the selected network mode.

        if edge.mode != mode:
            continue

        node_a = edge.node_a.node_id
        node_b = edge.node_b.node_id

        if node_a not in adjacency or node_b not in adjacency:
            raise ValueError(
                f"Edge {edge.edge_id} references an invalid node."
            )

        weight = float(edge.weight_m)

        if not math.isfinite(weight) or weight < 0:
            raise ValueError(
                f"Invalid weight on edge {edge.edge_id}."
            )

        # UNDIRECTED GRAPH

        adjacency[node_a].append(
            (node_b, weight, edge)
        )

        adjacency[node_b].append(
            (node_a, weight, edge)
        )

    # INITIALIZE DISTANCES

    distances = {
        node_id: math.inf
        for node_id in node_ids
    }

    previous = {}

    visited_order = []

    distances[start_node_id] = 0.0

    priority_queue = [
        (0.0, start_node_id)
    ]

    settled = set()

    # =================================
    # MAIN DIJKSTRA PROCESS
    # =================================

    while priority_queue:

        current_distance, current_id = heapq.heappop(
            priority_queue
        )

        if current_id in settled:
            continue

        if current_distance > distances[current_id]:
            continue

        settled.add(current_id)

        visited_order.append(current_id)

        # CHECK NEIGHBORS

        for neighbor_id, weight, edge in adjacency[current_id]:

            if neighbor_id in settled:
                continue

            alternative_distance = (
                current_distance + weight
            )

            # RELAXATION

            if alternative_distance < distances[neighbor_id] - 1e-12:

                distances[neighbor_id] = alternative_distance

                previous[neighbor_id] = (
                    current_id,
                    edge
                )

                heapq.heappush(
                    priority_queue,
                    (
                        alternative_distance,
                        neighbor_id
                    )
                )

    return {
        "distances": distances,
        "previous": previous,
        "visited_order": visited_order
    }


# =====================================
# RECONSTRUCT SHORTEST PATH
# =====================================

def reconstruct_shortest_path(
    result,
    start_id,
    target_id
):

    distances = result["distances"]
    previous = result["previous"]

    if target_id not in distances:
        raise ValueError(
            f"Target node '{target_id}' not found."
        )

    # NO PATH

    if math.isinf(distances[target_id]):
        return None

    node_ids = [target_id]
    path_edges = []

    current_id = target_id

    while current_id != start_id:

        predecessor = previous.get(current_id)

        if predecessor is None:
            return None

        parent_id, edge = predecessor

        path_edges.append(edge)

        current_id = parent_id

        node_ids.append(current_id)

        if len(node_ids) > len(distances):
            raise RuntimeError(
                "Cycle detected during path reconstruction."
            )

    node_ids.reverse()
    path_edges.reverse()

    return {
        "node_ids": node_ids,
        "edges": path_edges
    }


# =====================================
# EXTRACT SHORTEST PATH TREE EDGES
# =====================================

def get_shortest_path_tree_edges(result):

    return [
        edge
        for parent_id, edge in result["previous"].values()
    ]
