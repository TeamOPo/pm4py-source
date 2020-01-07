import joblib
from pm4py.algo.simulation.tree_generator import factory as tree_gen
import pm4py
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.discovery.inductive.versions.infrequent import im_infrequent as imf
from pm4py.algo.discovery.inductive.versions.plain_version import im_plain as imp
from pm4py.algo.simulation.playout import factory as playout_factory
from pm4py.algo.discovery.inductive.versions.plain_version import splitting as split
import time
from functools import wraps
from pm4py.algo.simulation.tree_generator import factory as tree_gen_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.objects.conversion.process_tree import factory as pt_conv_factory
from pm4py.algo.simulation.playout import factory as playout_factory
from statistics import median


"""
parameters = {"min_rec_depth": 200}
random_tree = tree_gen.apply()
net, initial_marking, final_marking = imp.apply_plain_petrinet(random_tree)
random_log = playout_factory.apply(net, initial_marking, parameters={"noTraces": 10, "maxTraceLength": 200,
                                                                     "min_trace_length": 20})
print("log length: ", len(random_log))
# print("log: ", split.show_nice_log(random_log))
length = 0
for trace in random_log:
    length += len(trace)
print("avg trace length: ", length/len(random_log))
print(random_tree)

joblib.dump(random_log, "runtime2.4", compress=3)


while True:
    tree = tree_gen_factory.apply(variant="basic", parameters={"prob_leaf": 0.5, "max_rec_depth": 10})
    net, im, fm = pt_conv_factory.apply(tree)

    log = playout_factory.apply(net, im, parameters={"noTraces": 100, "maxTraceLength": 70})
    len_traces = [len(x) for x in log]
    length = 0
    for trace in log:
        length += len(trace)
    print("avg trace length: ", length / len(log))
    if 10.5 > length / len(log) > 9.5:
        length = 0
        for trace in log:
            length += len(trace)
        print("avg trace length: ", length / len(log))
        joblib.dump(log, "runtime1.10", compress=3)
        break

l1_10 = joblib.load("runtime1.10")
print(len(l1_10))
l2_10 = joblib.load("runtime2.10")
print(len(l2_10))
"""



lo = joblib.load("runtime1.2")
start_time = time.time()
#tree = inductive_miner.apply_tree(lo, None)
#tree = imp.apply_im_plain(lo, None)
tree = imf.apply_im_infrequent(lo, 0.9, None)
print("%f seconds" % (time.time() - start_time))



