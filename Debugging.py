import os
import pm4py
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.discovery.inductive.versions.infrequent import im_infrequent as imf
from pm4py.algo.discovery.inductive.versions.plain_version import im_plain as imp
from pm4py.objects.conversion.log import factory as conv_factory
from pm4py.objects.log.importer.csv import factory as csv_importer
from pm4py.objects.log.importer.xes import factory as xes_import_factory
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
import joblib
from pm4py.algo.simulation.playout import factory as playout_factory
from pm4py.algo.discovery.inductive.versions.infrequent.splitting_infrequent import show_nice_log as nice_log
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.evaluation.replay_fitness import factory as fitness_factory
from pm4py.evaluation.generalization import factory as generalization_factory
from pm4py.evaluation.simplicity import factory as simple_factory
from pm4py.evaluation.precision import factory as precision_factory
from pm4py.algo.discovery.inductive.util.add_noise_to_log import introduce_deviations
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py import util as pmutil
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.inductive.versions.infrequent import splitting_infrequent as split
from pm4py.algo.discovery.inductive.versions.plain_version import fall_through
from pm4py.algo.conformance.tokenreplay import factory as token_replay
from pm4py.objects.log import log
from pm4py.algo.discovery.inductive.versions.plain_version.data_structures import subtree_plain
from pm4py.algo.simulation.tree_generator import factory as tree_gen



l = joblib.load("debug_log")
print("length log: ", len(l))
length = 0
for tr in l:
    length += len(tr)
avg_trace_length = length/len(l)
print("avg_trace_length: ", avg_trace_length)
activities = []
for trace in l:
    for act in trace:
        if act['concept:name'] not in activities:
            activities.append(act['concept:name'])
print("no of activitys: ", len(activities))
tree1 = imp.apply_im_plain(l, None)
print(tree1)
net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree1)

log_with_traces_only_once = []
for trace in l:
    if split.show_nice_trace(trace) not in log_with_traces_only_once:
        log_with_traces_only_once.append(split.show_nice_trace(trace))
#print(len(l), len(log_with_traces_only_once))
#print(log_with_traces_only_once)

unfit = []
bad_log = log.EventLog()
for trace in l:
    if split.show_nice_trace(trace) in log_with_traces_only_once:
        replay_result = token_replay.apply([trace], net1, initial_marking1, final_marking1)
        if replay_result[0]["trace_fitness"] != 1:
            unfit.append((split.show_nice_trace(trace), list(replay_result)))
            bad_log.append(trace)
        log_with_traces_only_once.remove(split.show_nice_trace(trace))
print(unfit)
print("bad log: ", split.show_nice_log(bad_log))
joblib.dump(bad_log, "debug_log", compress=3)
print(fitness_factory.apply(l, net1, initial_marking1, final_marking1))
"""

for i in range(1, 100):
    print(i)
    random_tree = tree_gen.apply()
    net, initial_marking, final_marking = imp.apply_plain_petrinet(random_tree)
    random_log = playout_factory.apply(net, initial_marking, parameters={"noTraces": 10, "maxTraceLength": 40})
    tree = imp.apply_im_plain(random_log, None)
    net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree)
    fitness1 = fitness_factory.apply(random_log, net1, initial_marking1, final_marking1)
    print(fitness1['log_fitness'])
    if fitness1['log_fitness'] != 1:
        print("whuuuuuuuuuupps da läuft was schief")
        joblib.dump(random_log, "debug_log", compress=3)
        break

print("finished")
"""