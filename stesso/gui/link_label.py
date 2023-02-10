from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtCore import Qt, QRectF, QPointF, QLineF, Slot
from PySide2.QtGui import QBrush, QColor, QFont, QPen

from .link_label_text import LinkLabelText

from typing import Protocol, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .textinfo import TextInfo

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
            text_info_grid: list[list['TextInfo']]
        ) -> None:

        super().__init__()

        self.link = self_link
        self.text_info_grid = text_info_grid
        
        self.line = \
               QLineF(self.link.pts[0][0], self.link.pts[0][1],
                      self.link.pts[1][0], self.link.pts[1][1])

        self.angle = self.line.angle()
        
        self.flip = (self.angle > 90) and (self.angle <= 270)

        if self.flip:
             self.setRotation(-self.angle - 180)
        else:
            self.setRotation(-self.angle)

        self.text_grid: list[list[LinkLabelText]] = []

        # How many columns and rows of text?
        self.n_cols = len(self.text_info_grid)
        self.n_rows = len(self.text_info_grid[0])

        self.col_max_char = []

        for col in range(self.n_cols):
            self.text_grid.append([])
            self.col_max_char.append(0)
        
        # Add text items
        for col in range(self.n_cols):
            for row in range(self.n_rows):
                text_info = self.text_info_grid[col][row]
                new_text = LinkLabelText(
                    parent=self, 
                    text="0", 
                    flip_text=False,
                    key=self.link.key,
                    text_info=text_info)
                
                self.text_grid[col].append(new_text)

        self.height = SCALE_VALUE * self.n_rows
        self.update_text()
        # self.setRotation(-self.angle)
        self.setFlag(QGraphicsItem.ItemIsMovable)


    # @Slot(tuple, bool)
    # def test_signal(self, key, selected):
    #     print(f"slot from approach_label: {key} {selected}")
    #     # self.show_input_dialog_fn(key, selected)

    # def connect_txt_signals(self, show_dialog_fn, show_tm_hint_fn):
    #     for col in self.text_columns:
    #         # filter based on what the text is showing (assigned volume, target volume, etc)
    #         if col['info'] != "assigned_volume":
    #             continue
    #         for txt in col['rows']:
    #             txt.is_selectable = True
    #             txt.signals.is_selected.connect(show_dialog_fn)
    #             txt.signals.is_selected.connect(show_tm_hint_fn)

    #             # For Debugging
    #             txt.signals.is_selected.connect(self.test_signal)
    
    # def get_text_items(self) -> list[LabelText]:
    #     items = []
    #     for col in self.text_columns:
    #         # filter based on what the text is showing (assigned volume, target volume, etc)
    #         if col['info'] != "assigned_volume":
    #             continue
    #         for txt in col['rows']:
    #             items.append(txt)
        
    #     return items

    # def get_selected_text(self):
    #     selected = []
    #     for col in self.text_columns:
    #         for txt in col['rows']:
    #             if txt._debug_clicked:
    #                 selected.append(txt.key)
    #     return selected

    def update_text(self):
        self._reset_max_char()

        for col in range(self.n_cols):
            for row in range(self.n_rows):
                new_text = self.text_grid[col][row].update_message()
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

    # def mousePressEvent(self, event) -> None:
    #     return super().mousePressEvent(event)

    # def mouseReleaseEvent(self, event) -> None:
    #     return super().mouseReleaseEvent(event)
