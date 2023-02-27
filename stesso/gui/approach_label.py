from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtCore import QRectF, QPointF, QLineF

from .approach_tmarrow import TMArrow
from .label_text import LabelText

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from label_props import LabelProps

SCALE_VALUE = 22
CHAR_WIDTH = 10
TURN_ARROW_WIDTH = 22


class LinkItemData(Protocol):
    @property
    def key(self) -> tuple[int, int]:
        ...
    @property
    def pts(self) -> list[tuple[float, float]]:
        ...


class ApproachLabel(QGraphicsItem):
    def __init__(self, 
            self_link: LinkItemData,
            outbound_links: list[LinkItemData],
            label_props: list[list['LabelProps']],
            get_model_data_fn
        ) -> None:

        super().__init__()

        self.link = self_link
        self.outbound_links = outbound_links
        self.label_props = label_props
        self.get_model_data = get_model_data_fn

        self.text_grid: list[list[LabelText]] = []

        # How many rows & columns and rows of text?
        self.n_rows = len(outbound_links)
        self.n_cols = len(self.label_props)

        self.col_max_char = []

        for col in range(self.n_cols):
            self.text_grid.append([])
            self.col_max_char.append(0)

        # Calculate angle based on self.link
        # Measure angle of line starting from the central intersection node.
        # Example: At intersection A, approach CA angle is measured from A0 to AC
        #  
        #       C .......
        #        \      . angle
        #         \     .
        #          A ..........0
    
        self.approach_line = \
               QLineF(self.link.pts[1][0], self.link.pts[1][1],
                      self.link.pts[0][0], self.link.pts[0][1])

        self.angle = self.approach_line.angle()
        self.flip = (self.angle > 90) and (self.angle <= 270)

        # Dictionary of turns: {(i, j, k): {'angle': 111, 'row': 1}}
        self.turns = {}  

        key_i = self.link.key[0]
        key_j = self.link.key[1]

        # Determine angle of all turns
        for i in range(0, self.n_rows):
            outbound_link = self.outbound_links[i]
            outbound_line = \
               QLineF(outbound_link.pts[0][0], outbound_link.pts[0][1],
                      outbound_link.pts[1][0], outbound_link.pts[1][1])

            angle_rel = self.approach_line.angleTo(outbound_line)

            key_k = outbound_link.key[1]
            self.turns[(key_i, key_j, key_k)] = {
                'angle_rel': angle_rel, 
                'angle': outbound_line.angle(),
                'approach_line': self.approach_line,
                'outbound_line': outbound_line
                }

        # Sort turns by angle relative to self
        self.turns = dict(sorted(self.turns.items(), key=lambda item: item[1]['angle_rel']))

        # Add text items and turn arrows for each turn
        for row, (turn_key, t) in enumerate(self.turns.items()):
            t['row'] = row

            new_tm_arrow = TMArrow(self, self.angle, t['angle'], t['angle_rel'])
            new_tm_arrow.setPos(0, row * SCALE_VALUE)

            for col in range(self.n_cols):
                text_props = self.label_props[col][0]
                new_text = LabelText(
                    parent=self, 
                    text="0", 
                    flip_text=self.flip,
                    key=turn_key,
                    properties=text_props,
                    obj_type="TURN")
                
                self.text_grid[col].append(new_text)

        self.update_text()
        self.height = SCALE_VALUE * self.n_rows
        self.width = 120
        self.setRotation(-self.angle)

    def connect_txt_signals(self, show_dialog_fn, make_new_selection_fn):
        for col in range(self.n_cols):
            for row in range(self.n_rows):
                # filter based on if the LabelText item is editable
                txt = self.text_grid[col][row]
                if not txt.props.editable:
                    continue

                txt.signals.click.connect(show_dialog_fn)
                txt.signals.click.connect(make_new_selection_fn)

    def update_text(self):
        self._reset_max_char()

        for row, _ in enumerate(self.turns.items()):
            for col in range(self.n_cols):
                txt = self.text_grid[col][row]
                data = self.get_model_data(txt.key, txt.props.data_name)
                new_text = txt.update_text(data)
                self.col_max_char[col] = max(len(new_text), self.col_max_char[col])

        self._update_text_pos()

        self.width = 0
        for col in range(self.n_cols):
            self.width += self.col_max_char[col]

        self.width = (self.width + self.n_cols) * CHAR_WIDTH + TURN_ARROW_WIDTH

    def _reset_max_char(self):
        for i in range(len(self.col_max_char)):
            self.col_max_char[i] = 0

    def _update_text_pos(self):
        prev_col_x_pos = TURN_ARROW_WIDTH

        if self.flip:
            prev_col_x_pos = SCALE_VALUE

        for col in range(self.n_cols):
            x_pos = prev_col_x_pos + CHAR_WIDTH
            for row in range(self.n_rows):
                txt = self.text_grid[col][row]
                if self.flip:
                    txt_offset = 0
                else:
                    txt_offset = (self.col_max_char[col] * CHAR_WIDTH) - (len(txt.text) * CHAR_WIDTH)
                    
                txt.setPos(x_pos + txt_offset, row * SCALE_VALUE)

            prev_col_x_pos = x_pos + (self.col_max_char[col] * CHAR_WIDTH)


    def get_offset(self) -> QPointF:
        offset: QLineF = self.approach_line.unitVector()
        offset.setLength(50)
        return offset.p2()
    
    def boundingRect(self):
        return QRectF(-10, -10, self.width, self.height + 20)

    def paint(self, painter, option, widget) -> None:
        if self.flip:
            # # Draw Bounding Rect for debugging
            # brush = QBrush(QColor(240, 240, 240))
            # painter.setBrush(brush)
            painter.drawRect(self.boundingRect())
            # painter.drawEllipse(0,0,3,3)
