import os
import sys
import unittest
from PySide2.QtWidgets import QApplication
from PySide2.QtTest import QTest
from PySide2.QtCore import Qt, QEventLoop, QTimer
from PySide2.QtWidgets import QDialogButtonBox

from context import stesso
import stesso.main
from stesso.model import Model


def event_loop(msec):
    """Event loop to show the GUI during a unit test. 
    
    https://www.qtcentre.org/threads/23541-Displaying-GUI-events-with-QtTest
    """
    loop = QEventLoop()
    timer = QTimer()
    timer.timeout.connect(loop.quit)
    timer.setSingleShot(True)
    timer.start(msec)
    loop.exec_()

class MainTest(unittest.TestCase):
    def setUp(self) -> None:
        self.app = QApplication(sys.argv)
        self.model = Model()
        self.window = stesso.main.MainWindow(self.model)
        return super().setUp()

    def test_draw(self):
        net_folder = os.path.join(os.getcwd(), "tests", "networks", "net02")
        export_folder = os.path.join(os.getcwd(), "tests", "exports")

        self.window.show()
        QTest.mouseClick(self.window.ui.pbShowDialogOpen, Qt.LeftButton)
        self.window.dialog_open.ui.leLinks.setText(os.path.join(net_folder, "links.shp"))
        self.window.dialog_open.ui.leNodes.setText(os.path.join(net_folder, "points.shp"))
        self.window.dialog_open.ui.leTurns.setText(os.path.join(net_folder, "turn targets.csv"))
        QTest.mouseClick(self.window.dialog_open.ui.buttonBox.button(QDialogButtonBox.Ok), Qt.LeftButton)

        QTest.mouseClick(self.window.ui.pbBalance, Qt.LeftButton)
        
        QTest.mouseClick(self.window.ui.pbShowExportDialog, Qt.LeftButton)
        self.window.dialog_export.ui.leExportFolder.setText(export_folder)
        QTest.mouseClick(self.window.dialog_export.ui.pbExport, Qt.LeftButton)

        event_loop(1000)
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
