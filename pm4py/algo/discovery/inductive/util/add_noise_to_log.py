import random
from random import randint
import numpy as np
from pm4py.algo.discovery.inductive.versions.plain_version.fall_through import show_nice_log
import copy


def introduce_deviations(logf, parameters):
    log = copy.deepcopy(logf)
    act_labels = []

    #generate random indexes:
    random_index = []
    if len(log) < 10:
        number_of_changed_traces = len(log)/3
    else:
        number_of_changed_traces = len(log)/8
    for i in range(0, int(number_of_changed_traces)):
        random_number = randint(0, len(log)-1)
        random_index.append(random_number)
    print("random index: ", random_index)

    for trace in log:
        for element in trace:
            if element['concept:name'] not in act_labels:
                act_labels.append(element['concept:name'])

    if parameters is None:
        parameters = {}
    p_dev_activity = parameters["p_dev_activity"] if "p_dev_activity" in parameters else 0
    p_dev_time = parameters["p_dev_time"] if "p_dev_time" in parameters else 0
    p_dev_additional = parameters["p_dev_additional"] if "p_dev_additional" in parameters else 0
    for j in random_index:
        trace = log[j]
        for i in range(0, len(trace)):
            if i % 2 == 1 and random.random() < p_dev_time:
                temp = trace[i]["concept:name"]
                trace[i]["concept:name"] = trace[i-1]["concept:name"]
                trace[i-1]["concept:name"] = temp
            if random.random() < p_dev_activity:
                other_activities = [label for label in act_labels if label != trace[i]["concept:name"]]
                trace[i]["concept:name"] = random.choice(other_activities)
        if random.random() < p_dev_additional:
            trace.append(dict(trace[len(trace)-1]))
            this_timestamp = int(((np.datetime64(trace[len(trace)-1]["time:timestamp"]) - np.datetime64(0, 's')) / np.timedelta64(1, 's')))
            trace[len(trace) - 1]["time:timestamp"] = np.datetime64(this_timestamp + random.randrange(60000, 86400), "s")

    return log