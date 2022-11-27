from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .net import NetLinkData

@dataclass
class NodeParameters():
    """Parameters needed for constructing a NetNode object.
    """
    __slots__ = ['name', 'x', 'y', 'is_origin', 'is_destination']
    name: str
    x: float
    y: float
    is_origin: bool
    is_destination: bool


class NetNode():
    """A point (junction) in the network graph.

    Two connected nodes form an link. A sequence of three nodes forms a 
    Turn (see TurnData).

    Attributes
    ----------
    key : int
        Unique identifier for the node.
    name : str
        Name, or label, for the node.
    x : float
        x-coordinate of node. Defaults to zero.
    y : float
        y-coordinate of node. Defaults to zero.
    is_origin : bool
        Indicates if traffic can start their trip from this node (source node)
    is_destination : bool
        Indicates if traffic can end their trip at this node (sink node)
    neighbors : Dict[int, NetLinkData]
        Adjacency list of connected downstream node IDs and associated data
    up_neighbors : list
        Upstream node IDs connected to this node.
    """
    def __init__(self, key, parameters: NodeParameters):
        """Create a node in the network graph.

        Parameters
        ----------
        key : int
            Unique identifier.
        parameters : NodeParameters
            Data about the node. Name, x,y coordinates, etc.
        """
        self.key = key
        
        self.name = parameters.name
        self.x = parameters.x
        self.y = parameters.y
        self.is_origin = parameters.is_origin
        self.is_destination = parameters.is_destination

        self.neighbors: dict[int, NetLinkData] = {}
        self.up_neighbors = []

    def add_neighbor(self, neighbor, link_data) -> None:
        """Connects two nodes to form an link.

        links are stored as an adjacency list.

        Parameters
        ----------
        neighbor : int
            Unique identifier of neighboring (connecting) node.
        link_data : NetLinkData
            See NetLinkData class.
        """
        self.neighbors[neighbor] = link_data

    def get_connections(self):
        """Return list of node keys connected to self node."""
        return self.neighbors.keys()