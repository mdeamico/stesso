from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QPainterPath, QFont, QBrush, QColor
from PySide2.QtCore import Qt, QRectF, QObject, Signal

SCALE_VALUE = 22
AVG_CHAR_WIDTH = 10

class Communicate(QObject):
    is_selected = Signal(tuple, bool)



class LabelText(QGraphicsItem):

    def __init__(self, parent, message, flip_text, key: tuple, is_selectable: bool) -> None:
        super().__init__(parent)
        # self.setFlags(QGraphicsItem.ItemIsFocusable | QGraphicsItem.ItemIsSelectable)
        # TODO: store text "info" assigned_volume, target_volume, etc...
        self.key = key
        self.message = message
        self.flip = flip_text
        self._debug_clicked = False
        self.signals = Communicate()
        self.is_selectable = is_selectable
        self.setToolTip(f"Tool Tip Test: {self.message}")

    def slot_test(self, message):
        print(f"slot from approach_text: {message}")

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
        print(f"approach_text mouse press: {self.message} selectable?{self.is_selectable}")
        if not self.is_selectable:
            return
            
        self._debug_clicked = not self._debug_clicked
        self.signals.is_selected.emit(self.key, self._debug_clicked)
        # self.setFocus()
        # self.update()
        # event.ignore()

    # def mouseReleaseEvent(self, event) -> None:
    #     print("approach_text mouse release")

    # def keyPressEvent(self, event) -> None:
    #     print(f"approach_text keypress: {event.text()}")
    #     # self.update_message(event.text())
    #     # self.update()
    #     return super().keyPressEvent(event)
    
    def update_message(self, new_text):
        self.message = new_text
        self.setToolTip(f"Tool Tip Test: {self.message}")
        self.update()
