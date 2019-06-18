from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree_imdfa import Subtree
from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges
from copy import deepcopy, copy
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.versions import native as dfg_inst


def merge_components():
    def detect_xor(self, conn_components, this_nx_graph, strongly_connected_components):
        """
        Detects concurrent cut

        Parameters
        --------------
        conn_components
            Connected components
        this_nx_graph
            NX graph calculated on the DFG
        strongly_connected_components
            Strongly connected components
        """
        if len(self.dfg) > 0:
            if len(conn_components) > 1:
                return [True, conn_components]

        return [False, []]
