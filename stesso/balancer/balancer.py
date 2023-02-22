import numpy as np
from scipy.optimize import lsq_linear as scipy_lsq_linear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.net import Network

def balance_volumes(net: 'Network') -> None:
    """Balance link and turn volumes in the network.
    
    Uses a linear least squares approach to volume balancing. Solves the matrix
    algebra equation Ax = B. A and B matrices are weighted (W) to add priority and 
    enforce constraints. W.Ax = W.B

    Each link and turn in the network is assigned to a column in the A matrix.
    Rows in the A matrix contain flow conservation equations and target volume 
    constraints.

    In the example below, the first row of A demonstrates a flow conservation
    equation where turns (t) #1, #2, #3 must equal the volume of link #6, that is:
        t_1 + t_2 + t_3 - l_6 = 0
    Because this equation must hold true, the corresponding cell in the weight
    matrix is assigned a high weight 999999.

    The second row in the A matrix shows a target volume constraint where turn #1
    should equal 42, i.e. t_1 = 60. The least squares result may or may not be 
    able to accomodate the turn target, so its weight is assigned 1. Higher weight
    could be used to encourage the least squares result to be closer to the target.
    
    EXAMPLE:
    network object type assigned to each column variable: t = turn, l = link

           var type:  t t t t l l  l
              var #:  0 1 2 3 4 5  6
                A = [[0 1 1 1 0 0 -1 ...],     B = [[0],      W = [[999999],
                     [0 1 0 0 0 0  0 ...],          [42],          [1],
                     [...]]                         [...]]         [...]]
     
    """


    # --------------------------------------------------------------------
    # Assign matrix column numbers to each link and turn in the network
    # --------------------------------------------------------------------
    matrix_cols_turns = {}
    matrix_cols_links = {}

    free_col_number = 0

    for (i, j, k), _ in net.turns(True):
        matrix_cols_turns[(i, j, k)] = free_col_number
        free_col_number += 1

    for (i, j), _ in net.links(True):
        matrix_cols_links[(i, j)] = free_col_number
        free_col_number += 1        

    n_variables = len(matrix_cols_turns) + len(matrix_cols_links)
    
    # --------------------------------------------------------------------------
    # Build A matrix in Ax = B equation.  
    # --------------------------------------------------------------------------

    # Determine how many flow conservation equations are needed.
    # Conservation equations are in the form of the following examples:
    #   sum(turns_in) - link_vol = 0
    #   sum(turns_out) - link_vol = 0

    n_flow_eq = 0
    for link in net.links():
        if len(link.turns_in) > 0:
            n_flow_eq += 1
        if len(link.turns_out) > 0:
            n_flow_eq += 1

    # Initialize A matrix with flow conservation equations.
    # Target volume equations are appended to A later.
    A = np.zeros(shape=(n_flow_eq, n_variables))
    
    # Build flow equations one-by-one. Use flow_eq_row to keep track of current row in matrix A.
    flow_eq_row = 0

    def update_matrix_a_flow_eq(link_flows: list, eq_row: int, link_col: int) -> int:
        """Helper function to create link flow conservation equations."""
        for turn in link_flows:
            turn_col = matrix_cols_turns[turn]
            A[eq_row, turn_col] = 1
        
        A[eq_row, link_col] = -1    

    for link_key, link in net.links(True):
        link_col = matrix_cols_links[link_key]

        if len(link.turns_in) > 0:
            update_matrix_a_flow_eq(link.turns_in, flow_eq_row, link_col)
            flow_eq_row += 1

        if len(link.turns_out) > 0:
            update_matrix_a_flow_eq(link.turns_out, flow_eq_row, link_col)
            flow_eq_row += 1


    # ----------------------------------------------------------------
    # - Build B matrix in Ax = B equation, 
    # - Provide solution bounds, and
    # - Build weight matrix W
    # ----------------------------------------------------------------
    B = [0] * A.shape[0]
    
    # Lower and upper bounds on resulting volumes.
    lbounds = [0] * A.shape[1]
    ubounds = [np.inf] * A.shape[1]

    # Weight matrix.
    # Use extremely high weight to force flow conservation equations to hold true.
    # Use lower weights on target volume equations that have flexibility in their reults.
    W = [999999] * A.shape[0]

    # Append equations for target volumes.
    def update_abw_for_target_constraints(target_volume, col):
        """Helper function to update A, B, W matrices, and bounds for target constaints."""
        
        # Allow re-assigning A defined in outer scope.
        nonlocal A

        new_eq = np.array([[0] * A.shape[1]])
        new_eq[0, col] = 1
        
        A = np.concatenate((A, new_eq), axis=0)
        B.append(target_volume)

        lbounds[col] = target_volume * 0.85
        if target_volume == 0:
            ubounds[col] = 0.01
            W.append(999999)
        else:
            ubounds[col] = target_volume * 1.15
            W.append(1)   


    for t, col in matrix_cols_turns.items():
        target_volume = net._turns[t].target_volume
        update_abw_for_target_constraints(target_volume, col)

    for l, col in matrix_cols_links.items():
        target_volume = net.link(l[0], l[1]).target_volume
        if target_volume == 0:
            continue
        update_abw_for_target_constraints(target_volume, col)

    B = np.array(B)
    W = np.diag(W)


    # --------------------------------------
    # Solve Matrix Equation Ax = B
    # --------------------------------------
    result = scipy_lsq_linear(np.dot(W, A), np.dot(W, B), bounds=(lbounds, ubounds))
    final_mat = result.x

    # Show result
    np.set_printoptions(linewidth=200)
    print(result)

    # ----------------------------------------
    # Assign result to network link & turns
    # ----------------------------------------
    for k, v in matrix_cols_links.items():
        net.link(k[0], k[1]).assigned_volume = final_mat[v]
            
    for k, v in matrix_cols_turns.items():
        net._turns[(k[0], k[1], k[2])].assigned_volume = final_mat[v]

    for k, t in net.turns(True):
        print(f"{t.name}: {t.assigned_volume}")

    for (i, j), l in net.links(True):
        print(f"({net.node(i).name}, {net.node(j).name}): {l.assigned_volume}")

    print("done")
