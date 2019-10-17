import joblib
from pm4py.algo.simulation.tree_generator import factory as tree_gen
import pm4py
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.algo.discovery.inductive.versions.infrequent import im_infrequent as imf
from pm4py.algo.discovery.inductive.versions.plain_version import im_plain as imp
from pm4py.algo.simulation.playout import factory as playout_factory
from pm4py.algo.discovery.inductive.versions.plain_version import splitting as split


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