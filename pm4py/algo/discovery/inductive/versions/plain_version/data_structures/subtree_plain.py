from copy import copy
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
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.util import get_tree_repr_imdfb
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.algo.filtering.log.attributes import attributes_filter





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

        self.initialize_tree(dfg, log, initial_dfg, activities)

    def initialize_tree(self, dfg, log, initial_dfg, activities, second_iteration=False):
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
        self.detect_cut(second_iteration=False)

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

    def detect_concurrent(self):
        inverted_dfg = []  # create an inverted dfg, the connected components of this dfg are the split
        for a in self.activities:
            for b in self.activities:
                if a != b:

                    if not (self.is_followed_by(self.dfg, a, b) and self.is_followed_by(self.dfg, b, a)):
                        if (a, b) not in inverted_dfg:
                            inverted_dfg.append(((a, b), 1))
                            inverted_dfg.append(((b, a), 1))

        self.inverted_dfg = inverted_dfg
        print(inverted_dfg)
        new_ingoing = get_ingoing_edges(inverted_dfg)
        new_outgoing = get_outgoing_edges(inverted_dfg)
        conn = get_connected_components(self, new_ingoing, new_outgoing, self.activities)
        if len(conn) > 1:
            return [True, conn]

        return [False, []]

    def detect_loop(self):
        # p0 is part of return value, it contains the partition of activities
        # write all start and end activities in p1
        p1 = set()
        if type(self.start_activities) is dict:
            p1.add(self.start_activities)
            p1.add(list(self.end_activities))
        else:
            p1.add(self.start_activities)
            p1.add(self.end_activities)
        # create new dfg without the transitions to start and end activities
        new_dfg = self.dfg
        for act in p1:
            for element in new_dfg:
                if element[0][0] == act or element[0][1] == act:
                    new_dfg.remove(element)
        # get connected components of this new dfg
        new_ingoing = get_ingoing_edges(new_dfg)
        new_outgoing = get_outgoing_edges(new_dfg)
        p0 = get_connected_components(self, new_ingoing, new_outgoing, self.activities)   # p0 is like P2,...,Pn in line 3 on page 190 of the IM Thesis

        # check for subsets in p0 that have connections to and end or from a start activity
        for element in p0:
            for act in element:
                for e in self.end_activities:
                    for i in range(0, self.dfg.length()):
                        if (act, e) == self.dfg[i][0]:      # is there an element in the dfg pointing from any act in a subset of p0 to an end activity?
                            p0.remove(element)              # remove subsets that are connected to an end activity
                for s in self.start_activities:
                    for i in range(0, self.dfg.length()):
                        if (s, act) == self.dfg[i][0]:
                            p0.remove(element)              # remove subsets that are connected from a start activity

        iterable_dfg = list()
        for i in range(0, self.dfg.length()):
            iterable_dfg.append(self.dfg[i][0])

        for element in p0:
            for act in element:
                for e in self.end_activities:
                    if (e, act) in iterable_dfg:            # get those act, that are connected from an end activity
                        for e2 in self.end_activities:      # check, if the act is connected from all end activities
                            if (e2, act) not in iterable_dfg:
                                p0.remove(element)
                                break
                for s in self.start_activities:
                    if (act, s) in iterable_dfg:            # same as above (in this case for activities connected to
                                                            # a start activity)
                        for s2 in self.start_activities:
                            if (act, s2) not in iterable_dfg:
                                p0.remove(element)
                                break

        if len(p0) > 0:
            p0.append(p1)
            return [True, p0]
        else:
            return [False, []]

    def check_for_cut(self, l):
        conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
        this_nx_graph = self.transform_dfg_to_directed_nx_graph()
        strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
        #search for cut and return true as soon as a cut is found:
        xor_cut = self.detect_xor(conn_components, this_nx_graph, strongly_connected_components)
        if xor_cut[0]:
            return True
        else:
            sequence_cut = self.detect_sequence(conn_components, this_nx_graph, strongly_connected_components)
            if sequence_cut[0]:
                return True
            else:
                parallel_cut = self.detect_sequence(conn_components, this_nx_graph, strongly_connected_components)
                if parallel_cut[0]:
                    return True
                else:
                    loop_cut = self.detect_sequence(conn_components, this_nx_graph, strongly_connected_components)
                    if loop_cut[0]:
                        return True
                    else:
                        return False

    def detect_cut(self,  second_iteration=False, parameters=None):
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
        single_activity = base_case.single_activity(self.log)
        if empty_log:
            self.detected_cut = 'empty_log'
        elif single_activity:
            self.detected_cut = 'single_activity'
        # if no base cases are found, search for a cut:
        else:
            conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
            this_nx_graph = self.transform_dfg_to_directed_nx_graph()
            strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
            xor_cut = self.detect_xor(conn_components, this_nx_graph, strongly_connected_components)
            # the following part searches for a cut in the current log
            # if a cut is found, the log is split according to the cut, the resulting logs are saved in new_logs
            # recursion is used on all the logs in new_logs
            if xor_cut[0]:
                self.detected_cut = 'concurrent'
                new_logs = split.split_xor(xor_cut[1], self.log)
                for l in new_logs:
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                    activities = attributes_filter.get_attribute_values(l, activity_key)
                    self.children.apppend(
                        SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
            else:
                sequence_cut = self.detect_sequence(conn_components, this_nx_graph, strongly_connected_components)
                if sequence_cut[0]:
                    new_logs = split.split_sequence(sequence_cut[1], self.log)
                    self.detected_cut = "sequential"
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                else:
                    parallel_cut = self.detect_sequence(self)
                    if parallel_cut[0]:
                        new_logs = split.split_parallel(parallel_cut[1], self.log)
                        self.detected_cut = "parallel"
                        for l in new_logs:
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                            activities = attributes_filter.get_attribute_values(l, activity_key)
                            self.children.append(
                                SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities))
                    else:
                        loop_cut = self.detect_loop(self)
                        if loop_cut[0]:
                            new_logs = split.split_loop(loop_cut[1], self.log)
                            self.detected_cut = "loopCut"
                            for l in new_logs:
                                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                                activities = attributes_filter.get_attribute_values(l, activity_key)
                                self.children.append(
                                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                                 self.rec_depth + 1,
                                                 noise_threshold=self.noise_threshold,
                                                 initial_start_activities=self.initial_start_activities,
                                                 initial_end_activities=self.initial_end_activities)

                        # if the code gets to this point, there is no base_case and no cut found in the log
                        # therefore, we now apply fall through:
                        self.apply_fall_through(self, parameters)


    # this function is called at the end of detect_cut in the case, that no cut was found and a fallthrough needs to be applied
    def apply_fall_through(self, parameters = None):
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
            self.detected_cut = 'concurrent'
            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
            activities = attributes_filter.get_attribute_values(new_log, activity_key)
            # TODO: append silent transition
            # self.children.append()
            self.children.append(
                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                             self.rec_depth + 1,
                             noise_threshold=self.noise_threshold,
                             initial_start_activities=self.initial_start_activities,
                             initial_end_activities=self.initial_end_activities))
        else:
            activity_once, new_log, small_log = fall_through.act_once_per_trace(self.log, self.activities)
            if activity_once:
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
                self.children.append(
                    SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg, small_activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))
                # continue with the recursion on the new log
                self.children.append(
                    SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg, activities,
                                 self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))

            else:
                activity_concurrent, new_log, small_log = fall_through.activity_concurrent(self.log, self.activities)
                if activity_concurrent:
                    self.detected_cut = 'parallel'
                    #create two new dfgs on to append later
                    new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                               v > 0]
                    activities = attributes_filter.get_attribute_values(new_log, activity_key)
                    small_dfg = [(k, v) for k, v in dfg_inst.apply(small_log, parameters={
                        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                               v > 0]
                    small_activities = attributes_filter.get_attribute_values(small_log, activity_key)
                    # append the concurrent activity as leaf:
                    self.children.append(
                        SubtreePlain(small_log, small_dfg, self.master_dfg, self.initial_dfg,
                                     small_activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
                    # continue with the recursion on the new log:
                    self.children.append(
                        SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                     activities,
                                     self.counts,
                                     self.rec_depth + 1,
                                     noise_threshold=self.noise_threshold,
                                     initial_start_activities=self.initial_start_activities,
                                     initial_end_activities=self.initial_end_activities))
                else:
                    strict_tau_loop, new_log = fall_through.strict_tau_loop(self.log, self.start_activities, self.end_activities)
                    if strict_tau_loop:
                        self.detected_cut = 'loopCut'
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                                   v > 0]
                        activities = attributes_filter.get_attribute_values(new_log, activity_key)
                        self.children.append(
                            SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                         activities,
                                         self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                        # TODO: append silent transition
                        # self.children.append()
                    else:
                        tau_loop, new_log = fall_through.tau_loop(self.log, self.start_activities)
                        if tau_loop:
                            self.detected_cut = 'loopCut'
                            new_dfg = [(k, v) for k, v in dfg_inst.apply(new_log, parameters={
                                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if
                                       v > 0]
                            activities = attributes_filter.get_attribute_values(new_log, activity_key)
                            self.children.append(
                                SubtreePlain(new_log, new_dfg, self.master_dfg, self.initial_dfg,
                                             activities,
                                             self.counts,
                                             self.rec_depth + 1,
                                             noise_threshold=self.noise_threshold,
                                             initial_start_activities=self.initial_start_activities,
                                             initial_end_activities=self.initial_end_activities))
                            # TODO: append silent transition
                            # self.children.append()












def make_tree(log, dfg, master_dfg, initial_dfg, activities, c, noise_threshold, start_activities,
              end_activities, initial_start_activities, initial_end_activities):
    tree = SubtreePlain(log, dfg, master_dfg, initial_dfg, activities, c, noise_threshold, start_activities,
                        end_activities, initial_start_activities, initial_end_activities)

    return tree
