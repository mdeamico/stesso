from PySide2.QtWidgets import (
    QMainWindow, 
    QAbstractItemView, 
    QDialogButtonBox)

from PySide2.QtGui import QPainter, QFont, QFontMetrics
from PySide2.QtCore import Qt

from gui.ui_mainwindow import Ui_MainWindow

from gui import schematic_scene
from gui.dialog_open import DialogOpen
# from gui.dialog_export import DialogExport


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model

class MainWindow(QMainWindow):
    """Main window presented to the user when the program first starts."""
    def __init__(self, model: 'Model'):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Connect MainWindow view/controller to model
        self.model = model

        # Dialog Open
        self.dialog_open = DialogOpen()
        self.dialog_open.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.load)

    #     # Dialog Export
    #     self.dialog_export = DialogExport(
    #         cb_export_links_and_turns_by_od=self.model.export_node_sequence,
    #         cb_export_routes=self.model.export_route_list,
    #         cb_export_turns=self.model.export_turns
    #     )

    #     # Dialog ODME
    #     self.dialog_odme = DialogODME(cb_odme=self.estimate_od)

        # Connect push buttons to slot functions
        self.ui.pbShowDialogOpen.clicked.connect(self.show_dialog_open)
        # self.ui.pbShowExportDialog.clicked.connect(self.show_dialog_export)
        self.ui.pbBalance.clicked.connect(self.balance_volumes)


    #     # Disable buttons that should only be used after loading a network
    #     self.ui.pbShowExportDialog.setEnabled(False)
    #     self.ui.pbShowODEstimation.setEnabled(False)

        # Setup graphics view
        self.schematic_scene = schematic_scene.SchematicScene()
        self.ui.gvSchematic.setScene(self.schematic_scene)
        self.ui.gvSchematic.setRenderHints(QPainter.Antialiasing)
        
        # Experimenting with font properties
        font = QFont("consolas", 14)
        fm = QFontMetrics(font)
        print(f"fm.height = {fm.height()}")
        print(f"fm.averageCharWidth = {fm.averageCharWidth()}")
        print(f"fm.horizontalAdvance(1234) = {fm.horizontalAdvance('1234')}")
        
        
    def show_dialog_open(self) -> None:
        self.dialog_open.store_data()
        self.dialog_open.show()

    # def show_dialog_export(self) -> None:
    #     self.dialog_export.show()



    def load(self) -> None:
        """Load nodes, links, etc from user inputs."""
    
        file_paths = self.dialog_open.get_data()
        
        load_successful = \
            self.model.load(node_file=file_paths.nodes,
                            links_file=file_paths.links,
                            turns_file=file_paths.turns)

        if not load_successful:
            print("Loading not successful")
            return
        
        self.schematic_scene.load_network(self.model.get_nodes(), 
                                          self.model.get_links(),
                                          self.model.get_nodes_to_label(),
                                          self.model.get_turn_text)

        # Set scene rectangle to something larger than the network.
        # This helps with panning & zooming near the edges of the network.
        init_rect = self.schematic_scene.sceneRect()
        self.schematic_scene.setSceneRect(
            init_rect.x() - init_rect.width(),
            init_rect.y() - init_rect.height(),
            init_rect.width() * 3,
            init_rect.height() * 3)

        self.ui.gvSchematic.fitInView(init_rect, Qt.KeepAspectRatio)

        # Flip y coordinates to make y coordinates increasing from bottom to top.
        self.ui.gvSchematic.scale(1, -1)




        # routes = self.model.get_route_list()
        # self.od_table_model = od_tablemodel.ODTableModel(routes)
        # self.ui.tblOD.setModel(self.od_table_model)
        # self.ui.tblOD.selectionModel().selectionChanged.connect(self.on_od_table_selection)

        # self.schematic_scene.load_routes(routes)

    #         self.ui.pbShowExportDialog.setEnabled(True)
    #         self.ui.pbShowODEstimation.setEnabled(True)
    
    def balance_volumes(self):
        self.model.balance_volumes()
        self.schematic_scene.update_approach_labels()

