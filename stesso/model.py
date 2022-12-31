"""Model component of the Model-View-Controller (MVC) design pattern for Stesso.
"""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from network import net_read, net_write
from balancer import balancer

if TYPE_CHECKING:
    from .network.netnode import NetNode
    from .network.netlink import NetLinkData

# @dataclass
# class RouteInfo:
#     """Basic OD information for a route."""
#     origin: int
#     destination: int
#     o_name: str
#     d_name: str
#     name: str
#     nodes: List

@dataclass
class TurnLabelData:
    """Data required for turning movement labels."""
    key: tuple[int, int, int]

@dataclass
class ApproachLabelData:
    """Group of TurnLabelData for a node approach."""
    link_key: tuple[int, int]
    turns: list[TurnLabelData]

@dataclass
class NodeApproachLabelData:
    """Group of ApproachLabelData for a node."""
    key: int
    approaches: list[ApproachLabelData]


class Model():
    """Contains the network and od data, and methods to operate on them.
    
    These methods are the API for a view/controller to interact with the data.
    """
    # __slots__ = ['net', 'od_seed']

    def __init__(self):
        """Initialize Model with an empty network and empty OD Seed Matrix.
        
        The Model variables are populated via the Model.load() function.
        """

        #: Network: Object containing network graph of nodes and links, as well 
        # as turns and volume targets
        self.net = None
        
    
    def load(self, node_file=None, links_file=None, turns_file=None) -> None:
        """Populate network and od variables with user supplied data.

        Parameters
        ----------
        node_file : str, optional
            File path to Network nodes, by default None.
        links_file : str, optional
            File path to Network links, by default None.
        turns_file : str, optional
            File path to turn targets, by default None.

        Returns
        -------
        bool
            True if load was successful, otherwise False.
        """

        node_file = _clean_file_path(node_file)
        links_file = _clean_file_path(links_file)
        turns_file = _clean_file_path(turns_file)

        if self.net is None:
            if node_file is None or links_file is None:
                # TODO: This case should trigger an alert to the user that
                # their inputs are invalid.
                return False
            
            self.net = net_read.create_network(node_file, links_file)
        
        if self.net is None:
            # can't continue loading turns without a Network
            return False

        if turns_file is not None:
            net_read.import_turns(turns_file, self.net)

        return True

    def balance_volumes(self):
        if self.net is None:
            return

        balancer.balance_volumes(self.net)

    def get_nodes(self) -> list['NetNode']:
        """Return a list of nodes in the network."""
        if not self.net:
            return
        
        return list(self.net.nodes())

    def get_links(self) -> list['NetLinkData']:
        """Return a list of data for each link."""
        if not self.net:
            return
        
        return list(self.net.links())

    def get_turn_text(self, turn_key: tuple[int, int, int], data_name: str) -> str:
        """Return data to display in turning movement labels."""
        turn = self.net.turn(*turn_key)
        
        match data_name:
            case "geh":
                text = str(turn.geh)
            case "target_volume": 
                text = f'{turn.target_volume:.0f}'
            case _:
                text = "NA"
        
        return text

    def get_nodes_to_label(self):
        # TODO: WIP: returning one test node for now.
        
        nodes_to_label: list[NodeApproachLabelData] = []

        j, _ = self.net.get_node_by_name('102')
        inbound_links = self.net.get_approach_links(j)
        outbound_links = self.net.get_outbound_links(j)

        # TODO: handle case when inbound_links is empty
        approach_labels: list[ApproachLabelData] = []

        for link_in in inbound_links:            
            i = link_in.key[0]
            turns: list[TurnLabelData] = []
            for link_out in outbound_links:
                k = link_out.key[1]
                if i == k: continue
                test_turn = self.net.turn(i, j, k)
                if test_turn is None: continue
                turns.append(TurnLabelData(key=test_turn.key))

            approach_labels.append(
                ApproachLabelData(
                    link_key=link_in.key,
                    turns=turns))

        nodes_to_label.append(
            NodeApproachLabelData(
                key=j,
                approaches=approach_labels))
                
        return nodes_to_label


def _clean_file_path(file_path: str) -> str:
    """Check if a file exists and return a valid path, else None."""
    if file_path is None:
        return None

    file_path = file_path.replace('"', '')
    if not os.path.isfile(file_path):
        return None

    return file_path


def _clean_folder_path(folder_path: str) -> str:
    """Check if a folder exists and return a valid path, else None."""
    if folder_path is None:
        return None

    folder_path = folder_path.replace('"', '')
    if not os.path.isdir(folder_path):
        return None

    return folder_path
