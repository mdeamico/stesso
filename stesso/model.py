"""Model component of the Model-View-Controller (MVC) design pattern for Stesso.
"""

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from network import net_read, net_write
from balancer import balancer

if TYPE_CHECKING:
    from .network.netnode import NetNode
    from .network.netlink import NetLinkData

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
            
            # TODO: is this the best spot to make these function calls?
            self.net.init_assigned_turn_vol()
            self.net.calc_link_imbalance()

        return True

    def balance_volumes(self):
        if self.net is None:
            return

        balancer.balance_volumes(self.net)
        # TODO: Calculate imbalance here, or within balance_volumes() ?
        self.net.calc_link_imbalance()

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

    def get_turn_data(self, turn_key: tuple[int, int, int], data_name: str) -> Any:
        turn = self.net.turn(*turn_key)        
        return getattr(turn, data_name, "NA")


    def get_link_data(self, link_key: tuple[int, int], data_name: str) -> Any:
        link = self.net.link(*link_key)
        return getattr(link, data_name, "NA")


    def set_link_target_volume(self, key: tuple, data_name, volume: int) -> None:
        link = self.net.link(*key)
        link.target_volume = volume
        print(f"set link target {key}, {volume}")
        # TODO: what else needs to get updated? GEH?

    def set_turn_volume(self, turn_key: tuple[int, int, int], data_name, volume: int) -> None:
        turn = self.net.turn(*turn_key)
        turn.assigned_volume = volume
        # TODO: what else needs to get updated? GEH?

    def get_nodes_for_approach_labeling(self):
        """Return data needed to label nodes that have more than one upstream or 
        downstream neighbor.
        """
        
        nodes_to_label: list[NodeApproachLabelData] = []

        for node in self.net.nodes():
            count_up = len(node.up_neighbors)
            count_dn = len(node.neighbors)

            if ((count_up == 0) or (count_up == 1)) and (
                (count_dn == 0) or (count_dn == 1)):
               continue

            j = node.key
            inbound_links = self.net.get_approach_links(j)
            outbound_links = self.net.get_outbound_links(j)

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

    def export_turns(self, export_folder=None):
        net_write.export_turns(self.net, export_folder)

    def export_links(self, export_folder=None):
        net_write.export_links(self.net, export_folder)        


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
