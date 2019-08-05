from pm4py.algo.discovery.inductive.versions.plain_version import base_case


def single_activity_infrequent(log, noise_threshold):
    if base_case.single_activity(log):
        activity = log[0][0]['concept:name']
        number_of_traces = len(log)
        number_of_events = 0
        for trace in log:
            number_of_traces += len(trace)
        p = number_of_traces/(number_of_traces+number_of_events)
        if p-0.5 <= noise_threshold:
            return True, activity
    else:
        return False, None
