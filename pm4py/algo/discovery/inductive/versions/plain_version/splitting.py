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
        if len(lo[0]) != 0:
            new_logs.append(lo)

    return new_logs  # new_logs is a list that contains logs


def split_sequence(cut, l):
    new_logs = list()
    for c in cut:                                       # for cut partition
        lo = log.EventLog()
        for trace in l:                               # for all traces
            trace_new = log.Trace()
            j = 0
            while j < len(trace):                     # for all events
                if trace[j]['concept:name'] in c:
                    while trace[j]['concept:name'] in c:    # append as long as contained in current cut partition
                        trace_new.append(trace[j])
                        if j+1 < len(trace):
                            j += 1
                        else:
                            j += 1
                            break
                else:
                    j += 1
            if len(trace_new) != 0:
                lo.append(trace_new)
        if len(lo[0]) != 0:
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
            if len(trace_new) != 0:
                lo.append(trace_new)
        if len(lo[0]) != 0:
            new_logs.append(lo)
    return new_logs


def split_loop(cut, l):
    # TODO fix this fucntion
    new_logs = []
    for c in cut:                                               # for cut partition
        lo = log.EventLog()
        for i in range(0, len(l)):                              # for all traces
            for j in range(0, len(l[i])):                       # for all events
                if l[i][j]['concept:name'] in c:
                    trace_new = log.Trace()
            # declared here and not above, so that we can generate multiple traces from one trace and cut (repetition)
            # append those events that are contained in c:
                    while l[i][j]['concept:name'] in c:
                        trace_new.append(l[i][j])
                        if j+1 < len(l[i]):
                            j += 1
                        else:
                            j += 1
                            break
                    if len(trace_new) != 0:
                        lo.append(trace_new)
        if len(lo) != 0:
            new_logs.append(lo)

    return new_logs