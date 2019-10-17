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



print(joblib.load("E1_T1_8_8"))
print(joblib.load("E1_T1_8_16"))
print(joblib.load("E1_T_16_4"))
print(joblib.load("E1_T_16_8"))
print(joblib.load("E1_T_16_16"))



"""
# generating logs:
def generate_log():
    random_tree = tree_gen.apply()
    net, initial_marking, final_marking = imp.apply_plain_petrinet(random_tree)
    random_log = playout_factory.apply(net, initial_marking, parameters={"noTraces": 10, "maxTraceLength": 40})
    length = 0
    for tr in random_log:
        length += len(tr)
    avg_trace_length = length/len(random_log)
    good_length = False
    if 20 > avg_trace_length > 3:
        good_length = True

    return good_length, random_log, random_tree, avg_trace_length


while True:
    good_l, random_l, random_t, avg = generate_log()
    if good_l:
        print(good_l, avg)
        activities = []
        for trace in random_l:
            for act in trace:
                if act['concept:name'] not in activities:
                    activities.append(act['concept:name'])
        print(len(activities))
        if 7 > len(activities) > 3:
            tree = imp.apply_im_plain(random_l, None)
            net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree)
            fitness1 = fitness_factory.apply(random_l, net1, initial_marking1, final_marking1)
            print(fitness1['log_fitness'])
            if fitness1['log_fitness'] != 1:
                print("avg trace length ", avg)
                print('fitness: ', fitness1['log_fitness'])
                print(len(activities), activities)
                print(random_t)
                break

joblib.dump(random_t, "debug_tree", compress=3)
joblib.dump(random_l, "debug_log", compress=3)

"""



"""
# load logs
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "roadtraffic100traces.csv"))
E1_8_4 = conv_factory.apply(stream)
E1_8_8 = joblib.load("E1_8_8_noise_20")
E1_8_16 = joblib.load("E1_8_16_noise_20")
E1_16_4 = joblib.load("E1_16_4_noise_20")
E1_16_8 = joblib.load("E1_16_8_noise_20")
E1_16_16 = joblib.load("E1_16_16_noise_20")


logs = [E1_8_4, E1_8_8, E1_8_16, E1_16_4, E1_16_8, E1_16_16]
for log in logs:
    activities = []
    for trace in log:
        for act in trace:
            if act['concept:name'] not in activities:
                activities.append(act['concept:name'])
    tree = imp.apply_im_plain(log, None)
    net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree)
    fitness1 = fitness_factory.apply(log, net1, initial_marking1, final_marking1)
    length = 0
    for trace in log:
        length += len(trace)
    avg_trace_length = length / len(log)

    print(fitness1['log_fitness'], "#activities = ", len(activities), "average tace lenght = ", avg_trace_length)












# add noise:
noise_parameters = {"p_dev_activity": 0.5, "p_dev_time": 0.5, "p_dev_additional": 0.5}
E1_8_4_noise_10 = introduce_deviations(E1_8_4, noise_parameters)
t1 = imp.apply_im_plain(E1_8_4_noise_10, None)
joblib.dump(E1_8_4, "E1_8_4_noise_10", compress=3)
joblib.dump(t1, "E1_8_4t", compress=3)
E1_8_8_noise_10 = introduce_deviations(E1_8_8, noise_parameters)
t2 = imp.apply_im_plain(E1_8_8_noise_10, None)
joblib.dump(E1_8_4, "E1_8_8_noise_10", compress=3)
joblib.dump(t2, "E1_8_4t", compress=3)
E1_8_16_noise_10 = introduce_deviations(E1_8_16, noise_parameters)
t3 = imp.apply_im_plain(E1_8_16_noise_10, None)
joblib.dump(E1_8_16, "E1_8_16_noise_10", compress=3)
joblib.dump(t3, "E1_8_16t", compress=3)
E1_16_4_noise_10 = introduce_deviations(E1_16_4, noise_parameters)
t4 = imp.apply_im_plain(E1_16_4_noise_10, None)
joblib.dump(E1_16_4, "E1_16_4_noise_10", compress=3)
joblib.dump(t4, "E1_16_4t", compress=3)
E1_16_8_noise_10 = introduce_deviations(E1_16_8, noise_parameters)
t5 = imp.apply_im_plain(E1_16_8_noise_10, None)
joblib.dump(E1_16_8, "E1_16_8_noise_10", compress=3)
joblib.dump(t5, "E1_16_8t", compress=3)
E1_16_16_noise_10 = introduce_deviations(E1_16_16, noise_parameters)
t6 = imp.apply_im_plain(E1_16_16_noise_10, None)
joblib.dump(E1_16_16, "E1_16_16_noise_10", compress=3)
joblib.dump(t, "E1_16_16t", compress=3)
"""


