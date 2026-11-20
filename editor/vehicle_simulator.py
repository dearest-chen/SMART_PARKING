
import math

from PySide6.QtCore import (
    QObject,
    QTimer,
    QElapsedTimer,
    QPointF,
    QRectF,
    Qt
)

from PySide6.QtGui import (
    QColor,
    QPen,
    QPainter
)

from PySide6.QtWidgets import (
    QGraphicsObject,
    QGraphicsEllipseItem,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QSpinBox,
    QMessageBox
)


# =====================================
# VEHICLE GRAPHICS
# =====================================

class VehicleSimulationItem(QGraphicsObject):

    def __init__(self, vehicle_id):

        super().__init__()

        self.vehicle_id = vehicle_id

        self.setZValue(80)

        self.setAcceptedMouseButtons(
            Qt.MouseButton.NoButton
        )

    def boundingRect(self):

        return QRectF(-32, -20, 64, 40)

    def paint(self, painter, option, widget=None):

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        # WHEELS

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#0F172A"))

        for x in [-17, 9]:

            painter.drawRoundedRect(
                QRectF(x, -16, 10, 5), 2, 2
            )

            painter.drawRoundedRect(
                QRectF(x, 11, 10, 5), 2, 2
            )

        # CAR BODY

        painter.setPen(
            QPen(QColor("#1E3A8A"), 1.5)
        )

        painter.setBrush(
            QColor("#2563EB")
        )

        painter.drawRoundedRect(
            QRectF(-25, -13, 50, 26),
            8, 8
        )

        # WINDOWS

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(
            QColor("#BFDBFE")
        )

        painter.drawRoundedRect(
            QRectF(-9, -9, 18, 18),
            4, 4
        )

        painter.setBrush(
            QColor("#93C5FD")
        )

        painter.drawRoundedRect(
            QRectF(11, -8, 8, 16),
            3, 3
        )

        # HEADLIGHTS

        painter.setBrush(
            QColor("#FEF08A")
        )

        painter.drawRoundedRect(
            QRectF(22, -9, 4, 6), 1, 1
        )

        painter.drawRoundedRect(
            QRectF(22, 3, 4, 6), 1, 1
        )

        painter.restore()


# =====================================
# PEDESTRIAN GRAPHICS
# =====================================

class PedestrianMarkerItem(QGraphicsEllipseItem):

    def __init__(self):

        super().__init__(
            -7, -7, 14, 14
        )

        self.setPen(
            QPen(
                QColor("#FFFFFF"),
                2
            )
        )

        self.setBrush(
            QColor("#DC2626")
        )

        self.setZValue(90)

        self.setAcceptedMouseButtons(
            Qt.MouseButton.NoButton
        )

        self.setToolTip(
            "Pedestrian"
        )


# =====================================
# MULTI-AGENT SIMULATION CONTROLLER
# =====================================

