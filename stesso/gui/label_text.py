from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QFont, QFontMetrics, QPainter, QPixmap, QPen, QColor
from PySide2.QtCore import Qt, QRectF, QObject, Signal, QPoint

from .label_props import LabelProps

from gui.settings import GUIConfig

class LabelText(QGraphicsItem):

    def __init__(self, 
                 parent, 
                 text: str, 
                 flip_text: bool, 
                 key: tuple, 
                 properties: LabelProps, 
                 obj_type: str) -> None:
        super().__init__(parent)
        
        self.text = text
        self.flip = flip_text

        self.key = key
        self.props = properties
        self.obj_type = obj_type
        
        self.selected = False
        self.signals = Communicate()

        self._fm_rect_top = GUIConfig.QFONTMETRICS.boundingRect("X").top()
        
        self.setToolTip(f"{self.props.data_name}: {self.text}")

        self.antialias_scale = GUIConfig.FONT_ANTIALIAS
        self.text_pixmap = self._update_text_pixmap()
        self.lod = 1


    def _update_text_pixmap(self):

        width_px = (len(self.text) * GUIConfig.CHAR_WIDTH) * self.antialias_scale
        height_px = GUIConfig.FONT_HEIGHT * self.antialias_scale

        canvas = QPixmap(width_px, height_px)
        canvas.fill(Qt.transparent)
        painter = QPainter(canvas)

        font = QFont(GUIConfig.FONT_NAME, GUIConfig.FONT_SIZE * self.antialias_scale)
        painter.setFont(font)
        painter.setPen(Qt.black)
        
        x_pos_aa_offset = width_px - (len(self.text) * GUIConfig.AA_CHAR_WIDTH)
        painter.translate(x_pos_aa_offset, -self._fm_rect_top * self.antialias_scale)
        # painter.scale(1.0, -1.0)
        
        painter.drawText(0, 0, self.text)

        return canvas



    def boundingRect(self):
        return QRectF(0, 
                      0, 
                      len(self.text) * GUIConfig.CHAR_WIDTH / self.lod, 
                      GUIConfig.FONT_HEIGHT / self.lod)

    def paint(self, painter, option, widget) -> None:
        self.prepareGeometryChange()
        self.lod = option.levelOfDetailFromTransform(painter.worldTransform())

        text_width = len(self.text) * GUIConfig.CHAR_WIDTH / self.lod
        
        if self.flip:
            painter.translate(text_width, 0)
            painter.scale(-1, 1)
        else:
            painter.translate(0, GUIConfig.FONT_HEIGHT / self.lod)
            painter.scale(1, -1)
        
        if self.selected:
            pen = QPen(QColor(0, 0, 255))
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawRect(self.boundingRect())
        
        scale_mult = (1 / self.antialias_scale) / self.lod
        painter.scale(scale_mult, scale_mult)
        
        painter.drawPixmap(QPoint(0, 0), self.text_pixmap)
        
        # painter.setBrush(Qt.black)
        # painter.drawEllipse(QPoint(0, 0), 8, 8)
           

    def mousePressEvent(self, event) -> None:
        print(f"{self.obj_type} mouse press: {self.text} editable? {self.props.editable}")
        if not self.props.editable:
            return
            
        self.selected = not self.selected
        self.signals.click.emit(self.key, self.selected, self.props, self.obj_type, self)
        self.update()
    
    def update_text(self, new_data):
        self.text = f'{self.props.prefix}{self.props.formatted(new_data)}{self.props.postfix}'
        self.setToolTip(f"{self.props.data_name}: {self.text}")
        self.text_pixmap = self._update_text_pixmap()
        self.update()
        return self.text
    

class Communicate(QObject):
    click = Signal(tuple, bool, LabelProps, str, LabelText)