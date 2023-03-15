from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtCore import QRectF, QPointF
from typing import Optional

from PySide2.QtGui import QPainter, QPen, QColor, QPainterPath, QFont, QPolygonF
from PySide2.QtWidgets import QStyleOptionGraphicsItem, QWidget
from PySide2.QtCore import Qt

from .node_label import NodeLabel


class LinkItem(QGraphicsItem):
    """GraphicsItem for network links.
    
    Displayed as a line between the starting node i and ending node j of the link.
    """
    def __init__(
        self, 
        key: tuple[int, int], 
        pts: list[tuple[float, float]], 
        parent: Optional[QGraphicsItem] = None) -> None:

        super().__init__(parent=parent)
        self.key = key
        self.pts = pts
        self.polyline = QPolygonF([QPointF(x, y) for x, y in pts])

        self.topleft_x = min([x for x, _ in pts])
        self.topleft_y = min([y for _, y in pts])
        self.width = abs(max([x for x, _ in pts]) - self.topleft_x)
        self.height = abs(max([y for _, y in pts]) - self.topleft_y)

        self.is_on_selected_path = False
    
    def boundingRect(self) -> QRectF:
        return QRectF(self.topleft_x, self.topleft_y, self.width, self.height)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget]) -> None:
        if self.is_on_selected_path:
            pen = QPen(QColor("green"), 5)
        else:
            pen = QPen(Qt.gray, 2)

        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawPolyline(self.polyline)
        


class NodeItem(QGraphicsItem):
    """GraphicsItem for network nodes.
    
    Displayed as a circle at the node xy coordinate.
    """
    def __init__(self, x, y, name, parent: Optional[QGraphicsItem] = None) -> None:
        super().__init__(parent=parent)
        self.x = x
        self.y = y
        self.name = name
        self.diameter = 8.0
        self.pen_width = 1

        self.node_label = NodeLabel(self, self.name)
        self.node_label.setPos(self.x, self.y)
    
    def boundingRect(self) -> QRectF:
        return QRectF(self.x - self.diameter / 2 - self.pen_width, 
                      self.y - self.diameter / 2 - self.pen_width,
                      self.diameter + self.pen_width * 2,
                      self.diameter + self.pen_width * 2)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget]) -> None:

        pen = QPen(Qt.blue)
        pen.setWidth(self.pen_width)
        pen.setCosmetic(True)

        painter.setPen(pen)
        painter.setBrush(Qt.gray)

        lod = option.levelOfDetailFromTransform(painter.worldTransform())
        painter.scale(1 / lod, 1 / lod)

        painter.drawEllipse((self.x * lod) - self.diameter / 2, 
                            (self.y * lod) - self.diameter / 2, 
                            self.diameter,
                            self.diameter)


        
