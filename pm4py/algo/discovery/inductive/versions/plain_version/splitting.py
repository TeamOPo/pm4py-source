from pm4py.objects.log import log
from copy import deepcopy


def split_xor(cut, l):
    new_logs = []
    for c in cut:  # for cut partition
        lo = log.EventLog()
        for i in range(0, len(l)):  # for trace in log
            fits = True
            for j in range(0, len(l[i])):  # for event in trace
                if l[i][j]['concept:name'] not in c:
                    fits = False  # if not every event fits the current cut-partition, we don't add it's trace
            if fits:
                lo.append(l[i])
        new_logs.append(lo)

    return new_logs  # new_logs is a list that contains logs


def split_parallel(cut, l):
    new_logs = []
    for c in cut:
        lo = log.EventLog()
        for trace in l:
            new_trace = log.Trace()
            for event in trace:
                if event['concept:name'] in c:
                    new_trace.append(event)
            lo.append(new_trace)
        new_logs.append(lo)
    return new_logs


def split_sequence(cut, l):
    new_logs = []
    for c in cut:  # for all cut-partitions
        lo = log.EventLog()
        for trace in l:  # for all traces in the log
            not_in_c = True
            trace_new = log.Trace()
            for j in range(0, len(trace)):  # for every event in the current trace
                if trace[j]['concept:name'] in c:
                    not_in_c = False
                    while trace[j]["concept:name"] in c:
                        trace_new.append(trace[j])  # we only add the events that match the cut partition
                        if j + 1 < len(trace):
                            j += 1
                        else:
                            j += 1
                            break
                    lo.append(trace_new)
                    break
            if not_in_c:
                lo.append(trace_new)
        new_logs.append(lo)
        nice_log = show_nice_log(lo)
    if len(new_logs) > 0:
        return new_logs
    else:
        print('split_parallel failed')


def split_loop(cut, l):
    new_logs = []
    for c in cut:  # for cut partition
        lo = log.EventLog()
        for trace in l:  # for all traces
            j = 0
            while j in range(0, len(trace)):  # for all events
                if trace[j]['concept:name'] in c:
                    trace_new = log.Trace()
                    # declared here and not above, so that we can generate multiple traces from one trace and
                    # cut (repetition)
                    # append those events that are contained in c:
                    while trace[j]['concept:name'] in c:
                        trace_new.append(trace[j])
                        if j + 1 < len(trace):
                            j += 1
                        else:
                            j += 1
                            break
                    lo.append(trace_new)
                else:
                    j += 1

        if len(lo) != 0:
            new_logs.append(lo)

    return new_logs


def show_nice_trace(trace):
    # returns nice representation of trace, to make sure we don't add doubles in the splitting functions
    nt = []
    for element in trace:
        nt.append(element['concept:name'])
    return nt


def show_nice_log(l):
    nl = []
    for trace in l:
        nt = []
        for element in trace:
            nt.append(element['concept:name'])
        nl.append(nt)

    return nl
