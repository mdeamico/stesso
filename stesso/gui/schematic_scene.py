from PySide2.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide2.QtCore import Slot
from .schematic_items import LinkItem, NodeItem

from typing import TYPE_CHECKING, Protocol, Callable

from .approach_label import ApproachLabel
from .approach_tmhint import TMHint

if TYPE_CHECKING:
    import PySide2.QtWidgets    

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
        # self.routes = {}
        self.get_turn_text_fn: Callable[[tuple[int, int, int], str], str] = None
        self.approach_labels: list[ApproachLabel] = []
        self.tm_hints: dict[tuple[int, int, int], TMHint] = {}

    def load_network(
        self, 
        nodes: list[NodeData], 
        links: list[LinkData], 
        node_label_info: list[NodeApproachLabelData],
        get_turn_text_fn: Callable[[tuple[int, int, int], str], str]) -> None:
        """Transfer network node and link data from the Model to the SchematicScene. 

        Parameters
        ----------
        nodes : list[NodeData]
            List of basic data for each node: x, y, name.
        links : List[LinkData]
            List of basic data for each link: key, list of points
        node_label_info : list[NodeApproachLabelData]
            List of data needed to make turning movement labels at each node.
        get_turn_text_fn : Callable[[tuple[int, int, int], str], str])
            Callback function to get the text to display for each turning movement, 
            such as volume, GEH, etc.
        """
        for node in nodes:
            self.addItem(NodeItem(node.x, node.y, node.name))
        
        for link in links:
            new_link_item = LinkItem(key=link.key, pts=link.shape_points)
            self.links[link.key] = new_link_item
            self.addItem(new_link_item)

        self.get_turn_text_fn = get_turn_text_fn

        for node in node_label_info:            
            for approach in node.approaches:
                lbl = self.create_approach_label(node.key, approach)
                self.approach_labels.append(lbl)
                self.addItem(lbl)
                lbl.setPos(lbl.get_offset())

                # Add Turn Hints
                for (turn_key, t) in lbl.turns.items():
                    tm_hint = TMHint(t['approach_line'], t['outbound_line'])
                    self.tm_hints[turn_key] = tm_hint
                    self.addItem(tm_hint)

                # For Debug
                self.addEllipse(lbl.pos().x(), lbl.pos().y(), 5, 5)

        # # FIXME: Need to figure out how to update positions post-init.
        # for ap_label in self.approach_labels:
        #     for hint in ap_label.tm_hints:
        #         hint.update_polygon()
        #         self.addItem(hint)


    def create_approach_label(self, node_key: int, approach: 'ApproachLabelData') -> ApproachLabel:
 
        approach_link = self.links[approach.link_key]
        approach_turns = approach.turns
        outbound_links: list[LinkItem] = []

        for turn in approach_turns:
            link_out_key = (node_key, turn.key[2])
            outbound_links.append(self.links[link_out_key])
    
        ap_label = ApproachLabel(
            self_link=approach_link,
            outbound_links=outbound_links,
            get_turn_text_fn=self.get_turn_text_fn)

        ap_label.setFlag(QGraphicsItem.ItemIsMovable)
        # ap_label.setPos(approach_link.pts[1][0], approach_link.pts[1][1])
        return ap_label
    
    def update_approach_labels(self) -> None:
        for lbl in self.approach_labels:
            lbl.update_text()

    @Slot(tuple, bool)
    def select_tm_hint(self, turn_key: tuple, selected: bool):
        print(f"selected! {turn_key} {selected}")
        self.tm_hints[turn_key].selected = selected

    def connect_txt_signals(self, show_dialog_fn: Callable):
        """Connect approach text signal to the input dialog slot.
        
        Call this function from the MainWindow.
        """
        for lbl in self.approach_labels:
            lbl.connect_txt_signals(show_dialog_fn, self.select_tm_hint)

    def get_selected_text(self) -> list:
        return_list = []
        for lbl in self.approach_labels:
            for txt in lbl.get_selected_text():
                return_list.append(txt)
        return return_list

    # def load_routes(self, routes: List[RouteInfo]) -> None:
    #     """Transfers data about the routes and od from the Model to the SchematicScene.

    #     Parameters
    #     ----------
    #     routes : List[RouteInfo]
    #         Basic info about the route for each OD. 
    #         Includes route origin, destination, route name, and nodes.
    #     """
    #     for route in routes:
    #         self.routes[(route.origin, route.destination, route.name)] = route.nodes

    # def color_route(self, route, is_selected) -> None:
    #     """Sets a bool to indicate if the link is on the user-selected path.

    #     LinkItem objects in the scene can update themselves to be colored based
    #     on the selection bool.

    #     Parameters
    #     ----------
    #     route : Tuple
    #         Route identifier tuple: (route.origin, route.destination, route.name)
    #     is_selected : bool
    #         True if the the link is on the user selected path.
    #     """
    #     for x in range(len(self.routes[route]) - 1):
    #         i = self.routes[route][x]
    #         j = self.routes[route][x + 1]
    #         self.links[(i, j)].is_on_selected_path = is_selected

    def mousePressEvent(self, event: 'PySide2.QtWidgets.QGraphicsSceneMouseEvent') -> None:
        return super().mousePressEvent(event)
