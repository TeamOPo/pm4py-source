from pm4py.objects.log import log


def show_nice_trace(trace):
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


def show_nice_logs(ls):
    nls = []
    for l in ls:
        nl = []
        for trace in l:
            nt = []
            for element in trace:
                nt.append(element['concept:name'])
            nl.append(nt)
        nls.append(nl)
    return nls


def filter_trace_on_cut_partition(trace, partition):
    filtered_trace = log.Trace()
    for event in trace:
        if event['concept:name'] in partition:
            filtered_trace.append(event)
    return filtered_trace


def find_split_point(trace, cut_partition, start, ignore):
    possibly_best_before_first_activity = False
    nice_trace = show_nice_trace(trace)
    least_cost = start
    position_with_least_cost = start
    cost = float(0)
    for i in range(start, len(trace)):
        if trace[i]['concept:name'] in cut_partition:
            cost = cost-1
        elif trace[i]['concept:name'] not in ignore:
            # use bool variable for the case, that the best split is before the first activity
            if i == 0:
                possibly_best_before_first_activity = True
            cost = cost+1
        if cost < least_cost:
            least_cost = cost
            position_with_least_cost = i+1
    if possibly_best_before_first_activity and position_with_least_cost == 1:
        position_with_least_cost = 0
    return position_with_least_cost


def cut_trace_between_two_points(trace, point_a, point_b):
    nice_trace = show_nice_trace(trace)
    cutted_trace = log.Trace()
    # we have to use <= although in the paper the intervall is [) because our index starts at 0
    while point_a < point_b:
        cutted_trace.append(trace[point_a])
        add_act = trace[point_a]['concept:name']
        show_nice_cutted_trace = show_nice_trace(cutted_trace)
        point_a += 1

    return cutted_trace


def split_xor_infrequent(cut, l):
    # TODO think of empty logs
    # creating the empty L_1,...,L_n from the second code-line on page 205
    n = len(cut)
    new_logs = [log.EventLog() for i in range(0, n)]
    print('new_logs: ', new_logs)
    for trace in l:                                                 # for all traces
        number_of_events_in_trace = 0
        index_of_cut_partition = 0
        i = 0
        # use i as index here so that we can write in L_i
        for i in range(0, len(cut)):                                # for all cut partitions
            temp_counter = 0
            for event in trace:                                     # for all events in current trace
                if event['concept:name'] in cut[i]:                 # count amount of events from trace in partition
                    temp_counter += 1
            if temp_counter > number_of_events_in_trace:
                number_of_events_in_trace = temp_counter
                index_of_cut_partition = i
        filtered_trace = filter_trace_on_cut_partition(trace, cut[i])
        new_logs[index_of_cut_partition].append(filtered_trace)


def split_sequence_infrequent(cut, l):
    # write L_1,...,L_n like in second line of code on page 206
    n = len(cut)
    new_logs = [log.EventLog() for j in range(0, n)]
    ignore = []
    for i in range(0, n):
        split_point = 0
        # write our ignore list with all elements from past cut partitions
        if i != 0:
            for element in cut[i-1]:
                ignore.append(element)
        for trace in l:
            new_split_point = find_split_point(trace, cut[i], split_point, ignore)
            cutted_trace = cut_trace_between_two_points(trace, split_point, new_split_point)
            filtered_trace = filter_trace_on_cut_partition(cutted_trace, cut[i])
            new_logs[i].append(filtered_trace)
    return new_logs


def split_loop_infrequent(cut, l):
    n = len(cut)
    new_logs = [log.EventLog() for i in range(0, n)]
    for trace in l:
        s = cut[0]
        st = log.Trace()
        for act in trace:
            if act in s:
                st.insert(act)
            else:
                j = 0
                for j in range(0, len(cut)):
                    if cut[j] == s:
                        break
                new_logs[j].append(st)
                st = log.Trace()
                for partition in cut:
                    if act in partition:
                        s.append(partition)
        # L_j <- L_j + [st] with sigma_j = s
        j = 0
        for j in range(0, len(cut)):
            if cut[j] == s:
                break
        new_logs[j].append(st)
        if s != cut[0]:
            new_logs[0].append(log.EventLog())

    return new_logs