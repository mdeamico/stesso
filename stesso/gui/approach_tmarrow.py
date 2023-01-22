
from PySide2.QtWidgets import QGraphicsItem

from PySide2.QtGui import QPen
from PySide2.QtCore import Qt, QRectF, QLineF


SCALE_VALUE = 22


class TMArrow(QGraphicsItem):
    def __init__(self, parent, angle_in, angle_out, angle_rel) -> None:
        super().__init__(parent)
        self.angle_in = angle_in
        self.angle_out = angle_out + angle_in
        self.angle_rel = angle_rel
    
    def boundingRect(self):
        return QRectF(0, 0, SCALE_VALUE, SCALE_VALUE)
    
    def paint(self, painter, option, widget) -> None:
        painter.drawRect(self.boundingRect())
        
        line_in = QLineF(0, 0, SCALE_VALUE * 0.4, 0)
        # line_in always has zero angle because it is parallel to the approach
        # line_in.setAngle(self.angle_in)
        line_in.translate(SCALE_VALUE / 2, SCALE_VALUE / 2)
        
        line_out = QLineF(0, 0, SCALE_VALUE * 0.4, 0)
        #line_out.setAngle(self.angle_out)
        line_out.setAngle(self.angle_rel)
        line_out.translate(SCALE_VALUE / 2, SCALE_VALUE / 2)
        
        painter.setPen(QPen(Qt.green, 3))
        painter.drawLine(line_in)

        painter.setPen(QPen(Qt.red, 3))
        painter.drawLine(line_out)

        # painter.drawEllipse(line_out.p2().x(), line_out.p2().y(), 3, 3)
        #return super().paint(painter, option, widget)
