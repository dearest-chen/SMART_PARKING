
import json
import math
import re

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF

from editor.map_items import ParkingObjectItem

from editor.graph_items import (
    GraphNodeItem,
    GraphEdgeItem,
    RoadSegmentItem
)


FORMAT_NAME = "smart_parking_layout"
FORMAT_VERSION = 2


# =====================================
# HELPER FUNCTIONS
# =====================================

def get_max_id(records):

    maximum = 0

    for record in records:

        match = re.search(
            r"(\d+)$",
            str(record.get("id", ""))
        )

        if match:
            maximum = max(
                maximum,
                int(match.group(1))
            )

    return maximum


def get_counter(counters, group, key=None):

    if group == "nodes":
        value = counters.get("nodes", 0)

    else:
        group_data = counters.get(group, {})

        value = (
            group_data.get(key, 0)
            if isinstance(group_data, dict)
            else 0
        )

    if type(value) is int and value >= 0:
        return value

    return 0


def valid_number(value, field):

    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
    ):
        raise ValueError(
            f"Invalid number: {field}"
        )

    return float(value)


# =====================================
# BUILD LAYOUT DATA
# =====================================

def build_layout_data(scene):

    rect = scene.sceneRect()

    # PARKING OBJECTS

    objects = []

    for item in scene.items():

        if isinstance(item, ParkingObjectItem):

            object_data = {
                "type": item.object_type,
                "id": item.object_id,
                "label": item.label,
                "x": item.pos().x(),
                "y": item.pos().y()
            }

            # SAVE PARKING STATUS

            if item.object_type == "parking_slot":

                object_data["parking_status"] = (
                    item.get_parking_status()
                )

            objects.append(object_data)

    # GRAPH NODES

    nodes = []

    for node in scene.nodes:

        nodes.append({
            "id": node.node_id,
            "x": node.pos().x(),
            "y": node.pos().y()
        })

    # ROAD SEGMENTS

    roads = []

    for road in scene.road_items:

        line = road.line()

        roads.append({
            "id": road.road_id,
            "mode": road.mode,
            "width": road.road_width,
            "x1": line.x1(),
            "y1": line.y1(),
            "x2": line.x2(),
            "y2": line.y2()
        })

    # GRAPH EDGES

    edges = []

    for edge in scene.edges:

        edges.append({
            "id": edge.edge_id,
            "node_a": edge.node_a.node_id,
            "node_b": edge.node_b.node_id,
            "mode": edge.mode
        })

    return {
        "format": FORMAT_NAME,
        "version": FORMAT_VERSION,

        "scene": {
            "x": rect.x(),
            "y": rect.y(),
            "width": rect.width(),
            "height": rect.height()
        },

        "settings": {
            "grid_size": scene.grid_size,
            "grid_visible": scene.grid_visible
        },

        "objects": objects,
        "nodes": nodes,
        "roads": roads,
        "edges": edges,

        "counters": {
            "objects": dict(scene.counters),
            "nodes": scene.node_counter,
            "roads": dict(scene.road_counters),
            "edges": dict(scene.edge_counters)
        }
    }


# =====================================
# VALIDATE LAYOUT
# =====================================

