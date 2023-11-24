from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QFont, QPainter, QPixmap
from PySide2.QtCore import Qt, QRectF, QPointF


# TODO: convert these constants to be dependent on actual font size used.
SCALE_VALUE = 22
AVG_CHAR_WIDTH = 10
CHAR_CAP_HEIGHT = 12


class NodeLabel(QGraphicsItem):
    def __init__(self, parent, text: str) -> None:
        super().__init__(parent)
        self.x_offset = 5
        self.y_offset = 5

        self.text = text
        self.lod = 1
        self.antialias_scale = 2
        self.text_pixmap = self._setup_text_pixmap()

    def _setup_text_pixmap(self):
        
        width_px = (len(self.text) * AVG_CHAR_WIDTH) * self.antialias_scale
        height_px = CHAR_CAP_HEIGHT * self.antialias_scale

        canvas = QPixmap(width_px, height_px)
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)

        font = QFont("consolas", 14 * self.antialias_scale)
        painter.setFont(font)
        painter.setPen(Qt.blue)

        painter.scale(1.0, -1.0)
        painter.drawText(0, 0, self.text)

        return canvas

    def boundingRect(self):
        return QRectF(self.x_offset / self.lod, 
                      (self.y_offset) / self.lod, 
                      len(self.text) * AVG_CHAR_WIDTH / self.lod, 
                      CHAR_CAP_HEIGHT / self.lod)

    def paint(self, painter, option, widget) -> None:
        self.prepareGeometryChange()
        self.lod = option.levelOfDetailFromTransform(painter.worldTransform())
                
        scale_mult = (1 / self.antialias_scale) / self.lod
        painter.scale(scale_mult, scale_mult)
        
        painter.drawPixmap(QPointF(self.x_offset * self.antialias_scale,
                                   self.y_offset * self.antialias_scale), 
                                   self.text_pixmap)
        
        