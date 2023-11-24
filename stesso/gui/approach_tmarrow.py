
from PySide2.QtWidgets import QGraphicsItem

from PySide2.QtGui import QPen
from PySide2.QtCore import Qt, QRectF, QLineF

from gui.settings import GUIConfig


class TMArrow(QGraphicsItem):
    def __init__(self, parent, angle_in, angle_out, angle_rel) -> None:
        super().__init__(parent)
        self.angle_in = angle_in
        self.angle_out = angle_out + angle_in
        self.angle_rel = angle_rel
        self.lod = 1
    
    def boundingRect(self):
        return QRectF(0, 0, GUIConfig.FONT_HEIGHT / self.lod, GUIConfig.FONT_HEIGHT / self.lod)
    
    def paint(self, painter, option, widget) -> None:
        self.prepareGeometryChange()
        self.lod = option.levelOfDetailFromTransform(painter.worldTransform())
        painter.scale(1 / self.lod, 1 / self.lod)

        # painter.drawRect(self.boundingRect())
        
        line_in = QLineF(0, 0, GUIConfig.FONT_HEIGHT * 0.4, 0)
        # Line_in always has zero angle because it is parallel to the approach,
        # so we don't need to call setAngle(). We only need to call translate()
        line_in.translate(GUIConfig.FONT_HEIGHT / 2, GUIConfig.FONT_HEIGHT / 2)
        
        line_out = QLineF(0, 0, GUIConfig.FONT_HEIGHT * 0.4, 0)
        line_out.setAngle(self.angle_rel)
        line_out.translate(GUIConfig.FONT_HEIGHT / 2, GUIConfig.FONT_HEIGHT / 2)
        
        painter.setPen(QPen(Qt.green, 3))
        painter.drawLine(line_in)

        painter.setPen(QPen(Qt.red, 3))
        painter.drawLine(line_out)

