"""Model component of the Model-View-Controller (MVC) design pattern for Stesso.
"""

import os
from dataclasses import dataclass


from network import net_read, net_write
from balancer import balancer


# @dataclass
# class RouteInfo:
#     """Basic OD information for a route."""
#     origin: int
#     destination: int
#     o_name: str
#     d_name: str
#     name: str
#     nodes: List


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

    def get_node_xy(self):
        """Return xy coordinates for each node."""
        if not self.net:
            return
        
        return {i: (node.x, node.y, node.name) for i, node in self.net.nodes(True)}

    def get_link_end_ids(self):
        """Return node ids for the start and end of each link."""
        if not self.net:
            return
        
        return [(i, j, self.net.link(i, j).shape_points) for (i, j), _ in self.net.links(True)]

    def get_nodes_to_label(self):
        # TODO: WIP: returning one test node for now.
        
        nodes_to_label = []
        j, node = self.net.get_node_by_name('102')
        inbound_links = self.net.get_approach_links(j)
        outbound_links = self.net.get_outbound_links(j)

        # TODO: handle case when inbound_links is empty
        label_list = []
        for link in inbound_links:            
            i = link[0]
            turns = []
            for (_, k) in outbound_links:
                if i == k: continue
                test_turn = self.net.turn(i, j, k)
                if test_turn is None: continue
                turns.append(test_turn)

            label_list.append((link, turns))

        nodes_to_label.append((j, label_list))
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
