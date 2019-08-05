from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.util import shared_constants
from pm4py.algo.discovery.inductive.util.petri_el_count import Counts
from pm4py.algo.discovery.inductive.versions.plain_version import get_tree_repr_implain
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.discovery.inductive.versions.infrequent.data_structures import subtree_infrequent as subtree


def apply_im_infrequent(log, f, parameters):
    if parameters is None:
        parameters = {}
    if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
    if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
        parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
    dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
    c = Counts()
    activity_key = xes_util.DEFAULT_NAME_KEY
    activities = attributes_filter.get_attribute_values(log, activity_key)
    start_activities = list(start_activities_filter.get_start_activities(log, parameters=None).keys())
    end_activities = list(end_activities_filter.get_end_activities(log, parameters=None).keys())
    contains_empty_traces = False
    traces_length = [len(trace) for trace in log]
    if traces_length:
        contains_empty_traces = min([len(trace) for trace in log]) == 0

    # set the threshold parameter based on f and the max value in the dfg:
    max_value = 0
    for key, value in dfg:
        if value > max_value:
            max_value = value
    threshold = f * max_value

    recursion_depth = 0
    print('starting with dfg: ', dfg)
    sub = subtree.make_tree(log, dfg, dfg, dfg, activities, c, recursion_depth, f, threshold, start_activities, end_activities,
                            start_activities, end_activities)

    tree_repr = get_tree_repr_implain.get_repr(sub, 0, contains_empty_traces=contains_empty_traces)
    return tree_repr
