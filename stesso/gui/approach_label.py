from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtCore import QRectF, QPointF, QLineF
from PySide2.QtGui import QColor, QPen

from .approach_tmarrow import TMArrow
from .label_text import LabelText

from typing import Protocol, TYPE_CHECKING

if TYPE_CHECKING:
    from label_props import LabelProps
    from PySide2.QtWidgets import QGraphicsSceneMouseEvent

from gui.settings import GUIConfig


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
        self.lod = 1
        self.mouse_down = False
        self.init_pt = QPointF(self.link.pts[1][0], 
                                self.link.pts[1][1])
        self.offset_length = 20

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
                'row': 0,
                'angle_rel': angle_rel, 
                'angle': outbound_line.angle(),
                'approach_line': self.approach_line,
                'outbound_line': outbound_line,
                'tm_arrow': None
                }

        # Sort turns by angle relative to self
        self.turns = dict(sorted(self.turns.items(), key=lambda item: item[1]['angle_rel']))

        # Add text items and turn arrows for each turn
        for row, (turn_key, t) in enumerate(self.turns.items()):
            t['row'] = row

            new_tm_arrow = TMArrow(self, self.angle, t['angle'], t['angle_rel'])
            new_tm_arrow.setPos(0, row * GUIConfig.FONT_HEIGHT)
            t['tm_arrow'] = new_tm_arrow

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
        self.height = GUIConfig.FONT_HEIGHT * self.n_rows
        self.width = 120
        self.setRotation(-self.angle)
        self.init_pos()

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

        self.width = (self.width + self.n_cols) * GUIConfig.CHAR_WIDTH + GUIConfig.FONT_HEIGHT

    def _reset_max_char(self):
        for i in range(len(self.col_max_char)):
            self.col_max_char[i] = 0

    def _update_text_pos(self, lod:float=1):
        prev_col_x_pos = GUIConfig.FONT_HEIGHT

        if self.flip:
            prev_col_x_pos = GUIConfig.FONT_HEIGHT

        for col in range(self.n_cols):
            x_pos = prev_col_x_pos
            for row in range(self.n_rows):
                txt = self.text_grid[col][row]
                if self.flip:
                    txt_offset = 0
                else:
                    txt_offset = (self.col_max_char[col] * GUIConfig.CHAR_WIDTH) - (len(txt.text) * GUIConfig.CHAR_WIDTH)
                    
                txt.setPos((x_pos + txt_offset) / lod, 
                           row * GUIConfig.FONT_HEIGHT / lod)

            prev_col_x_pos = x_pos + (self.col_max_char[col] * GUIConfig.CHAR_WIDTH) + GUIConfig.CHAR_WIDTH

        for turn_key, t in self.turns.items():
            t['tm_arrow'].setPos(0, t['row'] * GUIConfig.FONT_HEIGHT / lod)
    
    def update_self_pos(self):
        self.offset.setLength(self.offset_length / self.lod)
        self.setPos(self.offset.p2())
    
    def update_offset(self):
        print(f"update_offset self.pos: {self.pos()}")
        self.offset = QLineF(self.init_pt, self.pos())
        self.offset_length = self.offset.length() * self.lod

    def init_pos(self):
        self.offset: QLineF = self.approach_line.unitVector()
        self.offset.setLength(self.offset_length)
        
        self.offset.translate(
            QPointF(self.offset.p2().x() - self.offset.p1().x(),
                    self.offset.p2().y() - self.offset.p1().y()))

        self.offset = self.offset.normalVector()
        self.offset.setAngle(self.offset.angle() + 180)
        self.offset.setP1(self.approach_line.p1())
        self.offset_length = self.offset.length()

        # self.offset.setLength(25)
        # self.offset_length = 25

        self.setPos(self.offset.p2())

    def boundingRect(self):
        return QRectF(-10 / self.lod, 
                      -10  / self.lod, 
                      self.width / self.lod,
                      (self.height + 20) / self.lod)

    def paint(self, painter, option, widget) -> None:
        if not self.mouse_down:
            self.update_self_pos()
        
        self.lod = option.levelOfDetailFromTransform(painter.worldTransform())
        self._update_text_pos(self.lod)

        #print(f"paint: {self.lod}")
        # if self.flip:
        #     # # Draw Bounding Rect for debugging
        #     # brush = QBrush(QColor(240, 240, 240))
        #     # painter.setBrush(brush)
        #     pen = QPen(QColor(255, 0, 0))
        #     pen.setCosmetic(True)
        #     painter.setPen(pen)
        #     painter.drawRect(self.boundingRect())
        #     # painter.drawEllipse(0,0,3,3)

    def mousePressEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.mouse_down = True
        #print(f"Mouse Down self.pos: {self.pos()}")
        return super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event: 'QGraphicsSceneMouseEvent') -> None:
        self.mouse_down = False
        self.update_offset()

        #print(f"Mouse Up self.pos: {self.pos()}")
        return super().mouseReleaseEvent(event)