"""
# load logs
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "roadtraffic100traces.csv"))
E1_8_4 = conv_factory.apply(stream)
E1_8_8 = joblib.load("E1_8_8")
E1_8_16 = joblib.load("E1_8_16")
E1_16_4 = joblib.load("E1_16_4")
E1_16_8 = joblib.load("E1_16_8")
E1_16_16 = joblib.load("E1_16_16")

E1_8_4_10 = joblib.load("E1_8_4_10")
E1_8_8_10 = joblib.load("E1_8_8_10")
E1_8_16_10 = joblib.load("E1_8_16_10")
E1_16_4_10 = joblib.load("E1_16_4_10")
E1_16_8_10 = joblib.load("E1_16_8_10")
E1_16_16_10 = joblib.load("E1_16_16_10")


# generate models:
tree1 = imp.apply_im_plain(E1_8_4, None)
tree2 = imp.apply_im_plain(E1_8_8, None)
tree3 = imp.apply_im_plain(E1_8_16, None)
tree4 = imp.apply_im_plain(E1_16_4, None)
tree5 = imp.apply_im_plain(E1_16_8, None)
tree6 = imp.apply_im_plain(E1_16_16, None)

net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree1)
net2, initial_marking2, final_marking2 = imp.apply_plain_petrinet(tree2)
net3, initial_marking3, final_marking3 = imp.apply_plain_petrinet(tree3)
net4, initial_marking4, final_marking4 = imp.apply_plain_petrinet(tree4)
net5, initial_marking5, final_marking5 = imp.apply_plain_petrinet(tree5)
net6, initial_marking6, final_marking6 = imp.apply_plain_petrinet(tree6)


# measure quality of models
fitness1 = fitness_factory.apply(E1_8_4, net1, initial_marking1, final_marking1)
fitness2 = fitness_factory.apply(E1_8_8, net2, initial_marking2, final_marking2)
fitness3 = fitness_factory.apply(E1_8_16, net3, initial_marking3, final_marking3)
fitness4 = fitness_factory.apply(E1_16_4, net4, initial_marking4, final_marking4)
fitness5 = fitness_factory.apply(E1_16_8, net5, initial_marking5, final_marking5)
fitness6 = fitness_factory.apply(E1_16_16, net6, initial_marking6, final_marking6)
print('fitness: ', fitness1['log_fitness'], fitness2['log_fitness'], fitness3['log_fitness'], fitness4['log_fitness'])
simplicity1 = simple_factory.apply(net1)
simplicity2 = simple_factory.apply(net2)
simplicity3 = simple_factory.apply(net3)
simplicity4 = simple_factory.apply(net4)
simplicity5 = simple_factory.apply(net5)
simplicity6 = simple_factory.apply(net6)
print('simplicity: ', simplicity1,  simplicity2, simplicity3, simplicity4, simplicity5, simplicity6)
generalization1 = generalization_factory.apply(E1_8_4,  net1, initial_marking1, final_marking1)
generalization2 = generalization_factory.apply(E1_8_8,  net2, initial_marking2, final_marking2)
generalization3 = generalization_factory.apply(E1_8_16,  net3, initial_marking3, final_marking3)
generalization4 = generalization_factory.apply(E1_16_4,  net4, initial_marking4, final_marking4)
generalization5 = generalization_factory.apply(E1_16_8,  net5, initial_marking5, final_marking5)
generalization6 = generalization_factory.apply(E1_16_16,  net6, initial_marking6, final_marking6)
print('generalization: ', generalization1, generalization2, generalization3, generalization4, generalization5, 
    generalization6)
precision1 = precision_factory.apply(E1_8_4, net, initial_marking, final_marking)
precision2 = precision_factory.apply(E1_8_8, net, initial_marking, final_marking)
precision3 = precision_factory.apply(E1_8_16, net, initial_marking, final_marking)
precision4 = precision_factory.apply(E1_16_4, net, initial_marking, final_marking)
precision5 = precision_factory.apply(E1_16_8, net, initial_marking, final_marking)
precision6 = precision_factory.apply(E1_16_16, net, initial_marking, final_marking)
print('precision: ', precision1, precision2, precision3, precision4, precision_5, precision_6)

"""


