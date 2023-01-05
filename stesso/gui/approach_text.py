from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QPainterPath, QFont, QBrush, QColor
from PySide2.QtCore import Qt, QRectF

SCALE_VALUE = 22
AVG_CHAR_WIDTH = 10

class LabelText(QGraphicsItem):
    def __init__(self, parent, message, flip_text) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)
        self.message = message
        self.flip = flip_text
        self._debug_clicked = False

    def boundingRect(self):
        return QRectF(0, 0, len(self.message) * AVG_CHAR_WIDTH, 22)

    # def shape(self):
    #     """Defines the physical shape for selection."""
    #     path = QPainterPath()
    #     path.addEllipse(0, 0, SCALE_VALUE, SCALE_VALUE)
    #     return path

    def paint(self, painter, option, widget) -> None:

        # Rotate Text
        # https://stackoverflow.com/questions/45509348/cannot-understand-how-to-rotate-text-using-drawtext-for-qpainter

        font = QFont("consolas", 14)
        painter.setFont(font)
        
        if self.flip:
            #painter.translate(100 + SCALE_VALUE * 2, 22)
            painter.translate(len(self.message) * AVG_CHAR_WIDTH, 0)
            painter.scale(-1, 1)
        else:
            painter.translate(0, 22)
            painter.scale(1, -1)
        
        # Draw Bounding Rect for debugging
        text_width = len(self.message) * AVG_CHAR_WIDTH

        # brush = QBrush(QColor(240, 240, 240))
        # painter.setBrush(brush)
        if self._debug_clicked:
            painter.drawRect(self.boundingRect())
            painter.drawEllipse(0, 0, 5, 5)

        
        painter.drawText(0, 0, len(self.message) * AVG_CHAR_WIDTH, 22, Qt.AlignRight, self.message)
        

    def mousePressEvent(self, event) -> None:
        print(f"sub item mouse press: {self.message}")
        self._debug_clicked = not self._debug_clicked
        self.setFocus()
        event.ignore()

    def mouseReleaseEvent(self, event) -> None:
        print("sub item mouse release")

    def keyPressEvent(self, event) -> None:
        print(f"subitem keypress: {event.text()}")
        self.update_message(event.text())
        self.update()
        return super().keyPressEvent(event)
    
    def update_message(self, new_text):
        self.message = new_text
        self.update()