class VehicleSimulationController(QObject):

    def __init__(self, scene, parent=None):

        super().__init__(parent)

        self.scene = scene

        self.vehicle_speed = 90.0
        self.pedestrian_speed = 55.0

        self.agents = []

        self.vehicle_counter = 0

        self.timer = QTimer(self)

        self.timer.setInterval(16)

        self.timer.timeout.connect(
            self.advance
        )

        self.clock = QElapsedTimer()

        self._stats_refresh_elapsed_ms = 0

        # CALLBACKS

        self.on_vehicle_arrived = None
        self.on_pedestrian_arrived = None
        self.on_changed = None

    # =================================
    # CAR COUNT
    # =================================

    @property
    def car_count(self):

        return sum(
            1 for agent in self.agents
            if agent["car"].scene() is self.scene
        )

    # =================================
    # RUNNING STATUS
    # =================================

    @property
    def is_running(self):

        return any(
            agent["phase"] in ("vehicle", "pedestrian")
            for agent in self.agents
        )

    # =================================
    # SET SPEED
    # =================================

    def set_speed(self, speed):

        self.vehicle_speed = max(
            10.0,
            float(speed)
        )

    # =================================
    # BUILD ROUTE POINTS
    # =================================

    def build_route_points(
        self,
        origin,
        node_ids,
        destination,
        route_name
    ):

        points = []

        self.append_point(
            points,
            origin
        )

        for node_id in node_ids:

            node = self.scene.get_node_by_id(
                node_id
            )

            if node is None:

                raise ValueError(
                    f"{route_name}: Node {node_id} not found."
                )

            self.append_point(
                points,
                node.scenePos()
            )

        self.append_point(
            points,
            destination
        )

        return points

    # =================================
    # REMOVE DUPLICATE POINTS
    # =================================

    @staticmethod
    def append_point(points, point):

        point = QPointF(point)

        if not points:

            points.append(point)

            return

        previous = points[-1]

        distance = math.hypot(
            point.x() - previous.x(),
            point.y() - previous.y()
        )

        if distance > 0.5:

            points.append(point)

    # =================================
    # START ONE NEW CAR
    # =================================

    def start_assignment(
        self,
        result,
        gate,
        slot,
        building
    ):

        if slot.get_parking_status() != "reserved":

            raise ValueError(
                "Parking slot must be RESERVED before starting."
            )

        vehicle_path = result.get(
            "vehicle_path", []
        )

        pedestrian_path = result.get(
            "pedestrian_path", []
        )

        if not vehicle_path:

            raise ValueError(
                "Vehicle route is empty."
            )

        if not pedestrian_path:

            raise ValueError(
                "Pedestrian route is empty."
            )

        # VEHICLE ROUTE:
        # GATE -> VEHICLE NODES -> PARKING SLOT

        vehicle_points = self.build_route_points(
            gate.scenePos(),
            vehicle_path,
            slot.scenePos(),
            "Vehicle route"
        )

        # PEDESTRIAN ROUTE:
        # PARKING SLOT -> PEDESTRIAN NODES -> BUILDING

        pedestrian_points = self.build_route_points(
            slot.scenePos(),
            pedestrian_path,
            building.scenePos(),
            "Pedestrian route"
        )

        # CREATE VEHICLE ID

        self.vehicle_counter += 1

        vehicle_id = (
            f"CAR-SIM-{self.vehicle_counter:03d}"
        )

        car = VehicleSimulationItem(
            vehicle_id
        )

        car.setPos(
            vehicle_points[0]
        )

        self.scene.addItem(car)

        # CREATE AGENT RECORD

        agent = {

            "id": vehicle_id,

            "slot": slot,

            "building_id": building.object_id,

            "gate_id": gate.object_id,

            "car": car,

            "pedestrian": None,

            "vehicle_points": vehicle_points,

            "pedestrian_points": pedestrian_points,

            "vehicle_index": 0,

            "vehicle_progress": 0.0,

            "vehicle_distance_travelled_px": 0.0,

            "pedestrian_index": 0,

            "pedestrian_progress": 0.0,

            "phase": "vehicle"

        }

        self.agents.append(agent)

        # START TIMER IF NEEDED

        if not self.timer.isActive():

            self.clock.start()

            self.timer.start()

        self.notify_changed()

        return agent

    # =================================
    # MOVE ALONG A POLYLINE
    # =================================

    def advance_route(
        self,
        actor,
        points,
        agent,
        phase,
        speed,
        delta_time
    ):

        index_key = f"{phase}_index"

        progress_key = f"{phase}_progress"

        if len(points) == 1:

            actor.setPos(points[0])

            return True

        index = agent[index_key]

        progress = agent[progress_key]

        distance_budget = max(
            0.0,
            float(speed) * float(delta_time)
        )

        remaining = distance_budget

        while index < len(points) - 1:

            start = points[index]

            end = points[index + 1]

            segment_length = math.hypot(
                end.x() - start.x(),
                end.y() - start.y()
            )

            if segment_length < 0.001:

                index += 1

                progress = 0.0

                continue

            distance_left = (
                segment_length - progress
            )

            if remaining >= distance_left:

                remaining -= distance_left

                index += 1

                progress = 0.0

                if index >= len(points) - 1:

                    actor.setPos(
                        points[-1]
                    )

                    agent[index_key] = index

                    agent[progress_key] = progress

                    self.record_vehicle_distance(
                        agent,
                        phase,
                        distance_budget,
                        remaining
                    )

                    return True

            else:

                progress += remaining

                remaining = 0.0

                break

        if index >= len(points) - 1:

            actor.setPos(
                points[-1]
            )

            self.record_vehicle_distance(
                agent,
                phase,
                distance_budget,
                remaining
            )

            return True

        start = points[index]

        end = points[index + 1]

        segment_length = math.hypot(
            end.x() - start.x(),
            end.y() - start.y()
        )

        if segment_length < 0.001:

            return False

        ratio = (
            progress / segment_length
        )

        x = (
            start.x()
            + (end.x() - start.x()) * ratio
        )

        y = (
            start.y()
            + (end.y() - start.y()) * ratio
        )

        actor.setPos(
            QPointF(x, y)
        )

        # ROTATE CAR TO FOLLOW ROAD

        if isinstance(actor, VehicleSimulationItem):

            angle = math.degrees(
                math.atan2(
                    end.y() - start.y(),
                    end.x() - start.x()
                )
            )

            actor.setRotation(angle)

        agent[index_key] = index

        agent[progress_key] = progress

        self.record_vehicle_distance(
            agent,
            phase,
            distance_budget,
            remaining
        )

        return False

    # =================================
    # RECORD ACTUAL VEHICLE DISTANCE
    # =================================

    @staticmethod
    def record_vehicle_distance(
        agent,
        phase,
        distance_budget,
        remaining
    ):

        if phase != "vehicle":
            return

        travelled = max(
            0.0,
            distance_budget - remaining
        )

        agent["vehicle_distance_travelled_px"] = (
            agent.get("vehicle_distance_travelled_px", 0.0)
            + travelled
        )

    # =================================
    # MAIN ANIMATION LOOP
    # =================================

    def advance(self):

        if not self.timer.isActive():

            return

        elapsed = self.clock.restart()

        delta_time = min(
            elapsed / 1000.0,
            0.05
        )

        for agent in list(self.agents):

            # VEHICLE PHASE

            if agent["phase"] == "vehicle":

                finished = self.advance_route(
                    agent["car"],
                    agent["vehicle_points"],
                    agent,
                    "vehicle",
                    self.vehicle_speed,
                    delta_time
                )

                if finished:

                    self.vehicle_arrived(agent)

            # PEDESTRIAN PHASE

            elif agent["phase"] == "pedestrian":

                finished = self.advance_route(
                    agent["pedestrian"],
                    agent["pedestrian_points"],
                    agent,
                    "pedestrian",
                    self.pedestrian_speed,
                    delta_time
                )

                if finished:

                    self.pedestrian_arrived(agent)

        # STOP TIMER WHEN ALL AGENTS FINISH

        if not self.is_running:

            self.timer.stop()

        else:

            self._stats_refresh_elapsed_ms += elapsed

            # Refresh the dashboard about 10 times per second
            # while a vehicle or pedestrian is moving.
            if self._stats_refresh_elapsed_ms >= 100:

                self._stats_refresh_elapsed_ms = 0

                self.notify_changed()

        self.scene.update()

    # =================================
    # VEHICLE ARRIVAL
    # =================================

    def vehicle_arrived(self, agent):

        slot = agent["slot"]

        # OCCUPY PARKING SLOT

        if slot.scene() is self.scene:

            slot.set_parking_status(
                "occupied"
            )

        # CREATE PEDESTRIAN MARKER

        pedestrian = PedestrianMarkerItem()

        self.scene.addItem(
            pedestrian
        )

        pedestrian.setPos(
            agent["pedestrian_points"][0]
        )

        agent["pedestrian"] = pedestrian

        agent["phase"] = "pedestrian"

        agent["pedestrian_index"] = 0

        agent["pedestrian_progress"] = 0.0

        self.scene.update()

        if self.on_vehicle_arrived:

            self.on_vehicle_arrived(agent)

        # HANDLE ZERO-DISTANCE WALKING ROUTE

        if len(agent["pedestrian_points"]) == 1:

            self.pedestrian_arrived(agent)

        self.notify_changed()

    # =================================
    # PEDESTRIAN ARRIVAL
    # =================================

    def pedestrian_arrived(self, agent):

        agent["phase"] = "done"

        # KEEP RED DOT AT BUILDING

        self.scene.update()

        if self.on_pedestrian_arrived:

            self.on_pedestrian_arrived(agent)

        self.notify_changed()

    # =================================
    # RESET ALL SIMULATED CARS
    # =================================

    def reset_all(self):

        self.timer.stop()

        removed_count = len(self.agents)

        for agent in self.agents:

            slot = agent["slot"]

            # RELEASE ASSOCIATED PARKING SLOT

            if slot.scene() is self.scene:

                if slot.get_parking_status() in (
                    "reserved",
                    "occupied"
                ):

                    slot.set_parking_status(
                        "available"
                    )

            # REMOVE CAR

            car = agent["car"]

            if car.scene() is self.scene:

                self.scene.removeItem(car)

            # REMOVE PEDESTRIAN

            pedestrian = agent["pedestrian"]

            if (
                pedestrian is not None
                and pedestrian.scene() is self.scene
            ):

                self.scene.removeItem(
                    pedestrian
                )

        self.agents.clear()

        self.scene.update()

        self.notify_changed()

        return removed_count

    # =================================
    # NOTIFY UI
    # =================================

    def notify_changed(self):

        if self.on_changed:

            self.on_changed()


