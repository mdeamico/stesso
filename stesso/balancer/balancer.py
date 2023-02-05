import numpy as np
from scipy.optimize import lsq_linear as scipy_lsq_linear

from .flows import Flows

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..network.net import Network

def balance_volumes(net: 'Network') -> None:
    
    # -------------------------------------------------------
    # Remove u-turns
    # TODO: Find a way to avoid mutating net
    u_turns = [k for k in net._turns.keys() if k[0] == k[2]]

    for k in u_turns:
        del net._turns[k]
    # -------------------------------------------------------
    
    
    # --------------------------------------------
    # Determine inflows/outflows from Links
    # --------------------------------------------
    link_flows: dict[tuple[int, int], Flows] = {}

    for (i, j, k), _ in net.turns(True):
        if (i, j) not in link_flows:
            link_flows[(i, j)] = Flows(key=(i, j))    

        if (j, k) not in link_flows:
            link_flows[(j, k)] = Flows(key=(j, k))

        link_flows[(i, j)].outflows.append((i, j, k))

        link_flows[(j, k)].inflows.append((i, j, k))

    # ------------------------------------------------
    # Assign matrix column numbers to each variable
    # ------------------------------------------------
    matrix_cols_turns = {}
    matrix_cols_links = {}

    global free_col_number 
    free_col_number = 0

    def assign_cols(flows, col_dict):
        global free_col_number
        for x in flows:
            if x in col_dict:
                continue
            col_dict[x] = free_col_number
            free_col_number += 1

    for l, eq in link_flows.items():
        assign_cols(eq.inflows, matrix_cols_turns)
        assign_cols(eq.outflows, matrix_cols_turns)

    for l in link_flows:
        matrix_cols_links[l] = free_col_number
        free_col_number += 1


    # --------------------------------------
    # Build A matrix in Ax = B equation.  
    # --------------------------------------
    n_eq_initial = 0
    for l, eq in link_flows.items():
        if len(eq.inflows) > 0:
            n_eq_initial += 1
        if len(eq.outflows) > 0:
            n_eq_initial += 1

    A = np.zeros(shape=(n_eq_initial, free_col_number))
    
    row_iter = 0

    for l, eq in link_flows.items():
        
        l_col = matrix_cols_links[l]

        if len(eq.inflows) > 0:
            for t in eq.inflows:
                t_col = matrix_cols_turns[t]
                A[row_iter, t_col] = 1
            
            A[row_iter, l_col] = -1
            row_iter += 1

        if len(eq.outflows) > 0:
            for t in eq.outflows:
                t_col = matrix_cols_turns[t]
                A[row_iter, t_col] = 1

            A[row_iter, l_col] = -1
            row_iter += 1

    # ----------------------------------------------------------------
    # Build B matrix in Ax = B equation, provide solution bounds, and
    # build weight matrix W
    # ----------------------------------------------------------------
    B = [0] * A.shape[0]
    
    lbounds = [0] * A.shape[1]
    ubounds = [np.inf] * A.shape[1]

    # Weight matrix
    W = [999999] * n_eq_initial

    # Add equations in A for target volumes, and add target volume to B
    def update_abw_for_target_constraints(target_volume, col, A, B, W):
        """Helper function to update matrices."""
        # TODO: lbound, ubound, free_col_number should be function arguments

        new_eq = np.array([[0] * free_col_number])
        new_eq[0, col] = 1
        
        A = np.concatenate((A, new_eq), axis=0)
        B.append(target_volume)
        W.append(1)

        lbounds[col] = target_volume * 0.85
        ubounds[col] = target_volume * 1.15        
        return (A, B, W)

    for t, col in matrix_cols_turns.items():
        target_volume = net._turns[t].target_volume
        if target_volume == 0:
            continue
        A, B, W = update_abw_for_target_constraints(target_volume, col, A, B, W)

    for l, col in matrix_cols_links.items():
        target_volume = net.link(l[0], l[1]).target_volume
        if target_volume == 0:
            continue
        A, B, W = update_abw_for_target_constraints(target_volume, col, A, B, W)

    B = np.array(B)
    W = np.diag(W)

    np.set_printoptions(linewidth=200)

    # --------------------------------------
    # Solve Matrix Equation Ax = B
    # --------------------------------------
    result = scipy_lsq_linear(np.dot(W, A), np.dot(W, B), bounds=(lbounds, ubounds))
    final_mat = result.x
    print(result)

    for k, v in matrix_cols_links.items():
        net.link(k[0], k[1]).assigned_volume = final_mat[v]
            
    for k, v in matrix_cols_turns.items():
        net._turns[(k[0], k[1], k[2])].assigned_volume = final_mat[v]

    for k, t in net.turns(True):
        print(f"{t.name}: {t.assigned_volume}")

    for (i, j), l in net.links(True):
        print(f"({net.node(i).name}, {net.node(j).name}): {l.assigned_volume}")

    print("done")
