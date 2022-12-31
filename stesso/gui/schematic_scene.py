from PySide2.QtWidgets import QGraphicsScene
from .schematic_items import LinkItem, NodeItem

from typing import TYPE_CHECKING
from typing import List
# from model import RouteInfo

from .approach_label import ApproachLabel, LinkProperties

if TYPE_CHECKING:
    import PySide2.QtWidgets    



class SchematicScene(QGraphicsScene):
    """QGraphicsScene for displaying the network.

    Attributes
    ----------
    links : Dict
        Stores a LinkItem for each link in the network.
        Keyed by: (start node id, end node id)
    routes: Dict
        Stores the nodes along each route.
        Keyed by: (route.origin, route.destination, route.name) 
    """
    
    def __init__(self):
        super().__init__()
        self.links = {}
        self.routes = {}

    def load_network(self, nodes, links, node_label_info) -> None:
        """Transfer network node and link data from the Model to the SchematicScene. 

        Parameters
        ----------
        nodes : Dict
            {i: (x, y, name)} Dict of coordinates for each node.
        links : List
            [(i, j, shape_points), ...] List of start/end node numbers for each link.
        """
        for _, (x, y, name) in nodes.items():
            self.addItem(NodeItem(x, y, name))
        
        for (i, j, pts) in links:
            self.links[(i, j)] = LinkItem(pts)

            self.addItem(self.links[(i, j)])

        for node_key, approaches in node_label_info:
            # print(node)
            # (2, [((1, 2), [TurnData(key=(1, 2, 3), name='1_2_3', seed_volume=0, target_volume=0, assigned_volume=0, geh=0), 
            #                TurnData(key=(1, 2, 4), name='1_2_4', seed_volume=0, target_volume=0, assigned_volume=0, geh=0), 
            #                TurnData(key=(1, 2, 0), name='1_2_0', seed_volume=0, target_volume=0, assigned_volume=0, geh=0)])])
            for approach in approaches:
                self.add_approach_label(node_key, approach)


    def add_approach_label(self, node_key, approach) -> None:

        approach_link = LinkProperties(
            key=approach[0],
            shape_points=self.links[approach[0]].pts)
        
        approach_turns = approach[1]
        
        outbound_links = []
        for turn in approach_turns:
            outbound_links.append(
                LinkProperties(
                    key=(node_key, turn.key[2]),
                    shape_points=self.links[(node_key, turn.key[2])].pts))
    
        ap_label = ApproachLabel(
            self_link=approach_link,
            outbound_links=outbound_links,
            get_turn_data_fn="hello")

        #self.approach_label.setFlag(QGraphicsItem.ItemIsMovable)
        ap_label.setPos(approach_link.shape_points[1][0], approach_link.shape_points[1][1])
        self.addItem(ap_label)
    
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
