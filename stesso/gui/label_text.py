from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QRectF, QObject, Signal

from .label_props import LabelProps

SCALE_VALUE = 22
AVG_CHAR_WIDTH = 10


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

        self.font = QFont("consolas", 14)
        
        self.setToolTip(f"{self.props.data_name}: {self.text}")

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
            painter.drawRect(self.boundingRect())
            painter.drawEllipse(0, 0, 3, 3)

        painter.setFont(self.font)
        painter.drawText(0, 0, text_width, SCALE_VALUE, Qt.AlignRight, self.text)

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
        self.update()
        return self.text
    

class Communicate(QObject):
    click = Signal(tuple, bool, LabelProps, str, LabelText)