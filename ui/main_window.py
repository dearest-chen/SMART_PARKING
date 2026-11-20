
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QFileDialog,
    QMessageBox
)

from editor.map_scene import MapScene
from editor.map_view import MapView
from editor.map_items import ParkingObjectItem

from editor.graph_items import (
    GraphNodeItem,
    GraphEdgeItem,
    RoadSegmentItem
)

from editor.layout_manager import (
    save_layout,
    load_layout
)

from editor.graph_algorithms import (
    dijkstra,
    reconstruct_shortest_path,
    get_shortest_path_tree_edges
)

from editor.route_visualizer import (
    draw_shortest_path_tree,
    draw_dijkstra_progress,
    draw_parking_assignment_routes,
    clear_route_visualization as clear_route_overlay
)

from editor.parking_assignment import (
    assign_parking_slot,
    release_parking_slot
)

from editor.vehicle_simulator import (
    install_vehicle_simulation
)

from ui.panels import ToolButton


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Smart Parking Simulator"
        )

        self.resize(1500, 900)
        self.setMinimumSize(1150, 760)

        self.scene = MapScene(self)

        self.tool_buttons = {}

        self.current_mode = "design"

        # Dijkstra exploration animation (reuses the existing Run Dijkstra button).
        self._dijkstra_animation = None
        self._dijkstra_animation_token = 0
        self._dijkstra_timer = QTimer(self)
        self._dijkstra_timer.setInterval(140)
        self._dijkstra_timer.timeout.connect(
            self._advance_dijkstra_animation
        )

        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI';
                font-size: 10pt;
                color: #1E293B;
            }

            QMainWindow {
                background: #F1F5F9;
            }

            QFrame#header,
            QFrame#sidePanel,
            QFrame#canvasPanel {
                background: white;
                border: 1px solid #DCE3EC;
                border-radius: 12px;
            }

            QLabel#pageTitle {
                font-size: 19pt;
                font-weight: bold;
                color: #0F172A;
            }

            QLabel#sectionTitle {
                font-size: 11pt;
                font-weight: bold;
                color: #1E293B;
            }

            QPushButton#modeButton {
                background: #F8FAFC;
                border: 1px solid #DCE3EC;
                border-radius: 8px;
                padding: 9px 14px;
            }

            QPushButton#modeButton:checked {
                background: #2563EB;
                color: white;
                border-color: #2563EB;
            }

            QPushButton#toolButton {
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 8px;
                padding: 9px;
                text-align: left;
            }

            QPushButton#toolButton:hover {
                background: #EFF6FF;
                border-color: #93C5FD;
            }

            QPushButton#toolButton:checked {
                background: #DBEAFE;
                border: 1px solid #2563EB;
                color: #1D4ED8;
                font-weight: bold;
            }

            QPushButton#actionButton {
                background: #F8FAFC;
                border: 1px solid #DCE3EC;
                border-radius: 6px;
                padding: 6px 10px;
            }

            QPushButton#runButton {
                background: #2563EB;
                color: white;
                border: 1px solid #2563EB;
                border-radius: 6px;
                padding: 7px 12px;
                font-weight: bold;
            }

            QPushButton#runButton:hover {
                background: #1D4ED8;
            }

            QPushButton#deleteButton {
                background: #FEE2E2;
                color: #B91C1C;
                border: 1px solid #FECACA;
                border-radius: 7px;
                padding: 9px;
            }

            QSpinBox,
            QComboBox {
                background: #F8FAFC;
                border: 1px solid #DCE3EC;
                border-radius: 6px;
                padding: 5px;
                min-height: 22px;
            }

            QGraphicsView#mapView {
                background: #F8FAFC;
                border: 1px solid #DCE3EC;
                border-radius: 10px;
            }

            QLabel#hint {
                color: #64748B;
                font-size: 9pt;
            }

            QLabel#routeResult {
                color: #1E293B;
                font-weight: bold;
                padding: 5px;
            }

            QStatusBar {
                background: white;
                color: #64748B;
                border-top: 1px solid #DCE3EC;
            }
        """)

        self.build_ui()

        install_vehicle_simulation(self)

        self.scene.selectionChanged.connect(
            self.update_properties
        )

        self.scene.layoutChanged.connect(
            self.update_stats
        )

        self.scene.layoutChanged.connect(
            self.update_properties
        )

        self.scene.layoutChanged.connect(
            self.clear_route_visualization
        )

        self.scene.layoutChanged.connect(
            self.refresh_node_selectors
        )

        self.scene.layoutChanged.connect(
            self.refresh_assignment_selectors
        )

        self.update_stats()
        self.refresh_node_selectors()
        self.refresh_assignment_selectors()

        self.set_mode("design")

    # =====================================
    # BUILD UI
    # =====================================

    def build_ui(self):

        central = QWidget()

        root = QVBoxLayout(central)

        root.setContentsMargins(
            16, 8, 16, 8
        )

        root.setSpacing(8)

        root.addWidget(
            self.create_header()
        )

        content = QHBoxLayout()
        content.setSpacing(12)

        self.left_panel = self.create_tools_panel()
        self.canvas_panel = self.create_canvas_panel()
        self.right_panel = self.create_properties_panel()

        content.addWidget(self.left_panel)

        content.addWidget(
            self.canvas_panel,
            1
        )

        content.addWidget(self.right_panel)

        root.addLayout(content, 1)

        self.setCentralWidget(central)

        self.statusBar().showMessage(
            "Smart Parking Simulator | Ready"
        )

    # =====================================
    # HEADER
    # =====================================

    def create_header(self):

        header = QFrame()

        header.setObjectName("header")
        header.setFixedHeight(64)

        layout = QHBoxLayout(header)

        layout.setContentsMargins(
            18, 6, 18, 6
        )

        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)
        title_layout.setAlignment(
            Qt.AlignmentFlag.AlignVCenter
        )

        title = QLabel(
            "Smart Parking Simulator"
        )

        title.setObjectName("pageTitle")

        title_layout.addWidget(title)
        layout.addLayout(title_layout)

        layout.addStretch()

        # SAVE / LOAD

        self.save_button = QPushButton(
            "Save Layout"
        )

        self.load_button = QPushButton(
            "Load Layout"
        )

        for button in [
            self.save_button,
            self.load_button
        ]:

            button.setObjectName("actionButton")
            button.setMinimumHeight(34)

        self.save_button.clicked.connect(
            self.save_layout_dialog
        )

        self.load_button.clicked.connect(
            self.load_layout_dialog
        )

        layout.addWidget(self.save_button)
        layout.addWidget(self.load_button)

        # MODE BUTTONS

        self.design_button = QPushButton(
            "Design Mode"
        )

        self.simulation_button = QPushButton(
            "Simulation Mode"
        )

        for button in [
            self.design_button,
            self.simulation_button
        ]:

            button.setObjectName("modeButton")
            button.setCheckable(True)
            button.setMinimumHeight(34)

        self.mode_group = QButtonGroup(self)

        self.mode_group.setExclusive(True)

        self.mode_group.addButton(
            self.design_button
        )

        self.mode_group.addButton(
            self.simulation_button
        )

        self.design_button.clicked.connect(
            lambda checked=False:
            self.set_mode("design")
        )

        self.simulation_button.clicked.connect(
            lambda checked=False:
            self.set_mode("simulation")
        )

        layout.addWidget(self.design_button)
        layout.addWidget(self.simulation_button)

        return header

    # =====================================
    # LEFT TOOLBOX
    # =====================================

    def create_tools_panel(self):

        panel = QFrame()

        panel.setObjectName("sidePanel")
        panel.setFixedWidth(225)

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            14, 16, 14, 14
        )

        layout.setSpacing(8)

        title = QLabel("MAP OBJECTS")
        title.setObjectName("sectionTitle")

        layout.addWidget(title)

        self.tool_group = QButtonGroup(self)

        self.tool_group.setExclusive(True)

        tools = [
            ("Select / Move", "select"),
            ("Parking Slot", "parking_slot"),
            ("Building", "building"),
            ("Entrance Gate", "gate"),
            ("Car Placeholder", "car"),
            ("Add Graph Node", "add_node"),
            ("Draw Vehicle Road", "draw_road"),
            ("Connect Vehicle Nodes", "connect_nodes"),
            ("Draw Pedestrian Path", "pedestrian_path"),
            ("Connect Pedestrian Nodes", "connect_pedestrian"),
        ]

        for text, tool_key in tools:

            button = ToolButton(
                text,
                tool_key
            )

            button.setObjectName("toolButton")
            button.setCheckable(True)
            button.setMinimumHeight(36)

            button.clicked.connect(
                lambda checked=False, key=tool_key:
                self.select_tool(key)
            )

            self.tool_group.addButton(button)

            self.tool_buttons[tool_key] = button

            layout.addWidget(button)

        layout.addStretch()

        note = QLabel(
            "Road: click and drag.\n"
            "Node: click canvas.\n"
            "Connect: click two nodes.\n"
            "Select: move objects."
        )

        note.setObjectName("hint")
        note.setWordWrap(True)

        layout.addWidget(note)

        return panel

    # =====================================
    # CENTER CANVAS
    # =====================================

    def create_canvas_panel(self):

        panel = QFrame()

        panel.setObjectName("canvasPanel")

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            14, 14, 14, 12
        )

        layout.setSpacing(10)

        # CANVAS TOOLBAR

        toolbar = QHBoxLayout()

        self.canvas_heading = QLabel(
            "DESIGN MODE - PARKING MAP"
        )

        self.canvas_heading.setObjectName(
            "sectionTitle"
        )

        toolbar.addWidget(
            self.canvas_heading
        )

        toolbar.addStretch()

        self.grid_checkbox = QCheckBox(
            "Show Grid"
        )

        self.grid_checkbox.setChecked(True)

        self.grid_checkbox.toggled.connect(
            self.scene.set_grid_visible
        )

        toolbar.addWidget(
            self.grid_checkbox
        )

        toolbar.addWidget(
            QLabel("Road Width:")
        )

        self.road_width_spin = QSpinBox()

        self.road_width_spin.setRange(30, 140)
        self.road_width_spin.setValue(70)
        self.road_width_spin.setSuffix(" px")
        self.road_width_spin.setFixedWidth(90)

        toolbar.addWidget(
            self.road_width_spin
        )

        zoom_in_button = QPushButton("Zoom +")
        zoom_out_button = QPushButton("Zoom -")
        fit_button = QPushButton("Fit")

        for button in [
            zoom_in_button,
            zoom_out_button,
            fit_button
        ]:

            button.setObjectName("actionButton")

            toolbar.addWidget(button)

        layout.addLayout(toolbar)

        # MAP VIEW

        self.view = MapView(
            self.scene
        )

        self.view.objectAdded.connect(
            self.on_object_added
        )

        self.view.message.connect(
            self.show_status_message
        )

        self.road_width_spin.valueChanged.connect(
            self.view.set_road_width
        )

        zoom_in_button.clicked.connect(
            self.view.zoom_in
        )

        zoom_out_button.clicked.connect(
            self.view.zoom_out
        )

        fit_button.clicked.connect(
            self.view.fit_to_scene
        )

        # =================================
        # DIJKSTRA CONTROLS
        # =================================

        route_controls = QHBoxLayout()

        route_controls.addWidget(
            QLabel("Network:")
        )

        self.route_mode_combo = QComboBox()

        self.route_mode_combo.addItem(
            "Vehicle",
            "vehicle"
        )

        self.route_mode_combo.addItem(
            "Pedestrian",
            "pedestrian"
        )

        self.route_mode_combo.setFixedWidth(115)

        route_controls.addWidget(
            self.route_mode_combo
        )

        route_controls.addWidget(
            QLabel("Start:")
        )

        self.start_node_combo = QComboBox()

        self.start_node_combo.setMinimumWidth(105)

        route_controls.addWidget(
            self.start_node_combo,
            1
        )

        route_controls.addWidget(
            QLabel("Destination:")
        )

        self.target_node_combo = QComboBox()

        self.target_node_combo.setMinimumWidth(105)

        route_controls.addWidget(
            self.target_node_combo,
            1
        )

        self.run_dijkstra_button = QPushButton(
            "Run Dijkstra"
        )

        self.run_dijkstra_button.setObjectName(
            "runButton"
        )

        self.clear_route_button = QPushButton(
            "Clear Path"
        )

        self.clear_route_button.setObjectName(
            "actionButton"
        )

        route_controls.addWidget(
            self.run_dijkstra_button
        )

        route_controls.addWidget(
            self.clear_route_button
        )

        layout.addLayout(route_controls)

        # =================================
        # PARKING ASSIGNMENT CONTROLS
        # =================================

        assignment_controls = QHBoxLayout()

        assignment_controls.addWidget(
            QLabel("Destination Building:")
        )

        self.assignment_building_combo = QComboBox()
        self.assignment_building_combo.setMinimumWidth(125)

        assignment_controls.addWidget(
            self.assignment_building_combo,
            1
        )

        assignment_controls.addWidget(
            QLabel("Entry Gate:")
        )

        self.assignment_gate_combo = QComboBox()
        self.assignment_gate_combo.setMinimumWidth(115)

        assignment_controls.addWidget(
            self.assignment_gate_combo,
            1
        )

        self.assign_parking_button = QPushButton(
            "Find & Reserve Slot"
        )

        self.assign_parking_button.setObjectName(
            "runButton"
        )

        assignment_controls.addWidget(
            self.assign_parking_button
        )

        layout.addLayout(assignment_controls)

        # ROUTE RESULT

        self.route_result_label = QLabel(
            "No route calculated."
        )

        self.route_result_label.setObjectName(
            "routeResult"
        )

        self.route_result_label.setWordWrap(True)

        self.assignment_result_label = QLabel(
            "Choose a building and entry gate to assign one vehicle."
        )

        self.assignment_result_label.setObjectName(
            "routeResult"
        )

        self.assignment_result_label.setWordWrap(True)

        # ROUTE SIGNALS

        self.run_dijkstra_button.clicked.connect(
            self.run_dijkstra
        )

        self.assign_parking_button.clicked.connect(
            self.run_parking_assignment
        )

        self.assignment_building_combo.currentIndexChanged.connect(
            lambda index:
            self.clear_route_visualization()
        )

        self.assignment_gate_combo.currentIndexChanged.connect(
            lambda index:
            self.clear_route_visualization()
        )

        self.clear_route_button.clicked.connect(
            self.clear_route_visualization
        )

        self.route_mode_combo.currentIndexChanged.connect(
            lambda index:
            self.clear_route_visualization()
        )

        self.start_node_combo.currentIndexChanged.connect(
            lambda index:
            self.clear_route_visualization()
        )

        self.target_node_combo.currentIndexChanged.connect(
            lambda index:
            self.clear_route_visualization()
        )

        # ADD CANVAS

        layout.addWidget(
            self.view,
            1
        )

        layout.addWidget(
            self.route_result_label
        )

        layout.addWidget(
            self.assignment_result_label
        )

        self.mode_notice = QLabel(
            "Create your parking map using the tools."
        )

        self.mode_notice.setObjectName("hint")
        self.mode_notice.setWordWrap(True)

        layout.addWidget(
            self.mode_notice
        )

        return panel

    # =====================================
    # RIGHT PROPERTIES PANEL
    # =====================================

    def create_properties_panel(self):

        panel = QFrame()

        panel.setObjectName("sidePanel")
        panel.setFixedWidth(250)

        layout = QVBoxLayout(panel)

        layout.setContentsMargins(
            14, 16, 14, 14
        )

        layout.setSpacing(10)

        title = QLabel("PROPERTIES")
        title.setObjectName("sectionTitle")

        layout.addWidget(title)

        self.properties_info = QLabel(
            "No object selected."
        )

        self.properties_info.setWordWrap(True)

        self.properties_info.setStyleSheet(
            "color: #64748B;"
        )

        layout.addWidget(
            self.properties_info
        )

        delete_button = QPushButton(
            "Delete Selected Object"
        )

        delete_button.setObjectName(
            "deleteButton"
        )

        delete_button.clicked.connect(
            self.view_delete_selected
        )

        layout.addWidget(delete_button)

        separator = QFrame()

        separator.setFrameShape(
            QFrame.Shape.HLine
        )

        layout.addWidget(separator)

        info_title = QLabel(
            "MAP INFORMATION"
        )

        info_title.setObjectName("sectionTitle")

        layout.addWidget(info_title)

        self.total_info = QLabel()
        self.slot_info = QLabel()
        self.parking_status_info = QLabel()
        self.parking_utilization_info = QLabel()

        self.building_info = QLabel()
        self.gate_info = QLabel()
        self.car_info = QLabel()

        self.road_info = QLabel()
        self.pedestrian_info = QLabel()

        self.node_info = QLabel()
        self.vehicle_edge_info = QLabel()
        self.pedestrian_edge_info = QLabel()

        map_stat_labels = [
            self.total_info,
            self.slot_info,
            self.parking_status_info,
            self.parking_utilization_info,
            self.building_info,
            self.gate_info,
            self.car_info,
            self.road_info,
            self.pedestrian_info,
            self.node_info,
            self.vehicle_edge_info,
            self.pedestrian_edge_info
        ]

        for label in map_stat_labels:

            label.setWordWrap(True)
            label.setStyleSheet(
                "color: #475569; font-size: 9pt;"
            )

            layout.addWidget(label)

        simulation_separator = QFrame()
        simulation_separator.setFrameShape(
            QFrame.Shape.HLine
        )

        layout.addWidget(simulation_separator)

        simulation_title = QLabel(
            "SIMULATION STATISTICS"
        )

        simulation_title.setObjectName("sectionTitle")

        layout.addWidget(simulation_title)

        self.simulated_car_info = QLabel()
        self.vehicle_distance_info = QLabel()

        for label in [
            self.simulated_car_info,
            self.vehicle_distance_info
        ]:

            label.setWordWrap(True)
            label.setStyleSheet(
                "color: #475569; font-size: 9pt;"
            )

            layout.addWidget(label)

        layout.addStretch()

        return panel

    # =====================================
    # TOOL SELECTION
    # =====================================

    def select_tool(self, tool):

        self.view.set_tool(tool)

        if tool in self.tool_buttons:

            self.tool_buttons[tool].setChecked(True)

        self.statusBar().showMessage(
            f"Active Tool: {tool.replace('_', ' ').title()}"
        )

    # =====================================
    # MODE MANAGEMENT
    # =====================================

    def set_mode(self, mode):

        self.current_mode = mode

        if mode == "design":

            self.design_button.setChecked(True)

            self.canvas_heading.setText(
                "DESIGN MODE - PARKING MAP"
            )

            self.mode_notice.setText(
                "Design Mode: Build roads, nodes, "
                "parking slots and buildings."
            )

            self.select_tool("select")

            if hasattr(self, "assign_parking_button"):
                self.assign_parking_button.setEnabled(False)

            self.statusBar().showMessage(
                "Active Mode: Design Mode"
            )

        else:

            self.simulation_button.setChecked(True)

            self.canvas_heading.setText(
                "SIMULATION MODE - MAP PREVIEW"
            )

            self.mode_notice.setText(
                "Simulation Preview: Dijkstra route "
                "analysis is available above the canvas."
            )

            self.select_tool("select")

            if hasattr(self, "assign_parking_button"):
                self.assign_parking_button.setEnabled(
                    self.assignment_building_combo.count() > 1
                    and self.assignment_gate_combo.count() > 1
                )

            self.statusBar().showMessage(
                "Simulation Preview"
            )

    # =====================================
    # REFRESH NODE SELECTORS
    # =====================================

    def refresh_node_selectors(self):

        if not hasattr(self, "start_node_combo"):
            return

        nodes = sorted(
            self.scene.nodes,
            key=lambda node: node.node_id
        )

        for combo, placeholder in [
            (
                self.start_node_combo,
                "-- Select Start --"
            ),
            (
                self.target_node_combo,
                "-- Select Target --"
            )
        ]:

            previous_value = combo.currentData()

            combo.blockSignals(True)

            combo.clear()

            combo.addItem(
                placeholder,
                None
            )

            for node in nodes:

                combo.addItem(
                    node.node_id,
                    node.node_id
                )

            previous_index = combo.findData(
                previous_value
            )

            if previous_index >= 0:
                combo.setCurrentIndex(previous_index)
            else:
                combo.setCurrentIndex(0)

            combo.blockSignals(False)

    # =====================================
    # REFRESH PARKING ASSIGNMENT SELECTORS
    # =====================================

    def refresh_assignment_selectors(self):

        if not hasattr(self, "assignment_building_combo"):
            return

        buildings = self.scene.get_buildings()
        gates = self.scene.get_gates()

        selector_data = [
            (
                self.assignment_building_combo,
                buildings,
                "-- Select Building --"
            ),
            (
                self.assignment_gate_combo,
                gates,
                "-- Select Entry Gate --"
            )
        ]

        for combo, objects, placeholder in selector_data:

            previous_value = combo.currentData()

            combo.blockSignals(True)
            combo.clear()

            combo.addItem(
                placeholder,
                None
            )

            for item in objects:

                combo.addItem(
                    f"{item.label} ({item.object_id})",
                    item.object_id
                )

            previous_index = combo.findData(
                previous_value
            )

            if previous_index >= 0:
                combo.setCurrentIndex(previous_index)
            else:
                combo.setCurrentIndex(0)

            combo.blockSignals(False)

        self.assign_parking_button.setEnabled(
            self.current_mode == "simulation"
            and bool(buildings)
            and bool(gates)
        )

    # =====================================
    # RUN DIJKSTRA
    # =====================================

    def run_dijkstra(self):

        # Stop any previous animation and clear its overlays.
        self._stop_dijkstra_animation()
        clear_route_overlay(self.scene)

        start_id = self.start_node_combo.currentData()
        target_id = self.target_node_combo.currentData()
        mode = self.route_mode_combo.currentData()

        if not self.scene.nodes:

            QMessageBox.warning(
                self,
                "No Graph Nodes",
                "Tambahkan Graph Node terlebih dahulu."
            )

            return

        if start_id is None or target_id is None:

            QMessageBox.warning(
                self,
                "Select Nodes",
                "Pilih Start Node dan Destination Node."
            )

            return

        try:

            result = dijkstra(
                self.scene.nodes,
                self.scene.edges,
                start_id,
                mode
            )

            path = reconstruct_shortest_path(
                result,
                start_id,
                target_id
            )

            tree_edges = get_shortest_path_tree_edges(
                result
            )

            node_lookup = {
                node.node_id: node
                for node in self.scene.nodes
            }

            visited_order = list(
                result.get("visited_order", [])
            )

            self._dijkstra_animation = {
                "visited_order": visited_order,
                "index": 0,
                "previous": result["previous"],
                "tree_edges": tree_edges,
                "path_edges": path["edges"] if path else [],
                "start_node": node_lookup[start_id],
                "target_node": node_lookup[target_id],
                "start_id": start_id,
                "target_id": target_id,
                "path": path,
                "distance": (
                    result["distances"][target_id]
                    if path is not None
                    else None
                ),
                "mode": mode,
                "node_lookup": node_lookup,
            }

            if not visited_order:
                self._finish_dijkstra_animation(
                    self._dijkstra_animation_token
                )
                return

            self.route_result_label.setText(
                f"Dijkstra exploration: 0/{len(visited_order)} nodes visited"
            )

            self.statusBar().showMessage(
                f"Exploring {mode} network from {start_id}..."
            )

            self._dijkstra_timer.start()

        except Exception as error:

            self._stop_dijkstra_animation()

            QMessageBox.critical(
                self,
                "Dijkstra Error",
                str(error)
            )

    # =====================================
    # ADVANCE DIJKSTRA EXPLORATION
    # =====================================

    def _advance_dijkstra_animation(self):

        animation = self._dijkstra_animation

        if animation is None:
            self._dijkstra_timer.stop()
            return

        visited_order = animation["visited_order"]
        index = animation["index"]

        if index >= len(visited_order):
            self._dijkstra_timer.stop()
            token = self._dijkstra_animation_token

            QTimer.singleShot(
                350,
                lambda token=token:
                self._finish_dijkstra_animation(token)
            )
            return

        node_id = visited_order[index]
        node = animation["node_lookup"].get(node_id)

        if node is None:
            animation["index"] += 1
            return

        predecessor = animation["previous"].get(node_id)
        predecessor_edge = (
            predecessor[1]
            if predecessor is not None
            else None
        )

        draw_dijkstra_progress(
            self.scene,
            node,
            predecessor_edge
        )

        animation["index"] += 1

        visited_count = animation["index"]
        total_count = len(visited_order)

        self.route_result_label.setText(
            (
                f"Dijkstra exploration: {visited_count}/{total_count} nodes visited\n"
                f"Current node: {node_id}"
            )
        )

        self.statusBar().showMessage(
            f"Dijkstra visiting {node_id} ({visited_count}/{total_count})"
        )

        if visited_count >= total_count:

            self._dijkstra_timer.stop()
            token = self._dijkstra_animation_token

            QTimer.singleShot(
                350,
                lambda token=token:
                self._finish_dijkstra_animation(token)
            )

    # =====================================
    # FINISH DIJKSTRA EXPLORATION
    # =====================================

    def _finish_dijkstra_animation(self, token=None):

        if token is not None and token != self._dijkstra_animation_token:
            return

        animation = self._dijkstra_animation

        if animation is None:
            return

        self._dijkstra_timer.stop()

        draw_shortest_path_tree(
            self.scene,
            animation["tree_edges"],
            animation["path_edges"],
            animation["start_node"],
            animation["target_node"]
        )

        path = animation["path"]
        start_id = animation["start_id"]
        target_id = animation["target_id"]
        visited_count = len(animation["visited_order"])
        tree_count = len(animation["tree_edges"])

        if path is None:

            self.route_result_label.setText(
                (
                    f"No route found: {start_id} → {target_id}\n"
                    f"Reachable nodes: {visited_count} | "
                    f"Shortest Path Tree edges: {tree_count}"
                )
            )

            self.statusBar().showMessage(
                "Dijkstra selesai. Destination tidak dapat dijangkau.",
                7000
            )

        else:

            route_text = " → ".join(
                path["node_ids"]
            )

            distance = animation["distance"]

            self.route_result_label.setText(
                (
                    f"Shortest Route: {route_text}\n"
                    f"Total Distance: {distance:.2f} m | "
                    f"SPT Edges: {tree_count} | "
                    f"Visited Nodes: {visited_count}"
                )
            )

            self.statusBar().showMessage(
                f"Dijkstra completed. Distance: {distance:.2f} m",
                7000
            )

        self._dijkstra_animation = None

    # =====================================
    # STOP DIJKSTRA EXPLORATION
    # =====================================

    def _stop_dijkstra_animation(self):

        if hasattr(self, "_dijkstra_timer"):
            self._dijkstra_timer.stop()

        self._dijkstra_animation = None
        self._dijkstra_animation_token += 1

    # =====================================
    # RUN PARKING ASSIGNMENT
    # =====================================

    def run_parking_assignment(self):

        building_id = (
            self.assignment_building_combo.currentData()
        )

        gate_id = (
            self.assignment_gate_combo.currentData()
        )

        if building_id is None:

            QMessageBox.warning(
                self,
                "Select Building",
                "Pilih gedung tujuan terlebih dahulu."
            )

            return

        if gate_id is None:

            QMessageBox.warning(
                self,
                "Select Entry Gate",
                "Pilih gerbang masuk terlebih dahulu."
            )

            return

        # Stop Dijkstra animation before replacing route overlays.
        self._stop_dijkstra_animation()

        # Remove previous route overlays before calculating a new assignment.
        clear_route_overlay(self.scene)

        self.route_result_label.setText(
            "No Dijkstra route calculated."
        )

        self.assignment_result_label.setText(
            "Calculating parking assignment..."
        )

        reservation_slot_id = None

        try:

            result = assign_parking_slot(
                self.scene,
                building_id,
                gate_id
            )

          
            if not result.get("success"):

                self.assignment_result_label.setText(
                    f"Assignment failed: {result.get('message', 'Unknown error')}"
                )

                self.statusBar().showMessage(
                    "Parking assignment failed.",
                    5000
                )

                QMessageBox.warning(
                    self,
                    "Parking Assignment Failed",
                    result.get(
                        "message",
                        "Tidak ditemukan slot parkir yang sesuai."
                    )
                )

                return

            # =================================
            # VEHICLE ROUTE DEBUG
            # =================================

            print("\n========== VEHICLE ROUTE DEBUG ==========")

            print("Gate ID:", result["gate_id"])

            print("Vehicle Start Node:",
                  result["vehicle_start_node_id"])

            print("Vehicle Target Node:",
                  result["vehicle_target_node_id"])

            print("Vehicle Path:",
                  result["vehicle_path"])

            print("Vehicle Edges:",
                  [edge.edge_id for edge in result["vehicle_edges"]])

            print("Vehicle Distance:",
                  result["vehicle_distance_m"])

            print("=========================================\n")

            reservation_slot_id = result["slot_id"]

            node_lookup = {
                node.node_id: node
                for node in self.scene.nodes
            }

            required_node_ids = [
                result["vehicle_start_node_id"],
                result["vehicle_target_node_id"],
                result["pedestrian_start_node_id"],
                result["pedestrian_target_node_id"]
            ]

            missing_nodes = [
                node_id
                for node_id in required_node_ids
                if node_id not in node_lookup
            ]

            if missing_nodes:

                # Roll back the reservation if visualization cannot be built.
                release_parking_slot(
                    self.scene,
                    result["slot_id"]
                )

                reservation_slot_id = None

                raise RuntimeError(
                    "Graph node tidak ditemukan: "
                    + ", ".join(missing_nodes)
                )

            draw_parking_assignment_routes(
                self.scene,
                result["vehicle_edges"],
                result["pedestrian_edges"],
                node_lookup[result["vehicle_start_node_id"]],
                node_lookup[result["vehicle_target_node_id"]],
                node_lookup[result["pedestrian_start_node_id"]],
                node_lookup[result["pedestrian_target_node_id"]]
            )

            reservation_slot_id = None

            self.assignment_result_label.setText(
                (
                    f"Reserved Slot: {result['slot_id']} | "
                    f"Building: {result['building_id']} | "
                    f"Gate: {result['gate_id']}\n"
                    f"Vehicle Route: "
                    f"{' → '.join(result['vehicle_path'])} "
                    f"({result['vehicle_distance_m']:.2f} m)\n"
                    f"Pedestrian Route: "
                    f"{' → '.join(result['pedestrian_path'])} "
                    f"({result['walking_distance_m']:.2f} m)"
                )
            )

                        # SAVE ASSIGNMENT FOR VEHICLE SIMULATION

            self.last_assignment_result = result

            self.start_vehicle_button.setText(
                "Start Car Simulation"
            )

            self.start_vehicle_button.setEnabled(
                self.current_mode == "simulation"
            )

            self.statusBar().showMessage(
                (
                    f"{result['message']} "
                    f"Vehicle: {result['vehicle_distance_m']:.2f} m | "
                    f"Walking: {result['walking_distance_m']:.2f} m"
                ),
                9000
            )

            self.update_stats()
            self.update_properties()

            reservation_slot_id = None

        except Exception as error:

            if reservation_slot_id is not None:

                release_parking_slot(
                    self.scene,
                    reservation_slot_id
                )

            self.assignment_result_label.setText(
                f"Assignment error: {error}"
            )

            QMessageBox.critical(
                self,
                "Parking Assignment Error",
                str(error)
            )

    # =====================================
    # CLEAR ROUTE
    # =====================================

    def clear_route_visualization(self):

        self._stop_dijkstra_animation()

        clear_route_overlay(
            self.scene
        )

        if hasattr(self, "route_result_label"):

            self.route_result_label.setText(
                "No route calculated. Run Dijkstra to find a path."
            )

        if hasattr(self, "assignment_result_label"):

            self.assignment_result_label.setText(
                "Choose a building and entry gate to assign one vehicle."
            )

    # =====================================
    # OBJECT ADDED
    # =====================================

    def on_object_added(self, item):

        if item is None:
            return

        if isinstance(item, GraphNodeItem):

            name = item.node_id

        elif isinstance(item, ParkingObjectItem):

            name = item.label

        else:

            name = "Map Object"

        self.statusBar().showMessage(
            f"Added: {name}"
        )

    def show_status_message(self, message):

        self.statusBar().showMessage(
            message,
            5000
        )

    # =====================================
    # DELETE
    # =====================================

    def view_delete_selected(self):

        self.view.delete_selected()

    # =====================================
    # UPDATE PROPERTIES
    # =====================================

    def update_properties(self):

        selected = self.scene.selectedItems()

        if not selected:

            self.properties_info.setText(
                "No object selected."
            )

            return

        item = selected[0]

        if isinstance(item, ParkingObjectItem):

            extra_info = ""

            if item.object_type == "parking_slot":

                extra_info = (
                    f"\n\nStatus: "
                    f"{item.get_parking_status().title()}"
                )

            self.properties_info.setText(
                f"Type: {item.object_type.title()}\n\n"
                f"ID: {item.object_id}\n\n"
                f"X: {int(item.pos().x())}\n"
                f"Y: {int(item.pos().y())}"
                f"{extra_info}"
            )

        elif isinstance(item, GraphNodeItem):

            self.properties_info.setText(
                f"Type: Graph Node\n\n"
                f"ID: {item.node_id}\n\n"
                f"X: {int(item.pos().x())}\n"
                f"Y: {int(item.pos().y())}"
            )

        elif isinstance(item, GraphEdgeItem):

            self.properties_info.setText(
                f"Type: Graph Edge\n\n"
                f"ID: {item.edge_id}\n\n"
                f"Mode: {item.mode.title()}\n\n"
                f"Weight: {item.weight_m:.2f} m\n\n"
                f"From: {item.node_a.node_id}\n"
                f"To: {item.node_b.node_id}"
            )

        elif isinstance(item, RoadSegmentItem):

            distance = item.line().length() / 10

            self.properties_info.setText(
                f"Type: Road Segment\n\n"
                f"ID: {item.road_id}\n\n"
                f"Mode: {item.mode.title()}\n\n"
                f"Width: {item.road_width} px\n\n"
                f"Length: {distance:.2f} m"
            )

    # =====================================
    # UPDATE STATISTICS
    # =====================================

    def update_stats(self):

        # =================================
        # MAP ELEMENT STATISTICS
        # =================================

        total = (
            self.scene.count_objects()
            + self.scene.count_nodes()
            + self.scene.count_roads()
            + self.scene.count_edges()
        )

        total_slots = self.scene.count_objects(
            "parking_slot"
        )

        available_slots = (
            self.scene.count_parking_slots_by_status(
                "available"
            )
        )

        reserved_slots = (
            self.scene.count_parking_slots_by_status(
                "reserved"
            )
        )

        occupied_slots = (
            self.scene.count_parking_slots_by_status(
                "occupied"
            )
        )

        occupied_utilization = (
            occupied_slots / total_slots * 100
            if total_slots > 0
            else 0.0
        )

        self.total_info.setText(
            f"Total map elements: {total}"
        )

        self.slot_info.setText(
            f"Parking Slots: {total_slots}"
        )

        self.parking_status_info.setText(
            f"Available: {available_slots}  |  "
            f"Reserved: {reserved_slots}  |  "
            f"Occupied: {occupied_slots}"
        )

        self.parking_utilization_info.setText(
            f"Occupied Utilization: "
            f"{occupied_utilization:.1f}%"
        )

        self.building_info.setText(
            f"Buildings: "
            f"{self.scene.count_objects('building')}"
        )

        self.gate_info.setText(
            f"Gates: "
            f"{self.scene.count_objects('gate')}"
        )

        self.car_info.setText(
            f"Car Placeholders: "
            f"{self.scene.count_objects('car')}"
        )

        self.road_info.setText(
            f"Vehicle Roads: "
            f"{self.scene.count_roads('vehicle')}"
        )

        self.pedestrian_info.setText(
            f"Pedestrian Paths: "
            f"{self.scene.count_roads('pedestrian')}"
        )

        self.node_info.setText(
            f"Graph Nodes: "
            f"{self.scene.count_nodes()}"
        )

        self.vehicle_edge_info.setText(
            f"Vehicle Edges: "
            f"{self.scene.count_edges('vehicle')}"
        )

        self.pedestrian_edge_info.setText(
            f"Pedestrian Edges: "
            f"{self.scene.count_edges('pedestrian')}"
        )

        # =================================
        # SIMULATION STATISTICS
        # =================================

        controller = getattr(
            self,
            "vehicle_simulator",
            None
        )

        simulated_cars = (
            controller.car_count
            if controller is not None
            else 0
        )

        travelled_distance_px = 0.0

        if controller is not None:

            travelled_distance_px = sum(
                float(
                    agent.get(
                        "vehicle_distance_travelled_px",
                        0.0
                    )
                )
                for agent in controller.agents
                if agent["car"].scene() is self.scene
            )

        travelled_distance_m = (
            travelled_distance_px
            / GraphEdgeItem.PIXELS_PER_METER
        )

        self.simulated_car_info.setText(
            f"Simulated Vehicles: {simulated_cars}"
        )

        self.vehicle_distance_info.setText(
            f"Vehicle Distance Travelled: "
            f"{travelled_distance_m:.2f} m"
        )

    # =====================================
    # SAVE LAYOUT
    # =====================================

    def save_layout_dialog(self):

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Parking Layout",
            "parking_layout.json",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        if not file_path.lower().endswith(".json"):
            file_path += ".json"

        try:

            save_layout(
                self.scene,
                file_path
            )

            self.statusBar().showMessage(
                f"Layout saved: {file_path}",
                5000
            )

            QMessageBox.information(
                self,
                "Save Successful",
                f"Layout berhasil disimpan:\n{file_path}"
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Save Failed",
                str(error)
            )

    # =====================================
    # LOAD LAYOUT
    # =====================================

    def load_layout_dialog(self):

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Parking Layout",
            "",
            "JSON Files (*.json)"
        )

        if not file_path:
            return

        answer = QMessageBox.question(
            self,
            "Load Layout",
            "Layout saat ini akan digantikan. Lanjutkan?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:

            result = load_layout(
                self.scene,
                file_path
            )

            self.grid_checkbox.setChecked(
                self.scene.grid_visible
            )

            self.update_stats()
            self.update_properties()
            self.refresh_node_selectors()
            self.refresh_assignment_selectors()

            self.view.fit_to_scene()

            self.statusBar().showMessage(
                f"Layout loaded: {file_path}",
                5000
            )

            QMessageBox.information(
                self,
                "Load Successful",
                (
                    "Layout berhasil dimuat!\n\n"
                    f"Objects: {result['objects']}\n"
                    f"Nodes: {result['nodes']}\n"
                    f"Roads: {result['roads']}\n"
                    f"Edges: {result['edges']}"
                )
            )

        except Exception as error:

            QMessageBox.critical(
                self,
                "Load Failed",
                str(error)
            )
