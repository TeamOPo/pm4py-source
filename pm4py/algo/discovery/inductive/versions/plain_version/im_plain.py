from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.dfg.util import get_tree_repr_imdfb
from pm4py.algo.discovery.inductive.versions.plain_version.data_structures import subtree_plain as subtree
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.versions import native as dfg_inst


def apply_im_plain(log):
    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
    c = Counts()
    noise_threshold = shared_constants.NOISE_THRESHOLD
    activity_key = xes_util.DEFAULT_NAME_KEY
    activities = attributes_filter.get_attribute_values(log, activity_key)
    start_activities = list(start_activities_filter.get_start_activities(log, parameters=None).keys())
    end_activities = list(end_activities_filter.get_end_activities(log, parameters=None).keys())
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    sub = subtree.make_tree(log, dfg, dfg, dfg, activities, c, noise_threshold, start_activities, end_activities,
                            start_activities, end_activities)

    tree_repr = get_tree_repr_imdfb.get_repr(sub, 0, contains_empty_traces=contains_empty_traces)
    return tree_repr

