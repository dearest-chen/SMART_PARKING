
from PySide6.QtCore import Qt, Signal, QLineF
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsLineItem

from editor.graph_items import GraphNodeItem


class MapView(QGraphicsView):

    objectAdded = Signal(object)
    message = Signal(str)

    TOOL_MIME = "application/x-smart-parking-tool"

    OBJECT_TOOLS = {
        "parking_slot",
        "building",
        "gate",
        "car"
    }

    def __init__(self, scene, parent=None):

        super().__init__(scene, parent)

        self.parking_scene = scene

        self.current_tool = "select"

        self.road_width = 70
        self.pedestrian_width = 14

        self._panning = False
        self._space_pressed = False
        self._last_pan_pos = None

        self._drawing_start = None
        self._drawing_mode = None
        self._preview_line = None

        self._pending_node = None

        self._first_fit = True

        self.setObjectName("mapView")

        self.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
        )

        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.setDragMode(
            QGraphicsView.DragMode.NoDrag
        )

        # Zoom anchoring is handled manually in apply_zoom().
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.NoAnchor
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

        self.setAlignment(
            Qt.AlignmentFlag.AlignLeft
            | Qt.AlignmentFlag.AlignTop
        )

        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )
        # =================================
        # SCROLLBAR SETTINGS
        # =================================

        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOn
        )

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )

        self.verticalScrollBar().setMinimumWidth(16)

        self.verticalScrollBar().setStyleSheet("""
            QScrollBar:vertical {
                background: #E2E8F0;
                width: 16px;
                margin: 4px 2px;
                border: none;
                border-radius: 8px;
            }

            QScrollBar::handle:vertical {
                background: #94A3B8;
                min-height: 40px;
                border-radius: 6px;
            }

            QScrollBar::handle:vertical:hover {
                background: #64748B;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
        """)

        self.setBackgroundBrush(
            Qt.GlobalColor.white
        )

        self.setMinimumHeight(500)

        self.set_tool("select")

    # =================================
    # TOOL MANAGEMENT
    # =================================

    def set_tool(self, tool):

        self.current_tool = tool

        self._pending_node = None

        if tool == "select":

            self.setCursor(
                Qt.CursorShape.ArrowCursor
            )

        else:

            self.setCursor(
                Qt.CursorShape.CrossCursor
            )

    def set_road_width(self, width):

        self.road_width = int(width)

    # =================================
    # MOUSE PRESS
    # =================================

    def mousePressEvent(self, event):

        position = event.position().toPoint()

        # PAN CANVAS

        if (
            event.button() == Qt.MouseButton.MiddleButton
            or (
                event.button() == Qt.MouseButton.LeftButton
                and self._space_pressed
            )
        ):

            self._panning = True
            self._last_pan_pos = position

            self.setCursor(
                Qt.CursorShape.ClosedHandCursor
            )

            event.accept()
            return

        if event.button() != Qt.MouseButton.LeftButton:

            super().mousePressEvent(event)
            return

        scene_position = self.mapToScene(position)

        # DRAW VEHICLE ROAD

        if self.current_tool in (
            "draw_road",
            "pedestrian_path"
        ):

            self._drawing_start = scene_position

            if self.current_tool == "draw_road":

                self._drawing_mode = "vehicle"

                preview_width = self.road_width

                preview_color = QColor("#64748B")

            else:

                self._drawing_mode = "pedestrian"

                preview_width = self.pedestrian_width

                preview_color = QColor("#86EFAC")

            self._preview_line = QGraphicsLineItem()

            self._preview_line.setPen(
                QPen(
                    preview_color,
                    preview_width,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap
                )
            )

            self._preview_line.setZValue(100)

            self.parking_scene.addItem(
                self._preview_line
            )

            self._preview_line.setLine(
                QLineF(
                    scene_position,
                    scene_position
                )
            )

            event.accept()
            return

        # ADD NODE

        if self.current_tool == "add_node":

            node = self.parking_scene.add_node(
                scene_position
            )

            self.objectAdded.emit(node)

            event.accept()
            return

        # CONNECT VEHICLE OR PEDESTRIAN NODES

        if self.current_tool in (
            "connect_nodes",
            "connect_pedestrian"
        ):

            candidate = self.itemAt(position)

            while (
                candidate is not None
                and not isinstance(candidate, GraphNodeItem)
            ):

                candidate = candidate.parentItem()

            if candidate is None:

                self.message.emit(
                    "Klik tepat pada sebuah node."
                )

                event.accept()
                return

            if self._pending_node is None:

                self.parking_scene.clearSelection()

                self._pending_node = candidate

                candidate.setSelected(True)

                self.message.emit(
                    f"{candidate.node_id} dipilih. "
                    "Sekarang klik node tujuan."
                )

            else:

                mode = (
                    "vehicle"
                    if self.current_tool == "connect_nodes"
                    else "pedestrian"
                )

                edge = self.parking_scene.connect_nodes(
                    self._pending_node,
                    candidate,
                    mode
                )

                if edge is not None:

                    self.message.emit(
                        f"Koneksi {edge.edge_id} berhasil. "
                        f"Jarak: {edge.weight_m:.1f} meter."
                    )

                else:

                    self.message.emit(
                        "Koneksi tidak dibuat. "
                        "Node sama atau koneksi sudah tersedia."
                    )

                self._pending_node = None

                self.parking_scene.clearSelection()

            event.accept()
            return

        # ADD PARKING OBJECTS

        if self.current_tool in self.OBJECT_TOOLS:

            item = self.parking_scene.add_object(
                self.current_tool,
                scene_position
            )

            if item is not None:

                self.objectAdded.emit(item)

            event.accept()
            return

        self.setFocus()

        super().mousePressEvent(event)

    # =================================
    # MOUSE MOVE
    # =================================

    def mouseMoveEvent(self, event):

        if self._panning:

            current_position = event.position().toPoint()

            delta = current_position - self._last_pan_pos

            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )

            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )

            self._last_pan_pos = current_position

            event.accept()
            return

        if self._preview_line is not None:

            current_position = self.mapToScene(
                event.position().toPoint()
            )

            self._preview_line.setLine(
                QLineF(
                    self._drawing_start,
                    current_position
                )
            )

            event.accept()
            return

        super().mouseMoveEvent(event)

    # =================================
    # MOUSE RELEASE
    # =================================

    def mouseReleaseEvent(self, event):

        if self._panning:

            self._panning = False
            self._last_pan_pos = None

            if self._space_pressed:

                self.setCursor(
                    Qt.CursorShape.OpenHandCursor
                )

            else:

                self.set_tool(self.current_tool)

            event.accept()
            return

        if (
            self._preview_line is not None
            and event.button() == Qt.MouseButton.LeftButton
        ):

            end_position = self.mapToScene(
                event.position().toPoint()
            )

            start_position = self._drawing_start

            mode = self._drawing_mode

            self.parking_scene.removeItem(
                self._preview_line
            )

            self._preview_line = None

            self._drawing_start = None
            self._drawing_mode = None

            if mode == "vehicle":

                width = self.road_width

            else:

                width = self.pedestrian_width

            road = self.parking_scene.add_road(
                start_position,
                end_position,
                width,
                mode
            )

            if road is not None:

                self.message.emit(
                    f"{road.road_id} berhasil dibuat."
                )

            else:

                self.message.emit(
                    "Jalan terlalu pendek. Coba tarik lebih jauh."
                )

            event.accept()
            return

        super().mouseReleaseEvent(event)

    # =================================
    # ZOOM & SCROLL
    # =================================

    def wheelEvent(self, event):

        pixel_delta = event.pixelDelta()
        angle_delta = event.angleDelta()
        modifiers = event.modifiers()

        # CTRL + SCROLL = ZOOM AT MOUSE POSITION

        if modifiers & Qt.KeyboardModifier.ControlModifier:

            delta = (
                pixel_delta.y()
                if pixel_delta.y() != 0
                else angle_delta.y()
            )

            if delta == 0:
                event.ignore()
                return

            # Smooth zoom for trackpads; one 120-unit wheel step = 15%.
            factor = 1.15 ** (delta / 120.0)

            self.apply_zoom(
                factor,
                event.position().toPoint()
            )

            event.accept()
            return

        # SHIFT + SCROLL = HORIZONTAL PAN

        if modifiers & Qt.KeyboardModifier.ShiftModifier:

            scrollbar = self.horizontalScrollBar()

            delta = (
                pixel_delta.x()
                if pixel_delta.x() != 0
                else angle_delta.y()
            )

        # NORMAL SCROLL = VERTICAL PAN

        else:

            scrollbar = self.verticalScrollBar()

            delta = (
                pixel_delta.y()
                if pixel_delta.y() != 0
                else angle_delta.y()
            )

        if delta == 0:
            event.ignore()
            return

        if not pixel_delta.isNull():

            scroll_amount = delta

        else:

            scroll_amount = (
                delta / 120.0
            ) * scrollbar.singleStep() * 3

        scrollbar.setValue(
            scrollbar.value() - int(scroll_amount)
        )

        event.accept()

    # =================================
    # ZOOM AT CURSOR POSITION
    # =================================

    def apply_zoom(self, factor, anchor_pos=None):

        current_scale = self.transform().m11()

        if current_scale <= 0:
            return

        target_scale = max(
            0.25,
            min(4.0, current_scale * factor)
        )

        actual_factor = target_scale / current_scale

        if abs(actual_factor - 1.0) < 0.000001:
            return

        if anchor_pos is None:
            anchor_pos = self.viewport().rect().center()

        # Scene point currently under the chosen viewport position.
        old_scene_pos = self.mapToScene(anchor_pos)

        # Apply zoom without Qt changing the anchor automatically.
        self.scale(actual_factor, actual_factor)

        # Find where that same scene point moved after scaling.
        new_scene_pos = self.mapToScene(anchor_pos)

        # Shift the view so the scene point remains under the cursor.
        delta = new_scene_pos - old_scene_pos

        self.translate(
            delta.x(),
            delta.y()
        )

    def zoom_in(self):

        self.apply_zoom(1.15)

    def zoom_out(self):

        self.apply_zoom(1 / 1.15)

    def fit_to_scene(self):

        self.resetTransform()

        rect = self.sceneRect()

        if rect.width() <= 0 or rect.height() <= 0:
            return

        available_width = max(1, self.viewport().width())
        available_height = max(1, self.viewport().height())

        scale_factor = min(
            available_width / rect.width(),
            1.0
        )

        self.scale(
            scale_factor,
            scale_factor
        )

        # Start at the top-left of the map after fitting its width.
        self.horizontalScrollBar().setValue(
            self.horizontalScrollBar().minimum()
        )

        self.verticalScrollBar().setValue(
            self.verticalScrollBar().minimum()
        )

    # =================================
    # KEYBOARD
    # =================================

    def keyPressEvent(self, event):

        if event.key() in (
            Qt.Key.Key_Delete,
            Qt.Key.Key_Backspace
        ):

            self.delete_selected()

            event.accept()
            return

        if event.key() == Qt.Key.Key_Space:

            self._space_pressed = True

            self.setCursor(
                Qt.CursorShape.OpenHandCursor
            )

            event.accept()
            return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):

        if event.key() == Qt.Key.Key_Space:

            self._space_pressed = False

            if not self._panning:

                self.set_tool(self.current_tool)

            event.accept()
            return

        super().keyReleaseEvent(event)

    # =================================
    # DRAG AND DROP
    # =================================

    def dragEnterEvent(self, event):

        if event.mimeData().hasFormat(self.TOOL_MIME):

            tool = bytes(
                event.mimeData().data(self.TOOL_MIME)
            ).decode("utf-8")

            if tool in self.OBJECT_TOOLS:

                event.acceptProposedAction()
                return

        event.ignore()

    def dragMoveEvent(self, event):

        if event.mimeData().hasFormat(self.TOOL_MIME):

            event.acceptProposedAction()

        else:

            event.ignore()

    def dropEvent(self, event):

        if not event.mimeData().hasFormat(self.TOOL_MIME):

            event.ignore()
            return

        tool = bytes(
            event.mimeData().data(self.TOOL_MIME)
        ).decode("utf-8")

        if tool not in self.OBJECT_TOOLS:

            event.ignore()
            return

        position = self.mapToScene(
            event.position().toPoint()
        )

        item = self.parking_scene.add_object(
            tool,
            position
        )

        if item is not None:

            self.objectAdded.emit(item)

            event.acceptProposedAction()

        else:

            event.ignore()

    # =================================
    # DELETE
    # =================================

    def delete_selected(self):

        self.parking_scene.remove_selected()

    # =================================
    # INITIAL VIEW
    # =================================

    def resizeEvent(self, event):

        super().resizeEvent(event)

        if self._first_fit:

            self.fit_to_scene()

            self._first_fit = False