def validate_layout_data(data):

    if not isinstance(data, dict):
        raise ValueError("Invalid layout file.")

    if data.get("format") != FORMAT_NAME:
        raise ValueError("Unsupported project format.")

    version = data.get("version")

    # SUPPORT VERSION 1 AND VERSION 2

    if (
        type(version) is not int
        or version not in (1, FORMAT_VERSION)
    ):
        raise ValueError("Unsupported layout version.")

    scene_data = data.get("scene")
    settings = data.get("settings")

    if not isinstance(scene_data, dict):
        raise ValueError("Invalid scene data.")

    if not isinstance(settings, dict):
        raise ValueError("Invalid settings.")

    for field in ("x", "y", "width", "height"):

        valid_number(
            scene_data.get(field),
            f"scene.{field}"
        )

    if (
        scene_data["width"] <= 0
        or scene_data["height"] <= 0
    ):
        raise ValueError("Invalid scene dimensions.")

    grid_size = settings.get("grid_size")

    if type(grid_size) is not int or grid_size <= 0:
        raise ValueError("Invalid grid size.")

    if type(settings.get("grid_visible")) is not bool:
        raise ValueError("Invalid grid visibility.")

    for section in ("objects", "nodes", "roads", "edges"):

        if not isinstance(data.get(section), list):
            raise ValueError(
                f"Invalid section: {section}"
            )

    # OBJECT VALIDATION

    object_ids = set()

    for obj in data["objects"]:

        if not isinstance(obj, dict):
            raise ValueError("Invalid object.")

        if obj.get("type") not in ParkingObjectItem.OBJECT_CONFIG:
            raise ValueError("Unknown object type.")

        for field in ("id", "label"):

            if (
                not isinstance(obj.get(field), str)
                or not obj[field]
            ):
                raise ValueError(
                    f"Invalid object {field}."
                )

        if obj["id"] in object_ids:
            raise ValueError("Duplicate object ID.")

        object_ids.add(obj["id"])

        valid_number(obj.get("x"), "object.x")
        valid_number(obj.get("y"), "object.y")

        # PARKING STATUS VALIDATION

        if obj["type"] == "parking_slot":

            status = obj.get(
                "parking_status",
                "available"
            )

            if (
                not isinstance(status, str)
                or status not in ParkingObjectItem.PARKING_STATUS_CONFIG
            ):
                raise ValueError(
                    "Invalid parking status."
                )

        elif "parking_status" in obj:

            raise ValueError(
                "Parking status is only valid for parking slots."
            )

    # NODE VALIDATION

    node_ids = set()

    for node in data["nodes"]:

        if not isinstance(node, dict):
            raise ValueError("Invalid node.")

        node_id = node.get("id")

        if not isinstance(node_id, str) or not node_id:
            raise ValueError("Invalid node ID.")

        if node_id in node_ids:
            raise ValueError("Duplicate node ID.")

        node_ids.add(node_id)

        valid_number(node.get("x"), "node.x")
        valid_number(node.get("y"), "node.y")

    # ROAD VALIDATION

    road_ids = set()

    for road in data["roads"]:

        if not isinstance(road, dict):
            raise ValueError("Invalid road.")

        if road.get("mode") not in (
            "vehicle",
            "pedestrian"
        ):
            raise ValueError("Invalid road mode.")

        road_id = road.get("id")

        if not isinstance(road_id, str) or not road_id:
            raise ValueError("Invalid road ID.")

        if road_id in road_ids:
            raise ValueError("Duplicate road ID.")

        road_ids.add(road_id)

        if valid_number(
            road.get("width"),
            "road.width"
        ) <= 0:
            raise ValueError("Invalid road width.")

        for field in ("x1", "y1", "x2", "y2"):

            valid_number(
                road.get(field),
                f"road.{field}"
            )

    # EDGE VALIDATION

    edge_ids = set()

    for edge in data["edges"]:

        if not isinstance(edge, dict):
            raise ValueError("Invalid edge.")

        if edge.get("mode") not in (
            "vehicle",
            "pedestrian"
        ):
            raise ValueError("Invalid edge mode.")

        edge_id = edge.get("id")

        if not isinstance(edge_id, str) or not edge_id:
            raise ValueError("Invalid edge ID.")

        if edge_id in edge_ids:
            raise ValueError("Duplicate edge ID.")

        edge_ids.add(edge_id)

        node_a = edge.get("node_a")
        node_b = edge.get("node_b")

        if (
            not isinstance(node_a, str)
            or not isinstance(node_b, str)
            or node_a not in node_ids
            or node_b not in node_ids
        ):
            raise ValueError(
                "Edge references a missing node."
            )

        if node_a == node_b:
            raise ValueError(
                "Invalid self-connected edge."
            )

    return data


# =====================================
# SAVE LAYOUT
# =====================================

