
import math

from PySide6.QtCore import Signal, QPointF
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsScene

from editor.map_items import ParkingObjectItem

from editor.graph_items import (
    GraphNodeItem,
    GraphEdgeItem,
    RoadSegmentItem
)


class MapScene(QGraphicsScene):

    layoutChanged = Signal()

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setSceneRect(0, 0, 1600, 1800)

        self.grid_size = 20
        self.grid_visible = True

        self.counters = {
            "parking_slot": 0,
            "building": 0,
            "gate": 0,
            "car": 0,
        }

        self.node_counter = 0

        self.road_counters = {
            "vehicle": 0,
            "pedestrian": 0
        }

        self.edge_counters = {
            "vehicle": 0,
            "pedestrian": 0
        }

        self.nodes = []
        self.edges = []
        self.road_items = []

    # =====================================
    # BACKGROUND GRID
    # =====================================

    def drawBackground(self, painter, rect):

        painter.save()

        painter.fillRect(
            rect,
            QColor("#F8FAFC")
        )

        if self.grid_visible:

            grid = self.grid_size

            left = math.floor(rect.left() / grid) * grid
            top = math.floor(rect.top() / grid) * grid

            right = math.ceil(rect.right())
            bottom = math.ceil(rect.bottom())

            for x in range(left, right + grid, grid):

                major = (x // grid) % 5 == 0

                color = (
                    QColor("#DCE5EF")
                    if major else QColor("#EDF2F7")
                )

                painter.setPen(QPen(color, 0))

                painter.drawLine(
                    x, int(rect.top()),
                    x, bottom
                )

            for y in range(top, bottom + grid, grid):

                major = (y // grid) % 5 == 0

                color = (
                    QColor("#DCE5EF")
                    if major else QColor("#EDF2F7")
                )

                painter.setPen(QPen(color, 0))

                painter.drawLine(
                    int(rect.left()), y,
                    right, y
                )

        painter.restore()

    # =====================================
    # SNAP TO GRID
    # =====================================

    def snap_point(self, point):

        grid = self.grid_size

        x = round(point.x() / grid) * grid
        y = round(point.y() / grid) * grid

        return QPointF(x, y)

    # =====================================
    # PARKING OBJECTS
    # =====================================

    def add_object(self, tool, position):

        if tool not in self.counters:
            return None

        self.counters[tool] += 1

        number = self.counters[tool]

        if tool == "parking_slot":

            object_id = f"P{number:02d}"
            label = object_id

        elif tool == "building":

            object_id = f"BLD{number:02d}"
            label = f"GEDUNG {number:02d}"

        elif tool == "gate":

            object_id = f"GATE{number:02d}"
            label = "GERBANG"

        elif tool == "car":

            object_id = f"CAR{number:02d}"
            label = f"MOBIL {number:02d}"

        self.clearSelection()

        item = ParkingObjectItem(
            tool,
            object_id,
            label
        )

        self.addItem(item)

        item.setPos(
            self.snap_point(position)
        )

        item.setSelected(True)

        self.layoutChanged.emit()

        return item

    # =====================================
    # GET ALL PARKING OBJECTS
    # =====================================

    def get_objects(self, object_type=None):

        objects = [
            item
            for item in self.items()
            if isinstance(item, ParkingObjectItem)
        ]

        if object_type is not None:

            objects = [
                item
                for item in objects
                if item.object_type == object_type
            ]

        return sorted(
            objects,
            key=lambda item: item.object_id
        )

    # =====================================
    # GET OBJECT BY ID
    # =====================================

    def get_object_by_id(
        self,
        object_id,
        object_type=None
    ):

        for item in self.get_objects(object_type):

            if item.object_id == object_id:
                return item

        return None

    # =====================================
    # GET PARKING SLOTS
    # =====================================

    def get_parking_slots(self, status=None):

        slots = self.get_objects(
            "parking_slot"
        )

        if status is not None:

            status = str(status).lower().strip()

            if status not in ParkingObjectItem.PARKING_STATUS_CONFIG:
                raise ValueError(
                    f"Invalid parking status: {status}"
                )

            slots = [
                slot
                for slot in slots
                if slot.get_parking_status() == status
            ]

        return slots

    # =====================================
    # GET BUILDINGS
    # =====================================

    def get_buildings(self):

        return self.get_objects("building")

    # =====================================
    # GET GATES
    # =====================================

    def get_gates(self):

        return self.get_objects("gate")

    # =====================================
    # GET CARS
    # =====================================

    def get_cars(self):

        return self.get_objects("car")

    # =====================================
    # CHANGE PARKING SLOT STATUS
    # =====================================

    def set_parking_slot_status(
        self,
        slot_id,
        status
    ):

        slot = self.get_object_by_id(
            slot_id,
            "parking_slot"
        )

        if slot is None:
            return False

        slot.set_parking_status(status)

        self.layoutChanged.emit()

        return True

    # =====================================
    # RESET PARKING SLOTS
    # =====================================

    def reset_parking_slots(self):

        for slot in self.get_parking_slots():

            slot.set_parking_status(
                "available"
            )

        self.layoutChanged.emit()

    # =====================================
    # COUNT PARKING STATUS
    # =====================================

    def count_parking_slots_by_status(self, status):

        return len(
            self.get_parking_slots(status)
        )

    # =====================================
    # ADD GRAPH NODE
    # =====================================

    def add_node(self, position):

        self.node_counter += 1

        node_id = f"N{self.node_counter:02d}"

        self.clearSelection()

        node = GraphNodeItem(node_id)

        self.addItem(node)

        node.setPos(
            self.snap_point(position)
        )

        node.setSelected(True)

        self.nodes.append(node)

        self.layoutChanged.emit()

        return node

    # =====================================
    # GET NODE BY ID
    # =====================================

    def get_node_by_id(self, node_id):

        for node in self.nodes:

            if node.node_id == node_id:
                return node

        return None

    # =====================================
    # ADD ROAD
    # =====================================

    def add_road(
        self,
        start,
        end,
        width=70,
        mode="vehicle"
    ):

        distance = math.hypot(
            end.x() - start.x(),
            end.y() - start.y()
        )

        if distance < 20:
            return None

        if mode not in self.road_counters:
            return None

        self.road_counters[mode] += 1

        number = self.road_counters[mode]

        prefix = "R" if mode == "vehicle" else "W"

        road_id = f"{prefix}{number:02d}"

        road = RoadSegmentItem(
            road_id,
            start,
            end,
            width,
            mode
        )

        self.addItem(road)

        self.road_items.append(road)

        self.layoutChanged.emit()

        return road

    # =====================================
    # CONNECT GRAPH NODES
    # =====================================

    def connect_nodes(
        self,
        node_a,
        node_b,
        mode="vehicle"
    ):

        if node_a is node_b:
            return None

        if node_a not in self.nodes or node_b not in self.nodes:
            return None

        if mode not in self.edge_counters:
            return None

        for edge in self.edges:

            same_nodes = (
                edge.node_a is node_a
                and edge.node_b is node_b
            ) or (
                edge.node_a is node_b
                and edge.node_b is node_a
            )

            if same_nodes and edge.mode == mode:
                return None

        self.edge_counters[mode] += 1

        number = self.edge_counters[mode]

        prefix = "E" if mode == "vehicle" else "W"

        edge_id = f"{prefix}{number:02d}"

        edge = GraphEdgeItem(
            edge_id,
            node_a,
            node_b,
            mode
        )

        self.addItem(edge)

        self.edges.append(edge)

        self.layoutChanged.emit()

        return edge

    # =====================================
    # GET CONNECTED NODES BY NETWORK
    # =====================================

    def get_connected_nodes(self, mode="vehicle"):

        if mode not in self.edge_counters:
            return []

        connected_ids = set()

        for edge in self.edges:

            if edge.mode != mode:
                continue

            connected_ids.add(
                edge.node_a.node_id
            )

            connected_ids.add(
                edge.node_b.node_id
            )

        return [
            node
            for node in self.nodes
            if node.node_id in connected_ids
        ]

    # =====================================
    # FIND NEAREST CONNECTED GRAPH NODE
    # =====================================

    def find_nearest_node(
        self,
        position,
        mode="vehicle"
    ):

        connected_nodes = self.get_connected_nodes(
            mode
        )

        if not connected_nodes:
            return None

        return min(
            connected_nodes,
            key=lambda node: math.hypot(
                node.pos().x() - position.x(),
                node.pos().y() - position.y()
            )
        )

    # =====================================
    # MAP OBJECT TO NEAREST GRAPH NODE
    # =====================================

    def find_nearest_node_for_object(
        self,
        item,
        mode="vehicle"
    ):

        if not isinstance(item, ParkingObjectItem):
            return None

        if item.scene() is not self:
            return None

        return self.find_nearest_node(
            item.scenePos(),
            mode
        )

    # =====================================
    # UPDATE EDGES AFTER NODE MOVEMENT
    # =====================================

    def update_edges_for_node(self, node):

        for edge in self.edges:

            if (
                edge.node_a is node
                or edge.node_b is node
            ):

                edge.update_position()

    # =====================================
    # DELETE SELECTED OBJECTS
    # =====================================

    def remove_selected(self):

        selected = list(
            self.selectedItems()
        )

        for item in selected:

            if isinstance(item, GraphNodeItem):

                connected_edges = [
                    edge
                    for edge in self.edges
                    if (
                        edge.node_a is item
                        or edge.node_b is item
                    )
                ]

                for edge in connected_edges:

                    self.removeItem(edge)

                    if edge in self.edges:
                        self.edges.remove(edge)

                if item in self.nodes:
                    self.nodes.remove(item)

                self.removeItem(item)

            elif isinstance(item, GraphEdgeItem):

                if item in self.edges:
                    self.edges.remove(item)

                self.removeItem(item)

            elif isinstance(item, RoadSegmentItem):

                if item in self.road_items:
                    self.road_items.remove(item)

                self.removeItem(item)

            elif isinstance(item, ParkingObjectItem):

                self.removeItem(item)

        self.layoutChanged.emit()

    # =====================================
    # COUNT PARKING OBJECTS
    # =====================================

    def count_objects(self, object_type=None):

        return len(
            self.get_objects(object_type)
        )

    # =====================================
    # COUNT GRAPH NODES
    # =====================================

    def count_nodes(self):

        return len(self.nodes)

    # =====================================
    # COUNT GRAPH EDGES
    # =====================================

    def count_edges(self, mode=None):

        if mode is None:
            return len(self.edges)

        return sum(
            1
            for edge in self.edges
            if edge.mode == mode
        )

    # =====================================
    # COUNT ROADS
    # =====================================

    def count_roads(self, mode=None):

        if mode is None:
            return len(self.road_items)

        return sum(
            1
            for road in self.road_items
            if road.mode == mode
        )

    # =====================================
    # GRID VISIBILITY
    # =====================================

    def set_grid_visible(self, visible):

        self.grid_visible = visible

        self.update()
