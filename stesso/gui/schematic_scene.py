from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide2.QtCore import Slot
from .schematic_items import LinkItem, NodeItem

from typing import TYPE_CHECKING, Protocol, Callable

from .approach_label import ApproachLabel
from .approach_tmhint import TMHint

from .link_label import LinkLabel


if TYPE_CHECKING:
    import PySide2.QtWidgets
    from .label_text import LabelText
    from label_props import LabelProps

class NodeData(Protocol):
    @property
    def name(self) -> str:
        ...
    @property
    def x(self) -> float:
        ...
    @property
    def y(self) -> float:
        ...

class LinkData(Protocol):
    @property
    def key(self) -> tuple[int, int]:
        ...
    @property
    def shape_points(self) -> list[tuple[float, float]]:
        ...

class TurnLabelData(Protocol):
    """Data required for turning movement labels."""
    @property
    def key(self) -> tuple[int, int, int]:
        ...

class ApproachLabelData(Protocol):
    """Group of TurnLabelData for a node approach."""
    @property
    def link_key(self) -> tuple[int, int]:
        ...
    @property
    def turns(self) -> list[TurnLabelData]:
        ...

class NodeApproachLabelData(Protocol):
    """Group of ApproachLabelData for a node."""
    @property
    def key(self) -> int:
        ...
    @property
    def approaches(self) -> list['ApproachLabelData']:
        ...

class SchematicScene(QGraphicsScene):
    """QGraphicsScene for displaying the network.

    Attributes
    ----------
    links : dict[tuple[int, int], LinkItem]
        Stores a LinkItem for each link in the network.
        Keyed by: (start node id, end node id)
    routes: Dict
        Stores the nodes along each route.
        Keyed by: (route.origin, route.destination, route.name) 
    """
    
    def __init__(self):
        super().__init__()
        self.links: dict[tuple[int, int], LinkItem] = {}
        self.get_turn_text_fn: Callable[[tuple[int, int, int], str], str] = None
        self.approach_labels: list[ApproachLabel] = []
        self.link_labels: list[LinkLabel] = []
        self.tm_hints: dict[tuple[int, int, int], TMHint] = {}
        self.label_selection_set: set['LabelText'] = set([])

    def load_network(self, nodes: list[NodeData], links: list[LinkData]):
        """Transfer network node and link data from the Model to the SchematicScene. 

        Parameters
        ----------
        nodes : list[NodeData]
            List of basic data for each node: x, y, name.
        links : List[LinkData]
            List of basic data for each link: key, list of points
        """

        for link in links:
            new_link_item = LinkItem(key=link.key, pts=link.shape_points)
            self.links[link.key] = new_link_item
            self.addItem(new_link_item)

        for node in nodes:
            self.addItem(NodeItem(node.x, node.y, node.name))
        
    def init_labels(self, 
                    link_label_visibility,
                    approaches_to_label: list[NodeApproachLabelData], 
                    approach_label_props: list[list['LabelProps']], 
                    get_node_text_fn,
                    link_label_props,
                    get_link_text_fn) -> None:
        """
        Make node and link labels.

        nodes_to_label : list[NodeApproachLabelData]
            List of data needed to make turning movement labels at each node.
        """
        self._create_link_labels(link_label_visibility, link_label_props, get_link_text_fn)
        self._create_approach_labels(approaches_to_label, approach_label_props, get_node_text_fn)

    def _create_link_labels(self, label_visibility, label_props, get_data_fn) -> None:
        for key, link in self.links.items():
            is_visible = label_visibility[key]
            new_link_label = LinkLabel(link, is_visible, label_props, get_data_fn)
            self.addItem(new_link_label)
            #new_link_label.setPos(new_link_label.get_offset())
            # new_link_label.init_pos()
            self.link_labels.append(new_link_label)

    def _create_approach_labels(self, 
                            node_list: list[NodeApproachLabelData], 
                            label_props: list[list['LabelProps']],
                            get_data_fn) -> None:
        for node in node_list:            
            for approach in node.approaches:
                lbl = self._create_approach_label(node.key, approach, label_props, get_data_fn)
                self.approach_labels.append(lbl)
                self.addItem(lbl)

                # Add Turn Hints
                for (turn_key, t) in lbl.turns.items():
                    tm_hint = TMHint(t['approach_line'], t['outbound_line'])
                    self.tm_hints[turn_key] = tm_hint
                    self.addItem(tm_hint)

                # For Debug
                # self.addEllipse(lbl.pos().x(), lbl.pos().y(), 5, 5)

    def _create_approach_label(self, 
                               node_key: int, 
                               approach: 'ApproachLabelData', 
                               label_props,
                               get_data_fn) -> ApproachLabel:
 
        approach_link = self.links[approach.link_key]
        approach_turns = approach.turns
        outbound_links: list[LinkItem] = []

        for turn in approach_turns:
            link_out_key = (node_key, turn.key[2])
            outbound_links.append(self.links[link_out_key])
    
        ap_label = ApproachLabel(
            self_link=approach_link,
            outbound_links=outbound_links,
            label_props=label_props,
            get_model_data_fn=get_data_fn)

        ap_label.setFlag(QGraphicsItem.ItemIsMovable)
        return ap_label
    
    def hide_approach_labels(self) -> None:
        for lbl in self.approach_labels:
            lbl.setVisible(False)

    def show_approach_labels(self) -> None:
        for lbl in self.approach_labels:
            lbl.setVisible(True)

    def update_approach_labels(self) -> None:
        for lbl in self.approach_labels:
            lbl.update_text()

    def update_link_labels(self) -> None:
        for lbl in self.link_labels:
            lbl.update_text()

    def clear_label_selection(self):
        for label in self.label_selection_set:
            label.selected = False
            if label.obj_type == "TURN":
                self.tm_hints[label.key].selected = False
        self.label_selection_set.clear()


    def new_label_selection(self, key: tuple, selected: bool, text_props, obj_type, label):
        print(f"new_label_selection() {key} {selected}")

        if selected:
            self.clear_label_selection()
            self.label_selection_set.add(label)
        else:
            self.label_selection_set.discard(label)

        if obj_type == "TURN":
            self.tm_hints[key].selected = selected
        

    def connect_txt_signals(self, show_dialog_fn: Callable):
        """Connect approach text signal to the input dialog slot.
        
        Call this function from the MainWindow.
        """
        for lbl in self.approach_labels:
            lbl.connect_txt_signals(show_dialog_fn, self.new_label_selection)

        for lbl in self.link_labels:
            lbl.connect_txt_signals(show_dialog_fn, self.new_label_selection)

    def get_selected_text(self) -> list['LabelText']:
        return list(self.label_selection_set)

    def mousePressEvent(self, event: 'PySide2.QtWidgets.QGraphicsSceneMouseEvent') -> None:
        return super().mousePressEvent(event)
