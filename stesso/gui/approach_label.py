from PySide2.QtWidgets import QGraphicsItem
from PySide2.QtGui import QBrush, QColor
from PySide2.QtCore import QRectF, QPointF, QLineF, Slot

from .approach_arrow import TMArrow
from .approach_text import LabelText

from typing import Protocol, Callable

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
            get_turn_text_fn: Callable[[tuple[int, int, int], str], str]
        ) -> None:

        super().__init__()

        self.link = self_link
        self.outbound_links = outbound_links
        self.rows = len(outbound_links)

        # keep track of what is in each column of text      
        self.text_columns = []
        
        # Column 1
        self.text_columns.append({
            'info': 'target_volume', 
            'max_char': 0, 
            'text_prefix': "",  # character to add to start of string, ex "("
            'text_postfix': "", # character to add to end of string, ex ")"
            'rows': []              
        })

        # Column 2
        self.text_columns.append({
            'info': 'assigned_volume', 
            'max_char': 0, 
            'text_prefix': "<",
            'text_postfix': ">",
            'rows': []            
        })

        self.get_turn_text = get_turn_text_fn
    
        # Calculate angle based on self.link
        # Measure angle of line starting from the central intersection node.
        # Example: At intersection A, approach CA angle is measured from A to C
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
        for i in range(0, self.rows):
            outbound_link = self.outbound_links[i]
            outbound_line = \
               QLineF(outbound_link.pts[0][0], outbound_link.pts[0][1],
                      outbound_link.pts[1][0], outbound_link.pts[1][1])

            angle = self.approach_line.angleTo(outbound_line)

            key_k = outbound_link.key[1]
            self.turns[(key_i, key_j, key_k)] = {
                'angle_rel': angle, 
                'angle': outbound_line.angle()
                }

        # Sort turns by angle relative to self
        self.turns = dict(sorted(self.turns.items(), key=lambda item: item[1]['angle_rel']))

        # Add labels and turn arrows for each turn
        for row, (turn_key, t) in enumerate(self.turns.items()):
            t['row'] = row

            new_tm_arrow = TMArrow(self, self.angle, t['angle'], t['angle_rel'])
            new_tm_arrow.setPos(0, row * SCALE_VALUE)

            for col in self.text_columns:
                new_text = LabelText(self, "0", self.flip, turn_key)
                # new_text.signals.is_selected.connect(self.show_edit_dialog)
                col['rows'].append(new_text)

        self.update_text()
        self.height = SCALE_VALUE * self.rows
        self.width = 120
        self.setRotation(-self.angle)

    @Slot(tuple, bool)
    def show_edit_dialog(self, key, selected):
        print(f"slot from approach_label: {key} {selected}")
        self.show_input_dialog_fn(key, selected)

    def connect_txt_signals(self, show_dialog_fn):
        for col in self.text_columns:
            # filter based on what the text is showing (assigned volume, target volume, etc)
            if col['info'] != "assigned_volume":
                continue
            for txt in col['rows']:
                txt.signals.is_selected.connect(show_dialog_fn)

    def get_selected_text(self):
        selected = []
        for col in self.text_columns:
            for txt in col['rows']:
                if txt._debug_clicked:
                    selected.append(txt.key)
        return selected

    def update_text(self):
        self._reset_max_char()

        for row, (turn_key, t) in enumerate(self.turns.items()):
            for col in self.text_columns:
                info = col['info']
                
                turn_text = self.get_turn_text(turn_key, info)
                label_text = f"{col['text_prefix']}{turn_text}{col['text_postfix']}"
                col['max_char'] = max(len(label_text), col['max_char'])

                col['rows'][row].update_message(label_text)

        self._update_text_pos()

        self.width = 0
        for col in self.text_columns:
            self.width += col['max_char']

        self.width = (self.width + len(self.text_columns) + 2) * CHAR_WIDTH + TURN_ARROW_WIDTH

    def _reset_max_char(self):
        for col in self.text_columns:
            col['max_char'] = 0

    def _update_text_pos(self):
        prev_col_x_pos = TURN_ARROW_WIDTH

        if self.flip:
            prev_col_x_pos = SCALE_VALUE

        for col in self.text_columns:
            x_pos = prev_col_x_pos + CHAR_WIDTH
            for row, txt in enumerate(col['rows']):
                
                if self.flip:
                    txt_offset = 0
                else:
                    txt_offset = (col['max_char'] * CHAR_WIDTH) - (len(txt.message) * CHAR_WIDTH)
                    
                txt.setPos(x_pos + txt_offset, row * SCALE_VALUE)

            prev_col_x_pos = x_pos + (col['max_char'] * CHAR_WIDTH)


    def get_offset(self) -> QPointF:
        offset: QLineF = self.approach_line.unitVector()
        offset.setLength(50)
        return offset.p2()
    
    def boundingRect(self):
        return QRectF(-10, -10, self.width, self.height + 20)

    def paint(self, painter, option, widget) -> None:
        pass
        if self.flip:
        # # Draw Bounding Rect for debugging
        # brush = QBrush(QColor(240, 240, 240))
        # painter.setBrush(brush)
            painter.drawRect(self.boundingRect())
        # painter.drawEllipse(0,0,3,3)

    def mousePressEvent(self, event) -> None:
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        return super().mouseReleaseEvent(event)
