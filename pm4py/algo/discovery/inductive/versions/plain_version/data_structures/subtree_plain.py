from copy import copy, deepcopy
import networkx as nx
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_from_dfg, \
    get_connected_components, infer_start_activities, infer_end_activities
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges
from pm4py.algo.discovery.dfg.utils.dfg_utils import negate, get_activities_self_loop
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.versions.plain_version import base_case, fall_through
from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.versions.plain_version import splitting as split
from pm4py.algo.filtering.log.attributes import attributes_filter
import numpy as np
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.algo.discovery.dfg import factory as dfg_factory


class SubtreePlain(object):
    def __init__(self, log, dfg, master_dfg, initial_dfg, activities, counts, rec_depth, noise_threshold=0,
                 start_activities=None, end_activities=None, initial_start_activities=None,
                 initial_end_activities=None):
        """
        Constructor

        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
        master_dfg
            Original DFG
        initial_dfg
            Referral directly follows graph that should be taken in account adding hidden/loop transitions
        activities
            Activities of this subtree
        counts
            Shared variable
        rec_depth
            Current recursion depth
        """
        self.master_dfg = copy(master_dfg)
        self.initial_dfg = copy(initial_dfg)
        self.counts = counts
        self.rec_depth = rec_depth
        self.noise_threshold = noise_threshold
        self.start_activities = start_activities
        if self.start_activities is None:
            self.start_activities = []
        self.end_activities = end_activities
        if self.end_activities is None:
            self.end_activities = []
        self.initial_start_activities = initial_start_activities
        if self.initial_start_activities is None:
            self.initial_start_activities = infer_start_activities(master_dfg)
        self.initial_end_activities = initial_end_activities
        if self.initial_end_activities is None:
            self.initial_end_activities = infer_end_activities(master_dfg)

        self.second_iteration = None
        self.activities = None
        self.dfg = None
        self.outgoing = None
        self.ingoing = None
        self.self_loop_activities = None
        self.initial_ingoing = None
        self.initial_outgoing = None
        self.activities_direction = None
        self.activities_dir_list = None
        self.negated_dfg = None
        self.negated_activities = None
        self.negated_outgoing = None
        self.negated_ingoing = None
        self.detected_cut = None
        self.children = None
        self.must_insert_skip = False
        self.log = log
        self.inverted_dfg = None
        self.original_log = log

        self.initialize_tree(dfg, log, initial_dfg, activities)

    def initialize_tree(self, dfg, log, initial_dfg, activities, second_iteration=False, end_call=True):
        """
            Initialize the tree


            Parameters
            -----------
            dfg
                Directly follows graph of this subtree
            log
                the event log
            initial_dfg
                Referral directly follows graph that should be taken in account adding hidden/loop transitions
            activities
                Activities of this subtree
            second_iteration
                Boolean that indicates if we are executing this method for the second time
            """

        self.second_iteration = second_iteration

        if activities is None:
            self.activities = get_activities_from_dfg(dfg)
        else:
            self.activities = copy(activities)

        if second_iteration:
            self.dfg = clean_dfg_based_on_noise_thresh(self.dfg, self.activities, self.noise_threshold)
        else:
            self.dfg = copy(dfg)

        self.initial_dfg = initial_dfg

        self.outgoing = get_outgoing_edges(self.dfg)
        self.ingoing = get_ingoing_edges(self.dfg)
        self.self_loop_activities = get_activities_self_loop(self.dfg)
        self.initial_outgoing = get_outgoing_edges(self.initial_dfg)
        self.initial_ingoing = get_ingoing_edges(self.initial_dfg)
        # self.activities_direction = get_activities_direction(self.dfg, self.activities)
        # self.activities_dir_list = get_activities_dirlist(self.activities_direction)
        self.negated_dfg = negate(self.dfg)
        self.negated_activities = get_activities_from_dfg(self.negated_dfg)
        self.negated_outgoing = get_outgoing_edges(self.negated_dfg)
        self.negated_ingoing = get_ingoing_edges(self.negated_dfg)
        self.detected_cut = None
        self.children = []
        self.log = log
        self.original_log = log

        self.detect_cut(second_iteration=False, parameters=None)

    def create_dfg(self, parameters=None):
        if parameters is None:
            parameters = {}
        if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY

        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

        dfg = [(k, v) for k, v in dfg_inst.apply(self.log, parameters={
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]

        return dfg

    def is_followed_by(self, dfg, activity_a, activity_b):
        """
        check if Activity A is followed by Activity B in the dfg of self, returns bool.
        """
        for i in range(0, len(dfg)):
            if (activity_a, activity_b) == dfg[i][0]:
                return True

        return False

    def transform_dfg_to_directed_nx_graph(self):
        """
        Transform DFG to directed NetworkX graph

        Returns
        ------------
        G
            NetworkX digraph
        nodes_map
            Correspondence between digraph nodes and activities
        """
        G = nx.DiGraph()
        for act in self.activities:
            G.add_node(act)
        for el in self.dfg:
            act1 = el[0][0]
            act2 = el[0][1]
            G.add_edge(act1, act2)
        return G

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

    def get_connection_matrix(self, strongly_connected_components):
        """
        Gets the connection matrix between connected components

        Parameters
        ------------
        strongly_connected_components
            Strongly connected components

        Returns
        ------------
        connection_matrix
            Matrix reporting the connections
        """
        act_to_scc = {}
        for index, comp in enumerate(strongly_connected_components):
            for act in comp:
                act_to_scc[act] = index
        conn_matrix = np.zeros((len(strongly_connected_components), len(strongly_connected_components)))
        for el in self.dfg:
            comp_el_0 = act_to_scc[el[0][0]]
            comp_el_1 = act_to_scc[el[0][1]]
            if not comp_el_0 == comp_el_1:
                conn_matrix[comp_el_1][comp_el_0] = 1
                if conn_matrix[comp_el_0][comp_el_1] == 0:
                    conn_matrix[comp_el_0][comp_el_1] = -1
        return conn_matrix

    def detect_xor(self, conn_components):
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
        if len(self.dfg) >= 0:
            if len(conn_components) > 1:
                return [True, conn_components]

        return [False, []]

    def detect_sequence(self, strongly_connected_components):
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

    def shortest_self_distance(self, act_a, act_b):
        shortest_distance = 99999999
        in_between = []
        # TODO make sure that self.log is correct and not self.original_log is needed
        # go through all traces in the log to find the shortest distance
        for trace in self.log:
            # print('ssd', split.show_nice_trace(trace))
            i = 0
            while i < len(trace):
                # as soon as one activity matches act_a, search for occurrence of b
                if trace[i]["concept:name"] == act_a:
                    # search for occurence of b
                    for j in range(i + 1, len(trace)):
                        compare_act = trace[j]
                        if j - i <= shortest_distance:
                            # if we find another occurrence of act_a, update i
                            if compare_act["concept:name"] == act_a:
                                # in most cases we can shorten our path, except for the case a == b,
                                # then we are done at this point
                                if act_b == act_a:
                                    shortest_distance = j - i
                                    # write a list with activitys between a and b, notice that there
                                    # can be several of such lists
                                    in_between_list = []
                                    for k in range(i, j):
                                        in_between_list.append(trace[k]["concept:name"])
                                    in_between.append(in_between_list)
                                    # if length == 1 we have found a direct self loop and can therefore return this
                                    if len(in_between_list) == 1:
                                        return in_between_list
                                    if len(in_between_list) < shortest_distance:
                                        shortest_distance = in_between_list
                                    i = j
                                    break
                                else:
                                    i = j
                            # as soon as we find occurrence of act_b
                            elif compare_act["concept:name"] == act_b:
                                # shortest_distance = j - i
                                # write a list with activitys between a and b, notice that there
                                # can be several of such lists
                                in_between_list = []
                                for k in range(i, j):
                                    in_between_list.append(trace[k]["concept:name"])
                                in_between.append(in_between_list)
                                if len(in_between_list) < shortest_distance:
                                    shortest_distance = in_between_list
                                i = j
                                break
                        else:
                            break
                    if i+1 != len(trace):
                        if i != j:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1
        return in_between

    def check_if_b_between(self, a, b):
        in_between = self.shortest_self_distance(a, a)
        if len(in_between) == 0:
            return False
        else:
            min_lenght = len(in_between[0])
            for element in in_between:
                if len(element) > min_lenght:
                    in_between.remove(element)
            for element in in_between:
                if b in element:
                    return True

    """
    def detect_parallel(self):
        start_activities = list(start_activities_filter.get_start_activities(self.log, parameters=None).keys())
        end_activities = list(end_activities_filter.get_end_activities(self.log, parameters=None).keys())
        p = []
        for a in self.activities:
            p.append([a])
        activities = []
        for a in self.activities:
            activities.append(a)
        pairs = []
        for a in activities:
            for b in activities:
                if a != b:
                    if [a, b] not in pairs:
                        if [b, a] not in pairs:
                            pairs.append([a, b])

        something_changed = True
        while something_changed:
            something_changed =False
            for i in range(0, len(p)):




        for pair in pairs:
            a = pair[0]
            b = pair[1]
            # if a and b do not connected in both ways, we merge them
            follow_one = self.is_followed_by(self.dfg, a, b)
            follow_two = self.is_followed_by(self.dfg, b, a)
            if not (follow_one and follow_two):
                if [a] in p:
                    p.remove([a])
                if [b] in p:
                    p.remove([b])
                append_value = [a, b]
                if append_value not in p:
                    p.append(append_value)
            # else if b lies on the shortest path between a and a, we merge b and a
            elif self.check_if_b_between(a, b):
                if [a] in p:
                    p.remove([a])
                if [b] in p:
                    p.remove([b])
                append_value = [a, b]
                if append_value not in p:
                    p.append(append_value)
        # now we check for every part of p if it contains start and end activities,
        # if not we merge the element with a random other element

        for e in range(0, len(p)):
            element = p[e]
            contains_start_or_end = False
            for act in element:
                if act in start_activities or act in end_activities:
                    contains_start_or_end = True
                    break
            if not contains_start_or_end:
                if p[e+1]:
                    append_value = []
                    for z in element:
                        append_value.append(z)
                    for y in p[e+1]:
                        append_value.append(y)
                    p.append(append_value)
                    p.remove(p[e])
                    p.remove(p[e+1])
                    e = 0
                elif len(p) == 1:
                    return False, p
                else:
                    append_value = []
                    for z in element:
                        append_value.append(z)
                    for y in p[0]:
                        append_value.append(y)
                    p.append(append_value)
                    p.remove(p[e])
                    p.remove(p[0])
                    e = 0

        return True, p
    """

    def detect_concurrent(self):
        start_activities = list(start_activities_filter.get_start_activities(self.log, parameters=None).keys())
        end_activities = list(end_activities_filter.get_end_activities(self.log, parameters=None).keys())
        print('start activities: ', start_activities, 'end activities: ', end_activities)
        inverted_dfg = []  # create an inverted dfg, the connected components of this dfg are the split
        for a in self.activities:
            for b in self.activities:
                if a != b:
                    if not (self.is_followed_by(self.dfg, a, b) and self.is_followed_by(self.dfg, b, a)):
                        if ((a, b), 1) not in inverted_dfg:
                            inverted_dfg.append(((a, b), 1))
                            inverted_dfg.append(((b, a), 1))
        self.inverted_dfg = inverted_dfg
        new_ingoing = get_ingoing_edges(inverted_dfg)
        new_outgoing = get_outgoing_edges(inverted_dfg)
        conn = get_connected_components(new_ingoing, new_outgoing, self.activities)
        if len(conn) > 1:
            something_changed = True
            while something_changed:
                something_changed = False
                for i in range(0, len(conn)-1):
                    for j in range(i+1, len(conn)):
                        for act_a in conn[i]:
                            for act_b in conn[j]:
                                # check if a "doubleloop" b
                                between = self.check_if_b_between(act_a, act_b)
                                # check if b "doubleloop" a
                                between_2 = self.check_if_b_between(act_b, act_a)
                                if between:
                                    new_set = conn[i].union(conn[j])
                                    if conn[i] in conn:
                                        remove_conn_i = True
                                    if conn[j] in conn:
                                        if remove_conn_i:
                                            conn.remove(conn[i])
                                            conn.remove(conn[j-1])
                                        else:
                                            conn.remove(conn[j])
                                    conn.append(new_set)
                                    something_changed = True
                                    print("THIS GOT EXECUTED")
                                    break
                                elif between_2:
                                    new_set = conn[i].union(conn[j])
                                    if conn[i] in conn:
                                        conn.remove([conn[i]])
                                    if conn[j] in conn:
                                        conn.remove(conn[j])
                                    conn.append(new_set)
                                    something_changed = True
                                    print("THIS GOT EXECUTED")
                                    break
                            if something_changed:
                                break
                        if something_changed:
                            break
                    if something_changed:
                        break

        if len(conn) > 1:
            return [True, conn]

        return [False, []]

    def get_index_of_x_in_list(self, x, li):
        for i in range(0, len(li)):
            if li[i] == x:
                return i

    def find_set_with_x(self, x, list_of_sets):
        for i in range(0, len(list_of_sets)):
            if x in list_of_sets[i]:
                return i

    def detect_loop(self):
        # p0 is part of return value, it contains the partition of activities
        # write all start and end activities in p1
        start_activities = list(start_activities_filter.get_start_activities(self.log, parameters=None).keys())
        end_activities = list(end_activities_filter.get_end_activities(self.log, parameters=None).keys())
        p1 = []
        for act in start_activities:
            if act not in p1:
                p1.append(act)
        for act in end_activities:
            if act not in p1:
                p1.append(act)

        # create new dfg without the transitions to start and end activities
        new_dfg = deepcopy(self.dfg)
        copy_dfg = deepcopy(new_dfg)
        for ele in copy_dfg:
            if ele[0][0] in p1 or ele[0][1] in p1:
                new_dfg.remove(ele)
        # get connected components of this new dfg
        new_ingoing = get_ingoing_edges(new_dfg)
        new_outgoing = get_outgoing_edges(new_dfg)

        current_activities = {}
        iterate_order = []
        for element in self.activities:
            if element not in p1:
                current_activities.update({element: 1})
                iterate_order.append(element)
        # create an overview of what activity has which outgoing connections
        outgoing = [list() for _ in range(len(iterate_order))]
        for i in range(0, len(iterate_order)):
            current_act = iterate_order[i]
            for element in new_dfg:
                if element[0][0] == current_act:
                    if element[0][1] in iterate_order:
                        outgoing[i].append(element[0][1])

        # built p2, ..., pn :
        acts_not_assigned_to_set = deepcopy(iterate_order)
        p0 = []
        p = [list() for _ in range(len(iterate_order))]
        max_set = iterate_order
        max_set_found = False
        for i in range(0, len(iterate_order)):
            act = iterate_order[i]
            if act in acts_not_assigned_to_set:
                p[i] = [act]
                acts_not_assigned_to_set.remove(act)
                added = True
                while added:
                    added = False
                    # check if max set is already found
                    count = 0
                    for li in p:
                        if len(li) != 0:
                            count += 1
                    if count == len(max_set):
                        max_set_found = True
                        break
                    # if max set is not found, continue adding acts
                    for act_b in p[i]:
                        index_of_act_b_in_outgoing = self.get_index_of_x_in_list(act_b, iterate_order)
                        for outgoing_act in outgoing[index_of_act_b_in_outgoing]:
                            if outgoing_act in acts_not_assigned_to_set:
                                acts_not_assigned_to_set.remove(outgoing_act)
                                p[i].append(outgoing_act)
                                added = True
                                break
                        if added:
                            break
            if max_set_found:
                break

        for li in p:
            if len(li) == 0:
                p.remove(li)

        # p0 = get_connected_components(new_ingoing, new_outgoing, current_activities)
        p.insert(0, p1)
        p0 = p
        iterable_dfg = []
        for i in range(0, len(self.dfg)):
            iterable_dfg.append(self.dfg[i][0])
        # p0 is like P1,P2,...,Pn in line 3 on page 190 of the IM Thesis
        # check for subsets in p0 that have connections to and end or from a start activity
        p0_copy = deepcopy(p0)  # we use the bool removed to exit the nested loops once we removed an element
        for element in p0_copy:  # for every set in p0
            removed = False
            if element in p0 and element != p0[0]:
                for act in element:  # for every activity in this set
                    for e in end_activities:  # for every end activity
                        if (act, e) in iterable_dfg:  # check if connected
                            # is there an element in dfg pointing from any act in a subset of p0 to an end activity
                            for activ in element:
                                if activ not in p0[0]:
                                    p0[0].append(activ)
                            p0.remove(element)  # remove subsets that are connected to an end activity
                            removed = True
                            break
                    if removed:
                        break
                    for s in start_activities:
                        if not removed:
                            if (s, act) in iterable_dfg:
                                for acti in element:
                                    if acti not in p0[0]:
                                        p0[0].append(acti)
                                p0.remove(element)  # remove subsets that are connected to an end activity
                                removed = True
                                break
                        else:
                            break
                    if removed:
                        break
        """                
        p0_copy = deepcopy(p0)            # we use the bool removed to exit the nested loops once we removed an element
        for element in p0_copy:                             # for every set in p0
            removed = False
            if element in p0 and element != p0[0]:
                for act in element:                             # for every activity in this set
                    for e in self.end_activities:               # for every end activity
                        for i in range(0, len(self.dfg)):
                            if (act, e) == self.dfg[i][0]:      # check if connected
                                # is there an element in dfg pointing from any act in a subset of p0 to an end activity
                                for activ in element:
                                    if activ not in p0[0]:
                                        p0[0].append(activ)
                                p0.remove(element)              # remove subsets that are connected to an end activity
                                removed = True
                                break
                        if removed:
                            break
                    for s in self.start_activities:
                        if not removed:
                            for i in range(0, len(self.dfg)):
                                if (s, act) == self.dfg[i][0]:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    p0.remove(element)  # remove subsets that are connected to an end activity
                                    removed = True
                                    break
                        else:
                            break
                    if removed:
                        break
        """
        iterable_dfg = list()
        for i in range(0, len(self.dfg)):
            iterable_dfg.append(self.dfg[i][0])

        for element in p0:
            if element in p0 and element != p0[0]:
                for act in element:
                    for e in self.end_activities:
                        if (e, act) in iterable_dfg:  # get those act, that are connected from an end activity
                            for e2 in self.end_activities:  # check, if the act is connected from all end activities
                                if (e2, act) not in iterable_dfg:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    p0.remove(element)  # remove subsets that are connected to an end activity
                                    break
                    for s in self.start_activities:
                        if (act, s) in iterable_dfg:  # same as above (in this case for activities connected to
                            # a start activity)
                            for s2 in self.start_activities:
                                if (act, s2) not in iterable_dfg:
                                    for acti in element:
                                        if acti not in p0[0]:
                                            p0[0].append(acti)
                                    p0.remove(element)  # remove subsets that are connected to an end activity
                                    break
        for element in p0:
            if len(element) == 0:
                p0.remove(element)
        if len(p0) > 1:
            return [True, p0]
        else:
            return [False, []]

    def check_for_cut(self, test_log, deleted_activity=None, parameters=None):
        if deleted_activity is not None:
            del self.activities[deleted_activity]
        if parameters is None:
            parameters = {}
        if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
        if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        dfg = [(k, v) for k, v in dfg_inst.apply(test_log, parameters={
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
        self.dfg = dfg
        self.outgoing = get_outgoing_edges(self.dfg)
        self.ingoing = get_ingoing_edges(self.dfg)
        conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
        this_nx_graph = self.transform_dfg_to_directed_nx_graph()
        strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
        # search for cut and return true as soon as a cut is found:
        xor_cut = self.detect_xor(conn_components)
        if xor_cut[0]:
            return True
        else:
            sequence_cut = self.detect_sequence(strongly_connected_components)
            if sequence_cut[0]:
                return True
            else:
                parallel_cut = self.detect_concurrent()
                if parallel_cut[0]:
                    return True
                else:
                    loop_cut = self.detect_loop()
                    if loop_cut[0]:
                        return True
                    else:
                        return False

    def show_split(self, new_logs):
        # returns nice representation of new_logs
        nls = []
        for log in new_logs:
            nl = []
            for trace in log:
                nt = []
                for element in trace:
                    if len(element) > 0:
                        nt.append(element['concept:name'])
                nl.append(nt)
            nls.append(nl)
        return nls

    def show_nice_log(self, log):
        nl = []
        for trace in log:
            nt = []
            for element in trace:
                nt.append(element['concept:name'])
            nl.append(nt)
        return nl

    def detect_cut(self, second_iteration=False, parameters=None):

        # print(self.detect_parallel())

        if parameters is None:
            parameters = {}
        if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
        if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        # check base cases:
        empty_log = base_case.empty_log(self.log)
        if empty_log:
            print('detected empty_log')
            self.detected_cut = 'empty_log'
        single_activity = base_case.single_activity(self.log)
        if single_activity:
            self.detected_cut = 'single_activity'
            print("single activity")
        # if no base cases are found, search for a cut:
        else:
            conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = self.transform_dfg_to_directed_nx_graph()
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
            xor_cut = self.detect_xor(conn_components)
            # the following part searches for a cut in the current log
            # if a cut is found, the log is split according to the cut, the resulting logs are saved in new_logs
            # recursion is used on all the logs in new_logs
            if xor_cut[0]:
                print('xor', xor_cut[1])
                self.detected_cut = 'concurrent'
                new_logs = split.split_xor(xor_cut[1], self.log)
                # print('splitted to: ', self.show_split(new_logs))
                for l in new_logs:
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                    activities = attributes_filter.get_attribute_values(l, activity_key)
                    start_activities = list(
                        start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                    end_activities = list(
                        end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                    print('dfg: ', new_dfg)
                    self.children.append(
                        SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold, start_activities=start_activities,
                                     end_activities=end_activities,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
            else:
                # print('no xor-cut')
                sequence_cut = self.detect_sequence(strongly_connected_components)
                if sequence_cut[0]:
                    new_logs = split.split_sequence(sequence_cut[1], self.log)
                    self.detected_cut = "sequential"
                    # print('sequence')
                    print('detected sequence_cut', sequence_cut[1])
                    # print('splitted to: ', self.show_split(new_logs))
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        """
                        dfg_viz = dfg_factory.apply(l)
                        gviz = dfg_vis_factory.apply(dfg_viz, log=l, variant="frequency")
                        dfg_vis_factory.view(gviz)
                        """
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                        print('dfg: ', new_dfg)
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold, start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                else:
                    # print('no sequence-cut')
                    parallel_cut = self.detect_concurrent()
                    if parallel_cut[0]:
                        new_logs = split.split_parallel(parallel_cut[1], self.log)
                        self.detected_cut = "parallel"
                        # print('parallel')
                        print('detected parallel_cut', parallel_cut[1])
                        # print('splitted to: ', self.show_split(new_logs))
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                            activities = attributes_filter.get_attribute_values(l, activity_key)
                            start_activities = list(
                                start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                            end_activities = list(
                                end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                            print('dfg: ', new_dfg)
                            self.children.append(
                                SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold, start_activities=start_activities,
                                             end_activities=end_activities,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities))
                    else:
                        # print('no parallel-cut')
                        # dfg_viz = dfg_factory.apply(self.log)
                        # gviz = dfg_vis_factory.apply(dfg_viz, log=self.log, variant="frequency")
                        # dfg_vis_factory.view(gviz)
                        loop_cut = self.detect_loop()
                        if loop_cut[0]:
                            new_logs = split.split_loop(loop_cut[1], self.log)
                            self.detected_cut = "loopCut"
                            # print('loop')
                            print('detected loop', loop_cut[1])
                            # print('splitted to: ', self.show_split(new_logs))
                            for l in new_logs:
                                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                                activities = attributes_filter.get_attribute_values(l, activity_key)
                                start_activities = list(
                                    start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                                end_activities = list(
                                    end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                                print('dfg: ', new_dfg)
                                self.children.append(
                                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                                 self.rec_depth + 1,
                                                 noise_threshold=self.noise_threshold,
                                                 start_activities=start_activities,
                                                 end_activities=end_activities,
                                                 initial_start_activities=self.initial_start_activities,
                                                 initial_end_activities=self.initial_end_activities))

                        # if the code gets to this point, there is no base_case and no cut found in the log
                        # therefore, we now apply fall through:
                        else:
                            # print('no loop-cut... applying fall through')
                            self.apply_fall_through(parameters)

    # this is called at the end of detect_cut, if no cut was found and a fallthrough needs to be applied
    def apply_fall_through(self, parameters=None):
        if parameters is None:
            parameters = {}
        if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
        if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

        empty_trace, new_log = fall_through.empty_trace(self.log)
        # if an empty trace is found, the empty trace fallthrough applies
        #
        if empty_trace:
            activites_left = []
            for trace in new_log:
                for act in trace:
                    if act["concept:name"] not in activites_left:
                        activites_left.append(act["concept:name"])
            print('empty trace fall through', activites_left)
            self.detected_cut = 'empty_trace'
            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
            activities = attributes_filter.get_attribute_values(new_log, activity_key)
            print('dfg: ', new_dfg)
            self.children.append(
                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                             self.rec_depth + 1,
                             noise_threshold=self.noise_threshold,
                             initial_start_activities=self.initial_start_activities,
                             initial_end_activities=self.initial_end_activities))
        else:
            activity_once, new_log, small_log = fall_through.act_once_per_trace(self.log, self.activities)
            if activity_once:
                nice_small_log = self.show_nice_log(small_log)
                # print('activity once fallthrough ', nice_small_log)
                print('activity once fallthrough ')
                self.detected_cut = 'parallel'
                # create two new dfgs as we need them to append to self.children later
                new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                           v > 0]
                activities = attributes_filter.get_attribute_values(new_log, activity_key)
                small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                             v > 0]
                small_activities = attributes_filter.get_attribute_values(small_log, activity_key)
                # append the chosen activity as leaf:
                print('small dfg: ', small_dfg)
                self.children.append(
                    SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg, small_activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))
                # continue with the recursion on the new log
                print('dfg: ', new_dfg)
                self.children.append(
                    SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))

            else:
                activity_concurrent, new_log, small_log, activity_left_out = fall_through.activity_concurrent(self,
                                                                                                              self.log,
                                                                                                              self.activities)
                if activity_concurrent:
                    nice_small_log = self.show_nice_log(small_log)
                    # print('activity concurrent fallthrough ', nice_small_log)
                    print('activity concurrent fallthrough: ', activity_left_out)
                    self.detected_cut = 'parallel'
                    # create two new dfgs on to append later
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                               v > 0]
                    activities = attributes_filter.get_attribute_values(new_log, activity_key)
                    small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                                 v > 0]
                    small_activities = attributes_filter.get_attribute_values(small_log, activity_key)
                    # append the concurrent activity as leaf:
                    print('small dfg: ', small_dfg)
                    self.children.append(
                        SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg,
                                     small_activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
                    # continue with the recursion on the new log:
                    print('dfg: ', new_dfg)
                    self.children.append(
                        SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                     activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
                else:
                    strict_tau_loop, new_log = fall_through.strict_tau_loop(self.log, self.start_activities,
                                                                            self.end_activities)
                    if strict_tau_loop:
                        activites_left = []
                        for trace in new_log:
                            for act in trace:
                                if act["concept:name"] not in activites_left:
                                    activites_left.append(act["concept:name"])
                        print('strict_tau-loop fallthrough', activites_left)
                        self.detected_cut = 'strict_tau_loop'
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                                   v > 0]
                        activities = attributes_filter.get_attribute_values(new_log, activity_key)
                        print('dfg: ', new_dfg)
                        self.children.append(
                            SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                         activities,
                                         self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                    else:
                        tau_loop, new_log = fall_through.tau_loop(self.log, self.start_activities)
                        if tau_loop:
                            activites_left = []
                            for trace in new_log:
                                for act in trace:
                                    if act["concept:name"] not in activites_left:
                                        activites_left.append(act["concept:name"])
                            print('tau-loop fall through', activites_left)
                            self.detected_cut = 'tau_loop'
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                                       v > 0]
                            activities = attributes_filter.get_attribute_values(new_log, activity_key)
                            print('dfg: ', new_dfg)
                            self.children.append(
                                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                             activities,
                                             self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities))
                        else:
                            activites_left = []
                            for trace in new_log:
                                for act in trace:
                                    if act["concept:name"] not in activites_left:
                                        activites_left.append(act["concept:name"])
                            print('flower-fallthrough:', activites_left, fall_through.show_nice_log(self.log))
                            self.detected_cut = 'flower'
                            # apply flower fall through as last option:


def make_tree(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold, start_activities,
              end_activities, initial_start_activities, initial_end_activities):
    tree = SubtreePlain(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold,
                        start_activities,
                        end_activities, initial_start_activities, initial_end_activities)

    return tree
