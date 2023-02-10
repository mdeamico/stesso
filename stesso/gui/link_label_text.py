from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QFont, QBrush, QPen, QColor
from PySide2.QtCore import Qt, QRectF, QObject, Signal

from .textinfo import TextInfo

SCALE_VALUE = 22
AVG_CHAR_WIDTH = 10

class Communicate(QObject):
    is_selected = Signal(tuple, bool)



class LinkLabelText(QGraphicsItem):

    def __init__(self, parent, text, flip_text: bool, key: tuple, text_info: TextInfo) -> None:
        super().__init__(parent)
        
        self.text = text
        self.flip = flip_text

        self.key = key
        self.info = text_info
        
        self.selected = False
        self.signals = Communicate()
        
        self.setToolTip(f"{self.info.InfoType}: {self.text}")

    def boundingRect(self):
        return QRectF(0, 0, len(self.text) * AVG_CHAR_WIDTH, SCALE_VALUE)

    def paint(self, painter, option, widget) -> None:

        text_width = len(self.text) * AVG_CHAR_WIDTH
        
        if self.flip:
            painter.translate(text_width, 0)
            painter.scale(-1, 1)
        else:
            painter.translate(0, SCALE_VALUE)
            painter.scale(1, -1)
        
        if self.selected:
            # brush = QBrush(QColor(240, 240, 0))
            # painter.setBrush(brush)
            painter.drawRect(self.boundingRect())
            painter.drawEllipse(0, 0, 3, 3)

        pen = QPen(QColor(255, 0, 0))
        painter.setPen(pen)

        font = QFont("consolas", 14)
        painter.setFont(font)

        painter.drawText(0, 0, text_width, SCALE_VALUE, Qt.AlignRight, self.text)

    def mousePressEvent(self, event) -> None:
        print(f"link text mouse press: {self.text} editable? {self.info.editable}")
        if not self.info.editable:
            return
            
        self.selected = not self.selected
        self.signals.is_selected.emit(self.key, self.selected)
        self.update()
    
    def update_message(self):
        new_text = self.info.get_text_fn(self.key)
        self.text = f"{self.info.prefix}{new_text}{self.info.postfix}"
        self.setToolTip(f"{self.info.InfoType}: {self.text}")
        self.update()
        return self.text
