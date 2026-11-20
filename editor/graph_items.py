
import math

from PySide6.QtCore import Qt, QRectF, QLineF
from PySide6.QtGui import (
    QColor,
    QPen,
    QPainter,
    QFont,
    QBrush
)

from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsItem
)


# =====================================
# GRAPH NODE
# =====================================

class GraphNodeItem(QGraphicsEllipseItem):

    def __init__(self, node_id):

        super().__init__(-10, -10, 20, 20)

        self.node_id = node_id

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable
            | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            | QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

        self.setZValue(30)

        self.setCursor(
            Qt.CursorShape.OpenHandCursor
        )

    def paint(self, painter, option, widget=None):

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        color = (
            QColor("#2563EB")
            if self.isSelected()
            else QColor("#0F766E")
        )

        painter.setPen(
            QPen(QColor("#FFFFFF"), 2)
        )

        painter.setBrush(
            QBrush(color)
        )

        painter.drawEllipse(
            self.rect()
        )

        painter.setPen(
            QColor("#0F172A")
        )

        font = QFont("Segoe UI", 8)
        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            QRectF(-35, -35, 70, 20),
            Qt.AlignmentFlag.AlignCenter,
            self.node_id
        )

    def itemChange(self, change, value):

        scene = self.scene()

        # Snap node to grid before moving
        if (
            change == QGraphicsItem.GraphicsItemChange.ItemPositionChange
            and scene is not None
        ):

            return scene.snap_point(value)

        # Update connected edges after moving
        if (
            change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged
            and scene is not None
        ):

            scene.update_edges_for_node(self)
            scene.layoutChanged.emit()

        return super().itemChange(change, value)


# =====================================
# ROAD SEGMENT
# =====================================

class RoadSegmentItem(QGraphicsLineItem):

    def __init__(
        self,
        road_id,
        start,
        end,
        road_width,
        mode="vehicle"
    ):

        super().__init__(
            QLineF(start, end)
        )

        self.road_id = road_id
        self.mode = mode
        self.road_width = road_width

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setZValue(2)

        self.setToolTip(
            f"{road_id} - {mode.title()} Road"
        )

    def boundingRect(self):

        extra = self.road_width / 2 + 5

        return super().boundingRect().adjusted(
            -extra,
            -extra,
            extra,
            extra
        )

    def paint(self, painter, option, widget=None):

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        line = self.line()

        if self.mode == "vehicle":

            road_color = (
                QColor("#2563EB")
                if self.isSelected()
                else QColor("#64748B")
            )

            painter.setPen(
                QPen(
                    road_color,
                    self.road_width,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                )
            )

            painter.drawLine(line)

            painter.setPen(
                QPen(
                    QColor("#F8FAFC"),
                    2,
                    Qt.PenStyle.DashLine,
                    Qt.PenCapStyle.RoundCap
                )
            )

            painter.drawLine(line)

        else:

            path_color = (
                QColor("#2563EB")
                if self.isSelected()
                else QColor("#BBF7D0")
            )

            painter.setPen(
                QPen(
                    path_color,
                    self.road_width,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                    Qt.PenJoinStyle.RoundJoin
                )
            )

            painter.drawLine(line)

            painter.setPen(
                QPen(
                    QColor("#15803D"),
                    2,
                    Qt.PenStyle.DashLine,
                    Qt.PenCapStyle.RoundCap
                )
            )

            painter.drawLine(line)

        painter.restore()


# =====================================
# GRAPH EDGE
# =====================================

class GraphEdgeItem(QGraphicsLineItem):

    PIXELS_PER_METER = 10

    def __init__(
        self,
        edge_id,
        node_a,
        node_b,
        mode="vehicle"
    ):

        super().__init__()

        self.edge_id = edge_id
        self.node_a = node_a
        self.node_b = node_b
        self.mode = mode

        self.weight_m = 0.0

        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )

        self.setZValue(5)

        self.update_position()

    # UPDATE EDGE POSITION AND DISTANCE

    def update_position(self):

        start = self.node_a.pos()
        end = self.node_b.pos()

        self.setLine(
            QLineF(start, end)
        )

        distance = math.hypot(
            end.x() - start.x(),
            end.y() - start.y()
        )

        self.weight_m = (
            distance / self.PIXELS_PER_METER
        )

        self.setToolTip(
            f"{self.edge_id} | {self.weight_m:.1f} m"
        )

    # EDGE BOUNDING RECT

    def boundingRect(self):

        return super().boundingRect().adjusted(
            -35,
            -25,
            35,
            25
        )

    # EDGE VISUALIZATION

    def paint(self, painter, option, widget=None):

        painter.save()

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        if self.mode == "vehicle":

            color = (
                QColor("#2563EB")
                if self.isSelected()
                else QColor("#F59E0B")
            )

            style = Qt.PenStyle.DashLine

        else:

            color = (
                QColor("#2563EB")
                if self.isSelected()
                else QColor("#16A34A")
            )

            style = Qt.PenStyle.DotLine

        painter.setPen(
            QPen(
                color,
                2.5,
                style
            )
        )

        painter.drawLine(
            self.line()
        )

        midpoint = self.line().pointAt(0.5)

        label_rect = QRectF(
            midpoint.x() - 28,
            midpoint.y() - 12,
            56,
            22
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            QColor("#FFFFFF")
        )

        painter.drawRoundedRect(
            label_rect,
            5,
            5
        )

        painter.setPen(
            QColor("#334155")
        )

        font = QFont("Segoe UI", 8)
        font.setBold(True)

        painter.setFont(font)

        painter.drawText(
            label_rect,
            Qt.AlignmentFlag.AlignCenter,
            f"{self.weight_m:.1f} m"
        )

        painter.restore()
