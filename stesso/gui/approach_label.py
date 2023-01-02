from PySide2.QtWidgets import QGraphicsItem
# from PySide2.QtGui import QBrush, QPen, QPainter, QPainterPath, QFont, QFontMetrics
from PySide2.QtCore import QRectF, QPointF, QLineF

from .approach_arrow import TMArrow
from .approach_text import LabelText

from typing import Protocol, Callable

SCALE_VALUE = 22


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
                info = col['info']

                turn_text = self.get_turn_text(turn_key, info)

                label_text = f"{col['text_prefix']}{turn_text}{col['text_postfix']}"

                new_label = LabelText(self, label_text, self.flip)
                
                col['max_char'] = max(len(label_text), col['max_char'])
                col['rows'].append(new_label)

        # Set text position
        
        char_width = 10
        #prev_x_pos = SCALE_VALUE - 100
        #prev_x_pos = 0
        #prev_x_pos = (self.text_columns[0]['max_char'] * char_width) - 100 + char_width
        prev_x_pos = -100 + SCALE_VALUE

        prev_max_char = 0
        # self.flip = False
        if self.flip:
            prev_x_pos = SCALE_VALUE

        for col in self.text_columns:
            if self.flip:
                x_pos = prev_x_pos + (prev_max_char * char_width) + char_width
            else:
                x_pos = prev_x_pos + (col['max_char'] * char_width) + char_width

            for row, txt in enumerate(col['rows']):
                txt.setPos(x_pos, row * SCALE_VALUE)

            prev_x_pos = x_pos
            prev_max_char = col['max_char']

        self.height = SCALE_VALUE * self.rows

        self.setRotation(-self.angle)

    def update_text(self):
        for row, (turn_key, t) in enumerate(self.turns.items()):
            for col in self.text_columns:
                info = col['info']
                turn_text = self.get_turn_text(turn_key, info)
                label_text = f"{col['text_prefix']}{turn_text}{col['text_postfix']}"
                col['max_char'] = max(len(label_text), col['max_char'])
                col['rows'][row].update_message(label_text)


    def get_offset(self) -> QPointF:
        offset: QLineF = self.approach_line.unitVector()
        offset.setLength(50)
        return offset.p2()
    
    def boundingRect(self):
        return QRectF(-10, -10, 120, self.height + 20)

    def paint(self, painter, option, widget) -> None:
        # Draw Bounding Rect for debugging
        painter.drawRect(self.boundingRect())
        painter.drawEllipse(0,0,3,3)

    def mousePressEvent(self, event) -> None:
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        return super().mouseReleaseEvent(event)
