def empty_log(log):
    if len(log) == 0:
        return True
    else:
        return False


def single_activity(log):
    if log[0] is not None:
        first_trace = log[0]
        first_activity = log[0][0]['concept:name']
        for i in range(0, len(log)-1):
            if len(log[i]) != 1 or log[i][0]['concept:name'] != first_activity:
                return False                # if there is a trace that has a length not equal to 1, we return false

        # check if all traces consist of the same activity, therefore create dfg from log and get activities of that dfg
        return True
    else:
        return False