from PySide2.QtWidgets import QWidget, QFileDialog

from gui.ui_dialog_export import Ui_Dialog



class DialogExport(QWidget):
    """Dialog for exporting list of turns, paths, etc."""
    def __init__(self, cb_export):

        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        
        self.cb_export = cb_export
        self.ui.pbExport.clicked.connect(self.on_pbExport_click)

        self.ui.pbExportFolder.clicked.connect(self.on_pbExportFolder_click)

    def reject(self) -> None:
        """User clicks close."""
        self.close()

    def on_pbExportFolder_click(self) -> None:
        """Open a standard file dialog for selecting the export folder."""
        export_folder = QFileDialog.getExistingDirectory(
            self, "Select Export Folder", 
            "",
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        self.ui.leExportFolder.setText(export_folder)

    def on_pbExport_click(self) -> None:
        self.cb_export(self.ui.leExportFolder.text())
        self.close()