def save_layout(scene, file_path):

    file_path = Path(file_path)

    data = build_layout_data(scene)

    temporary_path = file_path.with_name(
        file_path.name + ".tmp"
    )

    try:

        with temporary_path.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                allow_nan=False
            )

        temporary_path.replace(file_path)

    except Exception:

        if temporary_path.exists():
            temporary_path.unlink()

        raise

    return file_path


# =====================================
# LOAD LAYOUT
# =====================================

def load_layout(scene, file_path):

    file_path = Path(file_path)

    # READ JSON

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    # VALIDATE BEFORE MODIFYING SCENE

    validate_layout_data(data)

    # BUILD OBJECTS FIRST

    objects = []

    for obj in data["objects"]:

        item = ParkingObjectItem(
            obj["type"],
            obj["id"],
            obj["label"]
        )

        # RESTORE PARKING STATUS

        if obj["type"] == "parking_slot":

            item.set_parking_status(
                obj.get("parking_status", "available")
            )

        item.setPos(
            QPointF(
                obj["x"],
                obj["y"]
            )
        )

        objects.append(item)

    # BUILD NODES

    nodes = []
    node_lookup = {}

    for node_data in data["nodes"]:

        node = GraphNodeItem(
            node_data["id"]
        )

        node.setPos(
            QPointF(
                node_data["x"],
                node_data["y"]
            )
        )

        nodes.append(node)

        node_lookup[node.node_id] = node

    # BUILD ROADS

    roads = []

    for road_data in data["roads"]:

        start = QPointF(
            road_data["x1"],
            road_data["y1"]
        )

        end = QPointF(
            road_data["x2"],
            road_data["y2"]
        )

        road = RoadSegmentItem(
            road_data["id"],
            start,
            end,
            road_data["width"],
            road_data["mode"]
        )

        roads.append(road)

    # BUILD EDGES USING NODE REFERENCES

    edges = []

    for edge_data in data["edges"]:

        node_a = node_lookup[edge_data["node_a"]]
        node_b = node_lookup[edge_data["node_b"]]

        edge = GraphEdgeItem(
            edge_data["id"],
            node_a,
            node_b,
            edge_data["mode"]
        )

        edges.append(edge)

    # RESTORE COUNTERS

    counters = data.get("counters", {})

    object_counters = {}

    for object_type in ParkingObjectItem.OBJECT_CONFIG:

        saved = get_counter(
            counters,
            "objects",
            object_type
        )

        existing = get_max_id([
            obj for obj in data["objects"]
            if obj["type"] == object_type
        ])

        object_counters[object_type] = max(
            saved,
            existing
        )

    node_counter = max(
        get_counter(counters, "nodes"),
        get_max_id(data["nodes"])
    )

    road_counters = {}
    edge_counters = {}

    for mode in ("vehicle", "pedestrian"):

        road_counters[mode] = max(
            get_counter(counters, "roads", mode),
            get_max_id([
                road for road in data["roads"]
                if road["mode"] == mode
            ])
        )

        edge_counters[mode] = max(
            get_counter(counters, "edges", mode),
            get_max_id([
                edge for edge in data["edges"]
                if edge["mode"] == mode
            ])
        )

    # ALL DATA IS READY.
    # NOW REPLACE CURRENT SCENE.

    scene.clear()

    scene.setSceneRect(
        QRectF(
            data["scene"]["x"],
            data["scene"]["y"],
            data["scene"]["width"],
            data["scene"]["height"]
        )
    )

    scene.grid_size = data["settings"]["grid_size"]
    scene.grid_visible = data["settings"]["grid_visible"]

    scene.nodes = nodes
    scene.edges = edges
    scene.road_items = roads

    scene.counters = object_counters
    scene.node_counter = node_counter
    scene.road_counters = road_counters
    scene.edge_counters = edge_counters

    # ADD ITEMS TO SCENE

    for item in objects:
        scene.addItem(item)

    for road in roads:
        scene.addItem(road)

    for node in nodes:
        scene.addItem(node)

    for edge in edges:
        scene.addItem(edge)

    scene.clearSelection()
    scene.update()

    scene.layoutChanged.emit()

    return {
        "objects": len(objects),
        "nodes": len(nodes),
        "roads": len(roads),
        "edges": len(edges)
    }
