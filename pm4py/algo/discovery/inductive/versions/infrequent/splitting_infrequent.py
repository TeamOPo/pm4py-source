from pm4py.objects.log import log


def filter_trace_on_cut_partition(trace, partition):
    filtered_trace = log.Trace()
    for event in trace:
        if event['concept:name'] in partition:
            filtered_trace.append(event)
    return filtered_trace


def find_split_point(trace, cut_partition, start, ignore):
    least_cost = start
    position_with_least_cost = start
    cost = 0
    for i in range(start, len(trace)):
        if trace[i] in cut_partition:
            cost = cost-1
        elif trace[i] not in ignore:
            cost = cost+1
        if cost < least_cost:
            least_cost = cost
            position_with_least_cost = i
    return position_with_least_cost


def cut_trace_between_two_points(trace, point_a, point_b):
    cutted_trace = log.Trace()
    for i in range(point_a, point_b-1):
        cutted_trace.append(trace[i])
    return cutted_trace


def split_xor_infrequent(cut, l):
    # TODO think of empty logs
    # creating the empty L_1,...,L_n from the second code-line on page 205
    empty_log = log.EventLog
    n = len(cut)
    new_logs = [empty_log for i in range(0, n)]
    # TODO did this work?
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
    empty_log = log.EventLog
    n = len(cut)
    new_logs = [empty_log for i in range(0, n)]
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
            split_point = new_split_point

    return new_logs


def split_loop_infrequent(cut, l):
    empty_log = log.EventLog
    n = len(cut)
    new_logs = [empty_log for i in range(0, n)]
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
            new_logs[0].append(empty_log)

    return new_logs