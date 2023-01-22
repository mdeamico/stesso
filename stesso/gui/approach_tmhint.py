from PySide2.QtWidgets import QGraphicsItem

from PySide2.QtGui import QPen, QPolygonF
from PySide2.QtCore import Qt, QRectF, QLineF


SCALE_VALUE = 22


class TMHint(QGraphicsItem):
    def __init__(self, line_in: QLineF, line_out: QLineF) -> None:
        super().__init__()
        self.line_in = line_in
        self.line_out = line_out

        self.polygon = QPolygonF([line_in.p2(), line_in.p1(), line_out.p2()])

        self.selected = False
        
    
    def boundingRect(self):
        return self.polygon.boundingRect()
    
    def paint(self, painter, option, widget) -> None:
        if self.selected:
            painter.setPen(QPen(Qt.blue, 6))
            painter.drawPolyline(self.polygon)

        # painter.setPen(QPen(Qt.green, 6))
        # painter.drawRect(self.boundingRect())
