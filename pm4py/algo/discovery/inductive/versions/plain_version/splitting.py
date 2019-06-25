

def split_log(str, cut, log):
    if str == "xor":
        return split_xor(cut, log)

    elif str == "sequential":
        return  split_sequence(cut, log)

    elif str == "parallel":
        return split_parallel(cut, log)

    elif str == "loop":
        return split_loop(cut, log)

def split_xor(cut, log):
    logs = ()
    for c in cut:
        l = list()
        for trace in log:
            trace_new = trace
            for act in trace_new:
                if act not in c:
                    trace_new.remove(act)
            l.append(trace_new)
        logs.append(l)

    return logs

def split_sequence(cut, log):

def  split_parallel(cut, log):

def split_loop(cut, log):