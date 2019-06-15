from pm4py.algo.discovery.inductive.versions.dfg.data_structures.subtree_imdfa import Subtree
from pm4py import util as pmutil
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges


def create_dfg(log, parameters = None)

    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY

    activity_key = pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY
    follow_relation = map((lambda t: [(t[i - 1][activity_key], t[i][activity_key]) for i in range(1, len(t))]), log) #iterate on log, safe all df-pairs in map
    dfg = (list(follow_relation))    #f is now a list with all the dfg-tuples in it

    return dfg


def get_connected_components(self, ingoing, outgoing, activities):
    """Question: is the set like a potenzmenge, i.e. if ABC can AB and BC and for example also be part?"""
    """
    Get connected components in the DFG graph

    Parameters
    -----------
    ingoing
        Ingoing attributes
    outgoing
        Outgoing attributes
    activities
        Activities to consider
    """
    activities_considered = set()

    connected_components = []

    """Question, if activity A is in ingoing and outgoing, is ingoing[act] not the same as outgoing[act]? Does this not refer to the same A?"""
    for act in ingoing:
        ingoing_act = set(ingoing[act].keys())
        if act in outgoing:
            ingoing_act = ingoing_act.union(set(outgoing[act].keys()))

        ingoing_act.add(act)

        if ingoing_act not in connected_components:
            connected_components.append(ingoing_act)
            activities_considered = activities_considered.union(set(ingoing_act))

    for act in outgoing:
        if act not in ingoing:
            outgoing_act = set(outgoing[act].keys())
            outgoing_act.add(act)
            if outgoing_act not in connected_components:
                connected_components.append(outgoing_act)
            activities_considered = activities_considered.union(set(outgoing_act))

    for activ in activities:
        if activ not in activities_considered:
            added_set = set()
            added_set.add(activ)
            connected_components.append(added_set)
            activities_considered.add(activ)

    max_it = len(connected_components)
    for it in range(max_it - 1):
        something_changed = False

        old_connected_components = copy(connected_components)
        connected_components = []

        for i in range(len(old_connected_components)):
            conn1 = old_connected_components[i]

            if conn1 is not None:
                for j in range(i + 1, len(old_connected_components)):
                    conn2 = old_connected_components[j]
                    if conn2 is not None:
                        inte = conn1.intersection(conn2)

                        if len(inte) > 0:
                            conn1 = conn1.union(conn2)
                            something_changed = True
                            old_connected_components[j] = None

            if conn1 is not None and conn1 not in connected_components:
                connected_components.append(conn1)

        if not something_changed:
            break

    return connected_components


def merge_components():


def is_followed_by(self, activityA, activityB):
    """
    check if Activity A is followed by Activity B in the dfg of self, returns bool.
    """
    f = create_dfg(self.log)
    if (activityA, activityB) in f:
        return True

    return False


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


def detect_sequence(self, conn_components, this_nx_graph, strongly_connected_components):
    """
            Detect sequential cut in DFG graph

            Parameters
            --------------
            conn_components
                Connected components of the graph
            this_nx_graph
                NX graph calculated on the DFG
            strongly_connected_components
                Strongly connected components
            """
    if len(strongly_connected_components) > 1:
        orig_conn_comp = copy(strongly_connected_components)
        conn_matrix = self.get_connection_matrix(strongly_connected_components)
        something_changed = True
        while something_changed:
            something_changed = False
            i = 0
            while i < len(strongly_connected_components):
                idx_i_comp = orig_conn_comp.index(strongly_connected_components[i])
                j = i + 1
                while j < len(strongly_connected_components):
                    idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                    if conn_matrix[idx_i_comp][idx_j_comp] > 0:
                        copyel = copy(strongly_connected_components[i])
                        strongly_connected_components[i] = strongly_connected_components[j]
                        strongly_connected_components[j] = copyel
                        something_changed = True
                        break
                    j = j + 1
                i = i + 1
        ret_connected_components = []
        ignore_comp = set()
        i = 0
        while i < len(strongly_connected_components):
            if i not in ignore_comp:
                idx_i_comp = orig_conn_comp.index(strongly_connected_components[i])
                comp = copy(strongly_connected_components[i])
                j = i + 1
                is_component_mergeable = True
                while j < len(strongly_connected_components):
                    idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                    if conn_matrix[idx_i_comp][idx_j_comp] < 0 or conn_matrix[idx_i_comp][idx_j_comp] > 0:
                        is_component_mergeable = False
                        break
                    j = j + 1
                if is_component_mergeable:
                    j = i + 1
                    while j < len(strongly_connected_components):
                        idx_j_comp = orig_conn_comp.index(strongly_connected_components[j])
                        if conn_matrix[idx_i_comp][idx_j_comp] == 0:
                            comp = comp + strongly_connected_components[j]
                            ignore_comp.add(j)
                        else:
                            break
                        j = j + 1
                ret_connected_components.append(comp)
            i = i + 1

        if len(ret_connected_components) > 1:
            return [True, ret_connected_components]
    return [False, [], []]

def is_followed_by(dfg, activity_a, activity_b):
    """
    check if Activity A is followed by Activity B in the dfg of self, returns bool.
    """
    for i in range(0, len(dfg)):
        if (activity_a, activity_b) == dfg[i][0]:
            return True

    return False


def detect_concurrent(self):
    inverted_dfg = []
    for  a in self.activities:
        for  b in self.activities:
            if a != b:
                if not(is_followed_by(self.dfg, a, b) and is_followed_by(self.dfg, b, a)):
                    if (a, b) not in inverted_dfg:
                        inverted_dfg.append((a, b), 1)

    self.inverted_dfg = inverted_dfg
    new_ingoing = get_ingoing_edges(inverted_dfg)
    new_outgoing = get_ingoing_edges(inverted_dfg)
    conn = get_connected_components(new_ingoing, new_outgoing, self.activities)
    print(conn)

def detect_loop():


def detect_cut(self):
    return detect_concurrent(self)

