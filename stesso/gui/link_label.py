from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtCore import QRectF, QPointF, QLineF
from PySide2.QtGui import QColor, QPen

from .label_text import LabelText

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from label_props import LabelProps

SCALE_VALUE = 22
CHAR_WIDTH = 10


class LinkItemData(Protocol):
    @property
    def key(self) -> tuple[int, int]:
        ...
    @property
    def pts(self) -> list[tuple[float, float]]:
        ...

class LinkLabel(QGraphicsItem):
    def __init__(self, 
            self_link: LinkItemData,
            label_props: list[list['LabelProps']],
            get_model_data_fn
        ) -> None:

        super().__init__()

        self.link = self_link
        self.label_props = label_props
        self.get_model_data = get_model_data_fn
        
        self.line = \
               QLineF(self.link.pts[0][0], self.link.pts[0][1],
                      self.link.pts[1][0], self.link.pts[1][1])

        self.angle = self.line.angle()
        
        self.flip = (self.angle > 90) and (self.angle <= 270)

        if self.flip:
             self.setRotation(-self.angle - 180)
        else:
            self.setRotation(-self.angle)

        self.text_grid: list[list[LabelText]] = []

        # How many columns and rows of text?
        self.n_cols = len(self.label_props)
        self.n_rows = len(self.label_props[0])

        self.col_max_char = []

        for col in range(self.n_cols):
            self.text_grid.append([])
            self.col_max_char.append(0)
        
        # Add text items
        for col in range(self.n_cols):
            for row in range(self.n_rows):
                text_props = self.label_props[col][row]
                new_text = LabelText(
                    parent=self, 
                    text="0", 
                    flip_text=False,
                    key=self.link.key,
                    properties=text_props,
                    obj_type="LINK")
                
                self.text_grid[col].append(new_text)

        self.height = SCALE_VALUE * self.n_rows
        self.update_text()
        # self.setRotation(-self.angle)
        self.setFlag(QGraphicsItem.ItemIsMovable)


    def connect_txt_signals(self, show_dialog_fn, make_new_selection_fn):
        for col in range(self.n_cols):
            for row in range(self.n_rows):
                # filter based on what the text is showing (assigned volume, target volume, etc)
                txt = self.text_grid[col][row]
                if not txt.props.editable:
                    continue

                txt.signals.click.connect(show_dialog_fn)
                txt.signals.click.connect(make_new_selection_fn)

    def update_text(self):
        self._reset_max_char()

        for col in range(self.n_cols):
            for row in range(self.n_rows):
                txt = self.text_grid[col][row]
                data = self.get_model_data(txt.key, txt.props.data_name)
                new_text = txt.update_text(data)
                self.col_max_char[col] = max(len(new_text), self.col_max_char[col])

        self._update_text_pos()

        self.width = 0
        for col in range(self.n_cols):
            self.width += self.col_max_char[col]

        self.width = (self.width + self.n_cols) * CHAR_WIDTH

    def _reset_max_char(self):
        for i in range(len(self.col_max_char)):
            self.col_max_char[i] = 0

    def _update_text_pos(self):        
        prev_col_x_pos = 0

        for col in range(self.n_cols):
            x_pos = prev_col_x_pos
            for row in range(self.n_rows):
                label = self.text_grid[col][row]
                text_len = len(label.text) * CHAR_WIDTH
                txt_offset = self.col_max_char[col] * CHAR_WIDTH - text_len
                
                label.setPos(x_pos + txt_offset, row * SCALE_VALUE)

            prev_col_x_pos = x_pos + (self.col_max_char[col] * CHAR_WIDTH) + CHAR_WIDTH

    def get_offset(self):
        unit_normal = self.line.normalVector().unitVector()
        
        center_pt = self.line.center()
        offset_pt = QPointF(center_pt.x() - self.line.p1().x(),
                            center_pt.y() - self.line.p1().y())
        
        unit_normal.translate(offset_pt)

        if self.flip:
            unit_normal.setLength(20)
        else:
            unit_normal.setLength(20 + self.height)

        return unit_normal.p2()

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height)

    def paint(self, painter, option, widget) -> None:
        # # Draw Bounding Rect for debugging
        # brush = QBrush(QColor(240, 240, 0))
        # painter.setBrush(brush)
        if self.flip:
            pen = QPen(QColor(255, 0, 0))
        else:
            pen = QPen(QColor(0, 255, 0))
        
        painter.setPen(pen)
        painter.drawRect(self.boundingRect())
        painter.drawEllipse(0,0,3,3)
