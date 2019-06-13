from copy import copy

from pm4py.algo.discovery.dfg.utils.dfg_utils import filter_dfg_on_act, negate, get_activities_dirlist, \
    get_activities_self_loop, get_activities_direction
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges, get_activities_from_dfg, \
    get_connected_components, add_to_most_probable_component, infer_start_activities, infer_end_activities
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.versions.plain_version import cutting


class Subtree_plain(object):

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

        self.initialize_tree(dfg, log, initial_dfg, activities)

    def initialize_tree(self, log, dfg, initial_dfg, activities, second_iteration=False):
        """
        Initialize the tree


        Parameters
        -----------
        dfg
            Directly follows graph of this subtree
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
        self.activities_direction = get_activities_direction(self.dfg, self.activities)
        self.activities_dir_list = get_activities_dirlist(self.activities_direction)
        self.negated_dfg = negate(self.dfg)
        self.negated_activities = get_activities_from_dfg(self.negated_dfg)
        self.negated_outgoing = get_outgoing_edges(self.negated_dfg)
        self.negated_ingoing = get_ingoing_edges(self.negated_dfg)
        self.detected_cut = None
        self.children = []

        self.detect_cut(log, second_iteration=second_iteration)
