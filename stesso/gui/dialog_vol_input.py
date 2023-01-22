from PySide2.QtWidgets import QDialog
from PySide2.QtCore import Qt, QPoint, QEvent

from gui.ui_dialog_vol_input import Ui_Dialog

class DialogVolInput(QDialog):
    """Volume input dialog
    
    Frameless & Draggable Window
    https://stackoverflow.com/questions/37718329/pyqt5-draggable-frameless-window
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.lineEdit.installEventFilter(self)
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.old_pos = self.pos()

    def mousePressEvent(self, event):
        self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.old_pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_pos = event.globalPos()

    def eventFilter(self, widget, event):
        if (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Tab):
            print("Tab key pressed!!!!")
            return True
        return super().eventFilter(widget, event)
        


    def focusNextPrevChild(self, next: bool) -> bool:
        # Returning False prevents Tab key from switching focus.
        # https://stackoverflow.com/questions/18160051/intercepting-tab-key-press-to-manage-focus-switching-manually
        return False
        # return super().focusNextPrevChild(next)
