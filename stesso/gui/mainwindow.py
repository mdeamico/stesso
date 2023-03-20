from PySide2.QtWidgets import (
    QMainWindow, 
    QDialogButtonBox)

from PySide2.QtGui import QPainter, QFont, QFontMetrics
from PySide2.QtCore import Qt

from gui.ui_mainwindow import Ui_MainWindow

from gui import schematic_scene
from gui.dialog_open import DialogOpen
from gui.dialog_export import DialogExport
from gui.dialog_vol_input import DialogVolInput
from gui import label_props

from gui import settings

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..model import Model
    from gui.label_text import LabelText
    

class MainWindow(QMainWindow):
    """Main window presented to the user when the program first starts."""
    def __init__(self, model: 'Model'):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.statusbar.showMessage("Hello from Status Bar!", 10000)

        settings.init()

        # Connect MainWindow view/controller to model
        self.model: 'Model' = model

        # Volume Input Dialog
        self.input_dialog = DialogVolInput(self)
        self.input_dialog.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.set_text)
        self.input_dialog.ui.buttonBox.button(QDialogButtonBox.Cancel).clicked.connect(self.clear_label_selection)

        # Dialog Open
        self.dialog_open = DialogOpen()
        self.dialog_open.ui.buttonBox.button(QDialogButtonBox.Ok).clicked.connect(self.load)

        # Dialog Export
        self.dialog_export = DialogExport(cb_export=self.export)

        # Connect push buttons to slot functions
        self.ui.pbShowDialogOpen.clicked.connect(self.show_dialog_open)
        self.ui.pbShowExportDialog.clicked.connect(self.show_dialog_export)
        self.ui.pbBalance.clicked.connect(self.balance_volumes)

    #     # Disable buttons that should only be used after loading a network
    #     self.ui.pbShowExportDialog.setEnabled(False)

        # Setup graphics view
        self.schematic_scene: schematic_scene.SchematicScene = schematic_scene.SchematicScene()
        self.ui.gvSchematic.setScene(self.schematic_scene)
        self.ui.gvSchematic.setRenderHints(QPainter.Antialiasing)
        self.ui.gvSchematic.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Experimenting with font properties
        # font = QFont("consolas", 8)
        # fm = QFontMetrics(font)
        # print(f"fm.height = {fm.height()} fm.capHeight = {fm.capHeight()}")
        # print(f"fm.averageCharWidth = {fm.averageCharWidth()}")
        # print(f"fm.horizontalAdvance(1234) = {fm.horizontalAdvance('1234')}")

    def clear_label_selection(self):
        self.schematic_scene.clear_label_selection()

    def set_text(self):
        """Function for when OK is pressed on the text input dialog."""
        text_list = self.schematic_scene.get_selected_text()
        
        user_input = int(self.input_dialog.ui.lineEdit.text())

        for obj in text_list:
            if obj.obj_type == "LINK":
                self.model.set_link_target_volume(obj.key, obj.props.data_name, user_input)
            elif obj.obj_type == "TURN":
                self.model.set_turn_volume(obj.key, obj.props.data_name, user_input)
        
        print(f"set_text() called: text_list: {text_list} user_input: {user_input}")
        self.schematic_scene.update_approach_labels()
        self.schematic_scene.update_link_labels()
        self.clear_label_selection()


    def show_input_dialog(self, key: tuple, selected: bool, label_props: 'label_props.LabelProps', obj_type: str, label: 'LabelText') -> None:
        
        if label.obj_type == "LINK":
            get_data_fn = self.model.get_link_data
        elif label.obj_type == "TURN":
            get_data_fn = self.model.get_turn_data

        text = label_props.formatted(get_data_fn(label.key, label.props.data_name))

        self.input_dialog.ui.lineEdit.setText(text)
        self.input_dialog.ui.lineEdit.setPlaceholderText(text)
        
        if self.input_dialog.isVisible():
            self.input_dialog.raise_()
            self.input_dialog.activateWindow()
        else:
            self.input_dialog.show()

        self.input_dialog.ui.lineEdit.setFocus() 
        self.input_dialog.ui.lineEdit.selectAll()
        
    def show_dialog_open(self) -> None:
        self.dialog_open.store_data()
        self.dialog_open.show()

    def show_dialog_export(self) -> None:
        self.dialog_export.show()

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
        
        self.schematic_scene.load_network(
            nodes=self.model.get_nodes(), 
            links=self.model.get_links())

        self.link_label_props = [[label_props.imbalance(), label_props.target_volume(True), label_props.assigned_volume()]]
        self.node_label_props = [[label_props.target_volume()], [label_props.assigned_volume(True)]]

        self.schematic_scene.init_labels(
            approaches_to_label=self.model.get_nodes_for_approach_labeling(),
            link_label_visibility=self.model.get_link_label_visibility(),
            approach_label_props=self.node_label_props,
            get_node_text_fn=self.model.get_turn_data,
            link_label_props=self.link_label_props,
            get_link_text_fn=self.model.get_link_data)
        
        self.schematic_scene.connect_txt_signals(self.show_input_dialog)

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

        # Enable buttons that can be used after the network is loaded
        # self.ui.pbShowExportDialog.setEnabled(True)

    
    def balance_volumes(self):
        self.model.balance_volumes()
        self.schematic_scene.update_approach_labels()
        self.schematic_scene.update_link_labels()


    def export(self, export_folder):
        self.model.export_turns(export_folder)
        self.model.export_links(export_folder)
