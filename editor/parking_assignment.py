
import math

from editor.graph_algorithms import (
    dijkstra,
    reconstruct_shortest_path
)

from editor.graph_items import GraphEdgeItem


# =====================================
# DISTANCE HELPER
# =====================================

def calculate_connector_distance(item, node):

    start = item.scenePos()
    end = node.scenePos()

    distance = math.hypot(
        end.x() - start.x(),
        end.y() - start.y()
    )

    return distance / GraphEdgeItem.PIXELS_PER_METER


# =====================================
# FIND BEST PARKING SLOT
# =====================================

def find_best_parking_slot(
    scene,
    building_id,
    gate_id=None
):

    # VALIDATE BUILDING

    building = scene.get_object_by_id(
        building_id,
        "building"
    )

    if building is None:
        return {
            "success": False,
            "message": "Building not found."
        }

    # GET AVAILABLE SLOTS

    available_slots = scene.get_parking_slots(
        "available"
    )

    if not available_slots:
        return {
            "success": False,
            "message": "No available parking slots."
        }

    # GET GATES

    if gate_id is not None:

        gate = scene.get_object_by_id(
            gate_id,
            "gate"
        )

        if gate is None:
            return {
                "success": False,
                "message": "Gate not found."
            }

        gates = [gate]

    else:
        gates = scene.get_gates()

    if not gates:
        return {
            "success": False,
            "message": "No entrance gate available."
        }

    # =================================
    # BUILDING PEDESTRIAN NODE
    # =================================

    building_node = scene.find_nearest_node_for_object(
        building,
        "pedestrian"
    )

    if building_node is None:
        return {
            "success": False,
            "message": (
                "Building is not connected "
                "to pedestrian network."
            )
        }

    # =================================
    # PEDESTRIAN DIJKSTRA
    # =================================

    try:

        pedestrian_result = dijkstra(
            scene.nodes,
            scene.edges,
            building_node.node_id,
            mode="pedestrian"
        )

    except (ValueError, RuntimeError) as error:

        return {
            "success": False,
            "message": str(error)
        }

    building_connector = calculate_connector_distance(
        building,
        building_node
    )

    # =================================
    # EVALUATE PARKING CANDIDATES
    # =================================

    candidates = []

    same_vehicle_node_count = 0

    for gate in gates:

        # ---------------------------------
        # FIND GATE VEHICLE NODE
        # ---------------------------------

        gate_node = scene.find_nearest_node_for_object(
            gate,
            "vehicle"
        )

        if gate_node is None:
            continue

        # ---------------------------------
        # VEHICLE DIJKSTRA
        # ---------------------------------

        try:

            vehicle_result = dijkstra(
                scene.nodes,
                scene.edges,
                gate_node.node_id,
                mode="vehicle"
            )

        except (ValueError, RuntimeError):

            continue

        gate_connector = calculate_connector_distance(
            gate,
            gate_node
        )

        # =================================
        # CHECK EACH AVAILABLE SLOT
        # =================================

        for slot in available_slots:

            # ---------------------------------
            # VEHICLE TARGET NODE
            # USE ACTUAL NEAREST NODE
            # ---------------------------------

            vehicle_target_node = (
                scene.find_nearest_node_for_object(
                    slot,
                    "vehicle"
                )
            )

            if vehicle_target_node is None:
                continue

            # GATE AND SLOT MUST MAP TO
            # DIFFERENT VEHICLE NODES

            if (
                vehicle_target_node.node_id
                == gate_node.node_id
            ):

                same_vehicle_node_count += 1
                continue

            # ---------------------------------
            # RECONSTRUCT VEHICLE PATH
            # ---------------------------------

            vehicle_path = reconstruct_shortest_path(
                vehicle_result,
                gate_node.node_id,
                vehicle_target_node.node_id
            )

            if vehicle_path is None:
                continue

            if not vehicle_path["edges"]:
                continue

            vehicle_graph_distance = (
                vehicle_result["distances"][
                    vehicle_target_node.node_id
                ]
            )

            slot_vehicle_connector = (
                calculate_connector_distance(
                    slot,
                    vehicle_target_node
                )
            )

            vehicle_distance = (
                gate_connector
                + vehicle_graph_distance
                + slot_vehicle_connector
            )

            # =================================
            # PEDESTRIAN TARGET NODE
            # =================================

            pedestrian_slot_node = (
                scene.find_nearest_node_for_object(
                    slot,
                    "pedestrian"
                )
            )

            if pedestrian_slot_node is None:
                continue

            # ---------------------------------
            # RECONSTRUCT PEDESTRIAN PATH
            # BUILDING -> SLOT
            # ---------------------------------

            pedestrian_path = reconstruct_shortest_path(
                pedestrian_result,
                building_node.node_id,
                pedestrian_slot_node.node_id
            )

            if pedestrian_path is None:
                continue

            pedestrian_graph_distance = (
                pedestrian_result["distances"][
                    pedestrian_slot_node.node_id
                ]
            )

            slot_pedestrian_connector = (
                calculate_connector_distance(
                    slot,
                    pedestrian_slot_node
                )
            )

            walking_distance = (
                building_connector
                + pedestrian_graph_distance
                + slot_pedestrian_connector
            )

            # =================================
            # SAVE VALID CANDIDATE
            # =================================

            candidates.append({

                "slot": slot,

                "gate": gate,

                "building": building,

                "vehicle_distance": vehicle_distance,

                "walking_distance": walking_distance,

                "vehicle_path": vehicle_path,

                "pedestrian_path": pedestrian_path,

                "vehicle_start_node": gate_node,

                "vehicle_target_node": vehicle_target_node,

                "pedestrian_start_node": pedestrian_slot_node,

                "pedestrian_target_node": building_node

            })

    # =================================
    # NO VALID CANDIDATES
    # =================================

    if not candidates:

        if same_vehicle_node_count:

            return {
                "success": False,
                "message": (
                    "Gate and parking slot are mapped "
                    "to the same vehicle node. "
                    "Add or move a vehicle graph node "
                    "near the parking slot and connect "
                    "it to the vehicle network."
                )
            }

        return {
            "success": False,
            "message": (
                "No parking slot is reachable through "
                "both vehicle and pedestrian networks. "
                "Check graph connections and node positions."
            )
        }

    # =================================
    # SELECT BEST PARKING SLOT
    # =================================

    best = min(
        candidates,
        key=lambda candidate: (
            candidate["walking_distance"],
            candidate["vehicle_distance"],
            candidate["slot"].object_id
        )
    )

    # =================================
    # RETURN ASSIGNMENT RESULT
    # =================================

    return {

        "success": True,

        "assigned": False,

        "slot": best["slot"],

        "slot_id": best["slot"].object_id,

        "building_id": best["building"].object_id,

        "gate_id": best["gate"].object_id,

        "vehicle_distance_m": round(
            best["vehicle_distance"],
            2
        ),

        "walking_distance_m": round(
            best["walking_distance"],
            2
        ),

        # GATE -> PARKING

        "vehicle_path": (
            best["vehicle_path"]["node_ids"]
        ),

        "vehicle_edges": (
            best["vehicle_path"]["edges"]
        ),

        # PARKING -> BUILDING

        "pedestrian_path": list(
            reversed(
                best["pedestrian_path"]["node_ids"]
            )
        ),

        "pedestrian_edges": list(
            reversed(
                best["pedestrian_path"]["edges"]
            )
        ),

        "vehicle_start_node_id": (
            best["vehicle_start_node"].node_id
        ),

        "vehicle_target_node_id": (
            best["vehicle_target_node"].node_id
        ),

        "pedestrian_start_node_id": (
            best["pedestrian_start_node"].node_id
        ),

        "pedestrian_target_node_id": (
            best["pedestrian_target_node"].node_id
        )

    }


# =====================================
# ASSIGN PARKING SLOT
# =====================================

def assign_parking_slot(
    scene,
    building_id,
    gate_id=None
):

    result = find_best_parking_slot(
        scene,
        building_id,
        gate_id
    )

    if not result["success"]:
        return result

    slot = result["slot"]

    if slot.get_parking_status() != "available":

        return {
            "success": False,
            "message": (
                "Selected parking slot is no longer available."
            )
        }

    slot.set_parking_status("reserved")

    scene.layoutChanged.emit()

    result["assigned"] = True

    result["message"] = (
        f"Parking slot {slot.object_id} "
        "successfully reserved."
    )

    return result


# =====================================
# RELEASE PARKING SLOT
# =====================================

def release_parking_slot(
    scene,
    slot_id
):

    slot = scene.get_object_by_id(
        slot_id,
        "parking_slot"
    )

    if slot is None:
        return False

    if slot.get_parking_status() != "reserved":
        return False

    slot.set_parking_status("available")

    scene.layoutChanged.emit()

    return True
