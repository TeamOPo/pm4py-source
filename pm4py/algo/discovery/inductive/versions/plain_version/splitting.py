from pm4py.objects.log import log


def split_xor(cut, l):
    new_logs = list()
    for c in cut:                               # for cut partition
        lo = log.EventLog()
        for i in range(0, len(l)):              # for trace in log
            fits = True
            for j in range(0, len(l[i])):       # for event in trace
                if l[i][j]['concept:name'] not in c:
                    fits = False            # if not every event fits the current cut-partition, we don't add it's trace
            if fits:
                lo.append(l[i])
        new_logs.append(lo)

    return new_logs  # new_logs is a list that contains logs


def split_sequence(cut, l):
    new_logs = list()
    for c in cut:                                       # for cut partition
        lo = log.EventLog()
        for i in range(0, len(l)):                      # for all traces
            trace_new = log.Trace()
            for j in range(0, len(l[i])):               # for all events
                if l[i][j]['concept:name'] in c:
                    while l[i][j] in c:
                        trace_new.append(l[i][j])       # only append those events of the trace, that are contained in c
            lo.append(trace_new)
        new_logs.append(lo)

    return new_logs


def split_parallel(cut, l):
    new_logs = list()
    for c in cut:                               # for all cut-partitions
        lo = log.EventLog()
        for i in range(0, len(l)):              # for all traces in the log
            trace_new = log.Trace()
            for j in range(0, len(l[i])):       # for every event in the current trace
                if l[i][j]['concept:name'] in c:
                    trace_new.append(l[i][j])  # we only add the events that match the cut partition
            lo.append(trace_new)
        new_logs.append(lo)

    return new_logs


def split_loop(cut, l):
    new_logs = list()
    for c in cut:  # for cut partition
        lo = log.EventLog()
        for i in range(0, len(l)):  # for all traces
            for j in range(0, len(l[i])):  # for all events
                if l[i][j]['concept:name'] in c:
                    trace_new = log.Trace()
            # declared here and not above, so that we can generate multiple traces from one trace and cut (repetition)
            # append those events that are contained in c:
                    while l[i][j] in c:
                        trace_new.append(l[i][j])
                        j += 1
                    lo.append(trace_new)
        new_logs.append(lo)

    return new_logs