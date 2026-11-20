from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QBrush
from PySide6.QtWidgets import (
    QGraphicsLineItem,
    QGraphicsEllipseItem
)


# =====================================
# CLEAR ROUTE VISUALIZATION
# =====================================

def clear_route_visualization(scene):

    overlay_items = getattr(
        scene,
        "_route_visualization_items",
        []
    )

    for item in overlay_items:

        if item.scene() is scene:
            scene.removeItem(item)

    scene._route_visualization_items = []
    scene._dijkstra_current_marker = None

    scene.update()


# =====================================
# ADD OVERLAY ITEM
# =====================================

def add_overlay(scene, item, pen, z_value):

    item.setPen(pen)
    item.setZValue(z_value)

    item.setAcceptedMouseButtons(
        Qt.MouseButton.NoButton
    )

    scene.addItem(item)

    scene._route_visualization_items.append(
        item
    )


# =====================================
# NODE MARKER
# =====================================

def add_node_marker(scene, node, color, z_value=40):

    marker = QGraphicsEllipseItem(
        -18, -18, 36, 36
    )

    marker.setPos(
        node.pos()
    )

    marker.setPen(
        QPen(
            QColor(color),
            3
        )
    )

    marker.setBrush(
        QBrush(Qt.BrushStyle.NoBrush)
    )

    marker.setZValue(z_value)

    marker.setAcceptedMouseButtons(
        Qt.MouseButton.NoButton
    )

    scene.addItem(marker)

    scene._route_visualization_items.append(
        marker
    )

    return marker




# =====================================
# DIJKSTRA EXPLORATION STEP
# =====================================

def draw_dijkstra_progress(scene, node, predecessor_edge=None):
    """
    Draw one settled Dijkstra node and its predecessor edge.
    Previous visited-node markers remain visible during exploration.
    The larger current marker moves from node to node.
    """

    if not hasattr(scene, "_route_visualization_items"):
        scene._route_visualization_items = []

    # Remove the previous moving marker, but keep visited markers.
    current_marker = getattr(
        scene,
        "_dijkstra_current_marker",
        None
    )

    if current_marker is not None:
        if current_marker.scene() is scene:
            scene.removeItem(current_marker)

        if current_marker in scene._route_visualization_items:
            scene._route_visualization_items.remove(current_marker)

    # Show the predecessor edge used to reach this node.
    if predecessor_edge is not None:
        edge_overlay = QGraphicsLineItem(
            predecessor_edge.line()
        )

        add_overlay(
            scene,
            edge_overlay,
            QPen(
                QColor("#38BDF8"),
                3,
                Qt.PenStyle.DashLine,
                Qt.PenCapStyle.RoundCap
            ),
            16
        )

    # Persistent marker: this node has been settled/visited.
    visited_marker = QGraphicsEllipseItem(
        -14, -14, 28, 28
    )

    visited_marker.setPos(node.pos())
    visited_marker.setPen(
        QPen(QColor("#0EA5E9"), 2)
    )
    visited_marker.setBrush(
        QBrush(QColor(14, 165, 233, 35))
    )
    visited_marker.setZValue(39)
    visited_marker.setAcceptedMouseButtons(
        Qt.MouseButton.NoButton
    )

    scene.addItem(visited_marker)
    scene._route_visualization_items.append(visited_marker)

    # Moving marker: highlights the node currently being processed.
    current_marker = QGraphicsEllipseItem(
        -21, -21, 42, 42
    )

    current_marker.setPos(node.pos())
    current_marker.setPen(
        QPen(QColor("#0284C7"), 3)
    )
    current_marker.setBrush(
        QBrush(Qt.BrushStyle.NoBrush)
    )
    current_marker.setZValue(41)
    current_marker.setAcceptedMouseButtons(
        Qt.MouseButton.NoButton
    )

    scene.addItem(current_marker)
    scene._route_visualization_items.append(current_marker)

    scene._dijkstra_current_marker = current_marker
    scene.update()


# =====================================
# DRAW SHORTEST PATH TREE
# =====================================

def draw_shortest_path_tree(
    scene,
    tree_edges,
    path_edges,
    start_node,
    target_node
):

    clear_route_visualization(scene)

    scene._route_visualization_items = []

    # SHORTEST PATH TREE

    for edge in tree_edges:

        overlay = QGraphicsLineItem(
            edge.line()
        )

        pen = QPen(
            QColor("#A855F7"),
            5,
            Qt.PenStyle.DashLine,
            Qt.PenCapStyle.RoundCap
        )

        add_overlay(
            scene,
            overlay,
            pen,
            15
        )

    # FINAL SHORTEST PATH

    for edge in path_edges:

        overlay = QGraphicsLineItem(
            edge.line()
        )

        pen = QPen(
            QColor("#F97316"),
            8,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap
        )

        add_overlay(
            scene,
            overlay,
            pen,
            20
        )

    # START / DESTINATION MARKERS

    if start_node is target_node:

        add_node_marker(
            scene,
            start_node,
            "#EAB308"
        )

    else:

        add_node_marker(
            scene,
            start_node,
            "#16A34A"
        )

        add_node_marker(
            scene,
            target_node,
            "#DC2626"
        )

    scene.update()


# =====================================
# DRAW PARKING ASSIGNMENT ROUTES
# =====================================

def draw_parking_assignment_routes(
    scene,
    vehicle_edges,
    pedestrian_edges,
    vehicle_start_node,
    vehicle_target_node,
    pedestrian_start_node,
    pedestrian_target_node
):

    clear_route_visualization(scene)

    scene._route_visualization_items = []

    # VEHICLE ROUTE: GATE -> PARKING SLOT

    for edge in vehicle_edges:

        overlay = QGraphicsLineItem(
            edge.line()
        )

        pen = QPen(
            QColor("#F97316"),
            8,
            Qt.PenStyle.SolidLine,
            Qt.PenCapStyle.RoundCap
        )

        add_overlay(
            scene,
            overlay,
            pen,
            20
        )

    # PEDESTRIAN ROUTE: PARKING SLOT -> BUILDING

    for edge in pedestrian_edges:

        overlay = QGraphicsLineItem(
            edge.line()
        )

        pen = QPen(
            QColor("#2563EB"),
            6,
            Qt.PenStyle.DashLine,
            Qt.PenCapStyle.RoundCap
        )

        add_overlay(
            scene,
            overlay,
            pen,
            21
        )

    # VEHICLE START: ENTRY GATE

    add_node_marker(
        scene,
        vehicle_start_node,
        "#2563EB"
    )

    # VEHICLE DESTINATION: PARKING SLOT

    add_node_marker(
        scene,
        vehicle_target_node,
        "#F97316"
    )

    # PEDESTRIAN START: PARKING SLOT

    add_node_marker(
        scene,
        pedestrian_start_node,
        "#16A34A"
    )

    # PEDESTRIAN DESTINATION: BUILDING

    add_node_marker(
        scene,
        pedestrian_target_node,
        "#DC2626"
    )

    scene.update()
