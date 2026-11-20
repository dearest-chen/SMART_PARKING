
from PySide6.QtCore import Qt, QPoint, QMimeData
from PySide6.QtGui import QDrag
from PySide6.QtWidgets import QPushButton, QApplication


class ToolButton(QPushButton):

    TOOL_MIME = "application/x-smart-parking-tool"

    DRAGGABLE_TOOLS = {
        "parking_slot",
        "building",
        "gate",
        "car"
    }

    def __init__(self, text, tool_key, parent=None):

        super().__init__(text, parent)

        self.tool_key = tool_key
        self._drag_start_pos = None

        self.setCursor(
            Qt.CursorShape.OpenHandCursor
        )

    def mousePressEvent(self, event):

        if event.button() == Qt.MouseButton.LeftButton:

            self._drag_start_pos = event.position().toPoint()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):

        if (
            self.tool_key in self.DRAGGABLE_TOOLS
            and self._drag_start_pos is not None
            and event.buttons() & Qt.MouseButton.LeftButton
        ):

            current_position = event.position().toPoint()

            distance = (
                current_position - self._drag_start_pos
            ).manhattanLength()

            if distance >= QApplication.startDragDistance():

                self.start_tool_drag()

                self._drag_start_pos = None
                return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):

        self._drag_start_pos = None

        super().mouseReleaseEvent(event)

    def start_tool_drag(self):

        drag = QDrag(self)

        mime = QMimeData()

        mime.setData(
            self.TOOL_MIME,
            self.tool_key.encode("utf-8")
        )

        drag.setMimeData(mime)

        pixmap = self.grab()

        drag.setPixmap(pixmap)

        drag.setHotSpot(
            QPoint(
                pixmap.width() // 2,
                pixmap.height() // 2
            )
        )

        drag.exec(
            Qt.DropAction.CopyAction
        )
