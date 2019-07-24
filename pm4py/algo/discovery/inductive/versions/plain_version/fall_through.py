from pm4py.objects.log import log
import networkx as nx
from pm4py.algo.discovery.inductive.versions.plain_version.data_structures import subtree_plain as subtree

if __name__ == '__main__':
    from pm4py.algo.discovery.inductive.versions.plain_version import subtree_plain

def empty_trace(l):
    # checks if there are empty traces in the log, if so, creates new_log without those empty traces
    contains_empty_trace = False
    for trace in l:
        if len(trace) == 0:
            contains_empty_trace = True

    if contains_empty_trace:
        new_log = log.EventLog()
        for trace in l:
            if len[trace] != 0:
                new_log.append(trace)
        return True, new_log
    else:
        return False, l


def filter_activity_from_trace(l, act):
    # remove the activity from every trace in the log
    # as trace doesnt have remove function, we just create new traces without chosen_activity
    new_log = log.EventLog()
    for trace in l:
        new_trace = log.Trace()
        for event in trace:
            if not event['concept:name'] == act:
                new_trace.append(event)
        new_log.append(new_trace)

    return new_log


def act_once_per_trace(l, activities):
    small_log = log.EventLog()
    small_trace = log.Trace()
    new_log = log.EventLog()
    number_of_traces = len(l)
    possible_activities = list()
    # transform dict of activities to list
    activities_dict = activities
    for key, value in activities_dict.items():
        # if activity appears as often as there are traces, add to list of possible activities:
        if value == number_of_traces:
            possible_activities.append(key)

    chosen_activity = None
    # find an activity that appears exactly once per trace and save it in chose_activity
    for act in possible_activities:
        fits_log = True
        for trace in l:
            fits_trace = False
            for element in trace:
                # enough to check if element occurs once per trace as number of occurrences equals the number of traces
                if act == element['concept:name']:
                    fits_trace = True
            if not fits_trace:
                fits_log = False

        if fits_log:
            chosen_activity = act
            break

    # save the chosen activity in a new trace, so that it can later be appended as leaf to our subtree
    for trace in l:
        if len(small_trace) > 0:
            break
        for element in trace:
            if element['concept:name'] == chosen_activity:
                small_trace.append(element)
                small_log.append(small_trace)
                break

    if chosen_activity is not None:
        new_log = filter_activity_from_trace(l, chosen_activity)
        return True, new_log, small_log
    else:
        return False, new_log, chosen_activity


def activity_concurrent(self, l, activities):
    small_log = log.EventLog()
    small_trace = log.Trace()
    chosen_activity = None
    activities_dict = activities
    for key, value in activities_dict.items():          # iterate through activities (saved in key)
        test_log = filter_activity_from_trace(l, key)
        cut = subtree.SubtreePlain.check_for_cut(self, test_log)            # check if leaving out act, leads to finding a cut
        if cut:
            # save act to small_trace, so that it can be appended as leaf later on
            for trace in l:
                if len(small_trace) > 0:
                    break
                for element in trace:
                    if element['concept:name'] == chosen_activity:
                        small_trace.append(element)
                        small_log.append(small_trace)
                        break

            return True, test_log, small_log                  # if so, return new log

    return False, test_log, small_log      # if,  after iterating through all act's still no cut is found, return false


def split_between_end_and_start(trace, start_activities, end_activities):
    # splits a trace between the first occurrence of an end activity  following a start activity
    found_split = False
    new_trace_1 = log.Trace()
    new_trace_2 = log.Trace()
    i = 0

    while not found_split and i < len(trace)-1:
        if trace[i]['concept:name'] in end_activities and trace[i + 1]['concept:name'] in start_activities:
            found_split = True
            for j in range(0, i):
                new_trace_1.append(trace[j])
            for k in range(i + 1, len(trace)):
                new_trace_2.append(trace[k])
            break
        else:
            i += 1

    return new_trace_1, new_trace_2, found_split


def strict_tau_loop(l, start_activities, end_activities):
    new_log = log.EventLog()
    for trace in l:  # for all traces
        t1, t2, found_split = split_between_end_and_start(trace, start_activities, end_activities)   # look for split
        if found_split:
            new_log.append(t1)
            while found_split:  # if split is found
                t1, t2, found_split = split_between_end_and_start(t2, start_activities,
                                                                  end_activities)  # continue to split
                new_log.append(t1)
        else:
            new_log.append(trace)               # if there is nothing to split, append the whole trace

    if len(new_log) > len(l):
        return True, new_log
    else:
        return False, new_log


def split_before_start(trace, start_activities):
    found_split = False
    new_trace_1 = log.Trace()
    new_trace_2 = log.Trace()
    i = 1
    while not found_split and i < len(trace):  # for all events in trace
        if trace[i]['concept:name'] in start_activities and len(trace) > 1:
            found_split = True
            for j in range(0, i):
                new_trace_1.append(trace[j])
            for k in range(i, len(trace)):
                new_trace_2.append(trace[k])
        i += 1

    return new_trace_1, new_trace_2, found_split


def tau_loop(l, start_activities):
    # pretty much the same code as in strict_tau_loop, just that we split at a different point
    new_log = log.EventLog()
    for trace in l:
        t1, t2, found_split = split_before_start(trace, start_activities)
        if found_split and len(t2) != 0:
            new_log.append(t1)
            while found_split:
                t1, t2, found_split = split_before_start(t2, start_activities)
                new_log.append(t1)
        else:
            new_log.append(trace)

    if len(new_log) > len(l):
        return True, new_log
    else:
        return False, new_log