# =====================================
# INSTALL SIMULATION UI
# =====================================

def install_vehicle_simulation(main_window):

    scene = main_window.scene

    controller = VehicleSimulationController(
        scene,
        main_window
    )

    main_window.vehicle_simulator = controller

    main_window.last_assignment_result = None

    # =================================
    # SIMULATION CONTROLS
    # =================================

    controls = QHBoxLayout()

    controls.setSpacing(8)

    controls.addWidget(
        QLabel("CAR + PEDESTRIAN:")
    )

    controls.addWidget(
        QLabel("Car Speed:")
    )

    speed_spin = QSpinBox()

    speed_spin.setRange(30, 300)

    speed_spin.setValue(90)

    speed_spin.setSuffix(" px/s")

    speed_spin.setFixedWidth(95)

    controls.addWidget(speed_spin)

    start_button = QPushButton(
        "Start Next Car"
    )

    start_button.setObjectName(
        "runButton"
    )

    reset_button = QPushButton(
        "Reset All Cars"
    )

    reset_button.setObjectName(
        "actionButton"
    )

    controls.addWidget(start_button)

    controls.addWidget(reset_button)

    status_label = QLabel(
        "Waiting for parking assignment."
    )

    status_label.setStyleSheet(
        "color: #64748B;"
    )

    controls.addWidget(
        status_label,
        1
    )

    main_window.canvas_panel.layout().insertLayout(
        3,
        controls
    )

    # STORE WIDGET REFERENCES

    main_window.start_vehicle_button = start_button

    main_window.reset_all_cars_button = reset_button

    main_window.vehicle_speed_spin = speed_spin

    main_window.vehicle_status_label = status_label

    start_button.setEnabled(False)

    reset_button.setEnabled(False)

    # =================================
    # UPDATE STATISTICS
    # =================================

    def refresh_stats():

        main_window.update_stats()

        reset_button.setEnabled(
            controller.car_count > 0
            or main_window.last_assignment_result is not None
        )

    controller.on_changed = refresh_stats

    # =================================
    # INVALIDATE PENDING ASSIGNMENT
    # DOES NOT TOUCH EXISTING CARS
    # =================================

    def invalidate_pending_assignment(*args):

        result = main_window.last_assignment_result

        if result is None:

            return

        slot = result.get("slot")

        if (
            slot is not None
            and slot.scene() is scene
            and slot.get_parking_status() == "reserved"
        ):

            slot.set_parking_status(
                "available"
            )

        main_window.last_assignment_result = None

        start_button.setEnabled(False)

        refresh_stats()

    # =================================
    # START NEXT CAR
    # =================================

    def start_next_car():

        result = main_window.last_assignment_result

        if result is None:

            QMessageBox.warning(
                main_window,
                "No Assignment",
                "Klik Find & Reserve Slot terlebih dahulu."
            )

            return

        gate = scene.get_object_by_id(
            result["gate_id"],
            "gate"
        )

        slot = result.get("slot")

        if slot is None or slot.scene() is not scene:

            slot = scene.get_object_by_id(
                result["slot_id"],
                "parking_slot"
            )

        building = scene.get_object_by_id(
            result["building_id"],
            "building"
        )

        if gate is None or slot is None or building is None:

            QMessageBox.warning(
                main_window,
                "Invalid Assignment",
                "Gate, parking slot, or building not found."
            )

            return

        try:

            agent = controller.start_assignment(
                result,
                gate,
                slot,
                building
            )

        except Exception as error:

            QMessageBox.critical(
                main_window,
                "Simulation Error",
                str(error)
            )

            return

        # CONSUME THIS ASSIGNMENT
        # OLD CARS REMAIN IN THE SCENE

        main_window.last_assignment_result = None

        start_button.setEnabled(False)

        reset_button.setEnabled(True)

        status_label.setText(
            f"{agent['id']} is driving to {slot.object_id}..."
        )

        main_window.statusBar().showMessage(
            f"{agent['id']} started from {gate.object_id}.",
            5000
        )

        refresh_stats()

    # =================================
    # VEHICLE ARRIVED CALLBACK
    # =================================

    def on_vehicle_arrived(agent):

        status_label.setText(
            f"{agent['id']} parked at "
            f"{agent['slot'].object_id}. "
            f"Pedestrian walking to {agent['building_id']}..."
        )

        main_window.statusBar().showMessage(
            f"{agent['id']} arrived. Parking slot occupied.",
            6000
        )

        refresh_stats()

    # =================================
    # PEDESTRIAN ARRIVED CALLBACK
    # =================================

    def on_pedestrian_arrived(agent):

        status_label.setText(
            f"{agent['id']}: pedestrian arrived at "
            f"{agent['building_id']}."
        )

        main_window.statusBar().showMessage(
            f"Pedestrian from {agent['slot'].object_id} "
            f"arrived at {agent['building_id']}.",
            6000
        )

    controller.on_vehicle_arrived = on_vehicle_arrived

    controller.on_pedestrian_arrived = on_pedestrian_arrived

    # =================================
    # RESET ALL
    # =================================

    def reset_all_cars():

        pending = main_window.last_assignment_result

        # RELEASE PENDING RESERVATION

        if pending:

            pending_slot = pending.get("slot")

            if (
                pending_slot is not None
                and pending_slot.scene() is scene
                and pending_slot.get_parking_status() == "reserved"
            ):

                pending_slot.set_parking_status(
                    "available"
                )

        main_window.last_assignment_result = None

        # REMOVE ALL SIMULATED AGENTS

        removed = controller.reset_all()

        start_button.setEnabled(False)

        reset_button.setEnabled(False)

        status_label.setText(
            "All simulated cars and pedestrians reset."
        )

        main_window.statusBar().showMessage(
            f"Reset complete. {removed} simulated car(s) removed.",
            6000
        )

        refresh_stats()

    # =================================
    # MODE SYNCHRONIZATION
    # =================================

    def sync_mode():

        is_simulation = (
            main_window.current_mode == "simulation"
        )

        start_button.setEnabled(
            is_simulation
            and main_window.last_assignment_result is not None
        )

        reset_button.setEnabled(
            controller.car_count > 0
            or main_window.last_assignment_result is not None
        )

    # =================================
    # SIGNAL CONNECTIONS
    # =================================

    speed_spin.valueChanged.connect(
        controller.set_speed
    )

    start_button.clicked.connect(
        start_next_car
    )

    reset_button.clicked.connect(
        reset_all_cars
    )

    # A NEW MAP EDIT INVALIDATES ONLY
    # THE PENDING ASSIGNMENT.
    # COMPLETED/RUNNING CARS ARE PRESERVED.

    scene.layoutChanged.connect(
        invalidate_pending_assignment
    )

    main_window.assignment_building_combo.currentIndexChanged.connect(
        invalidate_pending_assignment
    )

    main_window.assignment_gate_combo.currentIndexChanged.connect(
        invalidate_pending_assignment
    )

    main_window.design_button.clicked.connect(
        sync_mode
    )

    main_window.simulation_button.clicked.connect(
        sync_mode
    )
