
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPen, QPainter, QFont
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem


class ParkingObjectItem(QGraphicsRectItem):

    OBJECT_CONFIG = {
        "parking_slot": {
            "width": 90,
            "height": 48,
            "fill": "#DCFCE7",
            "border": "#16A34A",
        },
        "building": {
            "width": 150,
            "height": 95,
            "fill": "#DBEAFE",
            "border": "#2563EB",
        },
        "gate": {
            "width": 115,
            "height": 55,
            "fill": "#FEF3C7",
            "border": "#D97706",
        },
        "car": {
            "width": 68,
            "height": 38,
            "fill": "#E2E8F0",
            "border": "#475569",
        },
    }

    PARKING_STATUS_CONFIG = {
        "available": {
            "fill": "#DCFCE7",
            "border": "#16A34A",
        },
        "reserved": {
            "fill": "#FEF3C7",
            "border": "#D97706",
        },
        "occupied": {
            "fill": "#FEE2E2",
            "border": "#DC2626",
        },
    }

    def __init__(self, object_type, object_id, label):

        if object_type not in self.OBJECT_CONFIG:
            raise ValueError(
                f"Unknown object type: {object_type}"
            )

        config = self.OBJECT_CONFIG[object_type]

        width = config["width"]
        height = config["height"]

        super().__init__(
            -width / 2,
            -height / 2,
            width,
            height
        )

        self.object_type = object_type
        self.object_id = object_id
        self.label = label

        self.parking_status = (
            "available"
            if object_type == "parking_slot"
            else None
        )

        self.fill_color = QColor(config["fill"])
        self.border_color = QColor(config["border"])

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.setCursor(
            Qt.CursorShape.OpenHandCursor
        )

        self.setZValue(10)

        self.setData(0, object_type)
        self.setData(1, object_id)

        if self.parking_status is not None:
            self.setData(2, self.parking_status)

        self.update_tooltip()

    # =====================================
    # PARKING STATUS
    # =====================================

    def set_parking_status(self, status):

        if self.object_type != "parking_slot":
            raise ValueError(
                "Parking status only applies to parking slots."
            )

        status = str(status).lower().strip()

        if status not in self.PARKING_STATUS_CONFIG:
            raise ValueError(
                f"Invalid parking status: {status}"
            )

        config = self.PARKING_STATUS_CONFIG[status]

        self.parking_status = status

        self.fill_color = QColor(config["fill"])
        self.border_color = QColor(config["border"])

        self.setData(2, status)

        self.update_tooltip()
        self.update()

    # =====================================
    # GET PARKING STATUS
    # =====================================

    def get_parking_status(self):

        return self.parking_status

    # =====================================
    # UPDATE TOOLTIP
    # =====================================

    def update_tooltip(self):

        object_name = self.object_type.replace(
            "_", " "
        ).title()

        if self.parking_status is not None:

            status_text = self.parking_status.title()

            self.setToolTip(
                f"{object_name} - {self.object_id}\n"
                f"Status: {status_text}"
            )

        else:

            self.setToolTip(
                f"{object_name} - {self.object_id}"
            )

    # =====================================
    # PAINT OBJECT
    # =====================================

    def paint(self, painter, option, widget=None):

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        rect = self.rect()

        border = (
            QColor("#2563EB")
            if self.isSelected()
            else self.border_color
        )

        border_width = (
            3 if self.isSelected() else 1.5
        )

        painter.setPen(
            QPen(border, border_width)
        )

        painter.setBrush(
            self.fill_color
        )

        if self.object_type == "car":

            painter.drawRoundedRect(rect, 9, 9)

            roof = rect.adjusted(
                rect.width() * 0.25,
                rect.height() * 0.25,
                -rect.width() * 0.25,
                -rect.height() * 0.25
            )

            painter.setBrush(
                QColor("#CBD5E1")
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.drawRoundedRect(
                roof, 5, 5
            )

            painter.setPen(
                QPen(QColor("#334155"), 1)
            )

        else:

            painter.drawRoundedRect(
                rect, 8, 8
            )

        # PARKING SLOT LABEL

        if self.object_type == "parking_slot":

            label_font = QFont("Segoe UI", 8)
            label_font.setBold(True)

            painter.setFont(label_font)
            painter.setPen(QColor("#1E293B"))

            painter.drawText(
                rect.adjusted(0, 3, 0, -13),
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )

            status_font = QFont("Segoe UI", 6)
            status_font.setBold(True)

            painter.setFont(status_font)

            status_text = self.parking_status.upper()

            painter.drawText(
                rect.adjusted(0, 22, 0, 0),
                Qt.AlignmentFlag.AlignCenter,
                status_text
            )

        else:

            font = QFont("Segoe UI", 9)
            font.setBold(True)

            painter.setFont(font)
            painter.setPen(
                QColor("#1E293B")
            )

            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignCenter,
                self.label
            )

    # =====================================
    # ITEM POSITION CHANGE
    # =====================================

    def itemChange(self, change, value):

        scene = self.scene()

        if (
            change
            == QGraphicsItem.GraphicsItemChange.ItemPositionChange
            and scene is not None
        ):

            return scene.snap_point(value)

        if (
            change
            == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
            and scene is not None
            and hasattr(scene, "layoutChanged")
        ):

            scene.layoutChanged.emit()

        return super().itemChange(change, value)
