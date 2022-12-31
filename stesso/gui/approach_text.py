from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QPainterPath, QFont
from PySide2.QtCore import Qt, QRectF

SCALE_VALUE = 22

class LabelText(QGraphicsItem):
    def __init__(self, parent, message, flip_text) -> None:
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)
        self.message = message
        self.flip = flip_text

    def boundingRect(self):
        return QRectF(-14, -14, 100, 100)

    def shape(self):
        """Defines the physical shape for selection."""
        path = QPainterPath()
        path.addEllipse(0, 0, SCALE_VALUE, SCALE_VALUE)
        return path

    def paint(self, painter, option, widget) -> None:

        # Rotate Text
        # https://stackoverflow.com/questions/45509348/cannot-understand-how-to-rotate-text-using-drawtext-for-qpainter

        font = QFont("consolas", 14)
        painter.setFont(font)
        
        if self.flip:
            #painter.translate(100 + SCALE_VALUE * 2, 22)
            painter.translate(100, 0)
            painter.scale(-1, 1)
        else:
            painter.translate(0, 22)
            painter.scale(1, -1)
        
        # # painter.drawText(SCALE_VALUE, 14, self.message)
        # painter.drawText(SCALE_VALUE, 0, 100, 22, Qt.AlignRight, self.message)
        # painter.drawRect(SCALE_VALUE, 0, 100, 22)
        # painter.drawRect(100 + SCALE_VALUE * 2, 0, 2, 22)

        # painter.translate(100 + 0 * 2, 22)
        # painter.scale(-1, -1)
        
        # painter.drawText(SCALE_VALUE, 14, self.message)
        painter.drawText(0, 0, 100, 22, Qt.AlignRight, self.message)
        #painter.drawRect(0, 0, 100, 22)
        # painter.drawRect(100 + 0 * 2, 0, 2, 22)
        

    def mousePressEvent(self, event) -> None:
        print("sub item mouse press")
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
