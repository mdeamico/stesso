from PySide2.QtWidgets import QGraphicsView, QStyleOptionGraphicsItem
import PySide2.QtCore

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import PySide2.QtGui


class SchematicView(QGraphicsView):
    def __init__(self, parent = None):
        super().__init__()
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.prev_scale = self.transform().m11()
        self.vis_threshold_for_approach_label = 8
    
    def set_vis_threshold(self, value):
        self.vis_threshold_for_approach_label = value
        self.set_prev_scale()
        print(f"set_vis... {self.vis_threshold_for_approach_label}")

    def set_prev_scale(self):
        self.prev_scale = self.transform().m11()
        print(f"in set_prev_scale: {self.prev_scale}")
        lod = QStyleOptionGraphicsItem.levelOfDetailFromTransform(self.transform())
        if self.prev_scale < self.vis_threshold_for_approach_label:
            self.scene().hide_approach_labels(lod)
            print("change vis")
        elif self.prev_scale >= self.vis_threshold_for_approach_label:
            self.scene().show_approach_labels(lod)
            print("change vis")       

    def wheelEvent(self, event: 'PySide2.QtGui.QWheelEvent') -> None:

        # Zoom to point under mouse cursor.
        # https://stackoverflow.com/questions/58965209/zoom-on-mouse-position-qgraphicsview
        # https://stackoverflow.com/questions/19113532/qgraphicsview-zooming-in-and-out-under-mouse-position-using-mouse-wheel

        # self.fitInView(PySide2.QtCore.QRectF(27406.520785, 8102.370929, 89.298811, 42.243853))
        lod = QStyleOptionGraphicsItem.levelOfDetailFromTransform(self.transform())
        # print(f"wheelEvent: (m11, m22) = ({self.transform().m11()} {self.transform().m22()}) {lod}")

        # self.scene().show_approach_labels(QStyleOptionGraphicsItem.levelOfDetailFromTransform(self.transform()))

        # self.scene().update()
        # self.update()        
        
        # return super().wheelEvent(event)

        previous_anchor = self.transformationAnchor()
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        zoom_factor = 1.1
        if event.angleDelta().y() <= 0:
            zoom_factor = 1 / zoom_factor
        
        self.scale(zoom_factor, zoom_factor)
        self.setTransformationAnchor(previous_anchor)

        # print(f"view transform m11: {self.transform().m11()} m22: {self.transform().m22()}")
        new_scale = self.transform().m11()
        # scale_delta = new_scale - self.vis_threshold_for_approach_label

        if new_scale < self.vis_threshold_for_approach_label and \
           self.prev_scale >= self.vis_threshold_for_approach_label:
            self.scene().hide_approach_labels(lod)
            print("change vis - hide labels")
        elif new_scale >= self.vis_threshold_for_approach_label and \
             self.prev_scale < self.vis_threshold_for_approach_label:
            
            # self.scene().invalidate(self.scene().sceneRect())
            # self.scene().update()
            # self.update()
            # self.viewport().repaint()

            self.scene().show_approach_labels(lod)
            print("change vis - show labels")

        self.prev_scale = new_scale

        # Do not call the super().wheelEvent(event) method in the return statement.
        # Doing so interferes with the zoom to cursor behavior logic implemented above.
        return

