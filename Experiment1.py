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
import csv


# generating logs:
"""
def generate_log():
    random_tree = tree_gen.apply()
    net, initial_marking, final_marking = imp.apply_plain_petrinet(random_tree)
    random_log = playout_factory.apply(net, initial_marking, parameters={"noTraces": 100, "maxTraceLength": 40})
    length = 0
    for tr in random_log:
        length += len(tr)
    avg_trace_length = length/len(random_log)
    good_length = False
    if 16.5 > avg_trace_length > 15.5:
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
        if len(activities) == 8:
            tree = imp.apply_im_plain(random_l, None)
            net1, initial_marking1, final_marking1 = imp.apply_plain_petrinet(tree)
            fitness1 = fitness_factory.apply(random_l, net1, initial_marking1, final_marking1)
            print(fitness1['log_fitness'])
            if fitness1['log_fitness'] == 1:
                print("avg trace length ", avg)
                print('fitness: ', fitness1['log_fitness'])
                print(len(activities), activities)
                print(random_t)
                break

joblib.dump(random_t, "E1_8_16t", compress=3)
joblib.dump(random_l, "E1_8_16", compress=3)

# add noisy logs
E1_8_16 = joblib.load("E1_8_16")
noise_parameters = {"p_dev_activity": 0.5, "p_dev_time": 0.5, "p_dev_additional": 0.5}
E1_8_16_noise_10 = introduce_deviations(E1_8_16, noise_parameters)
t3 = imp.apply_im_plain(E1_8_16, None)
net3, initial_marking3, final_marking3 = imp.apply_plain_petrinet(t3)

joblib.dump(E1_8_16_noise_10, "E1_8_16_noise_20", compress=3)
joblib.dump(t3, "E1_8_16t_20", compress=3)
net3, initial_marking3, final_marking3 = imp.apply_plain_petrinet(t3)
print("starting  precision calculation")

precision3 = precision_factory.apply(E1_8_16, net3, initial_marking3, final_marking3)
print(precision3)
print("finished precision calculation")


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


# load logs and add noise:

stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "roadtraffic100traces.csv"))
E1_8_4 = conv_factory.apply(stream)
E1_8_8 = joblib.load("E1_8_8")
E1_8_16 = joblib.load("E1_8_16")
E1_16_4 = joblib.load("E1_16_4")
E1_16_8 = joblib.load("E1_16_8")
E1_16_16 = joblib.load("E1_16_16")


noise_parameters = {"p_dev_activity": 0.5, "p_dev_time": 0.5, "p_dev_additional": 0.5}
E1_8_4_noise_10 = introduce_deviations(E1_8_4, noise_parameters)
t1 = imp.apply_im_plain(E1_8_4_noise_10, None)
joblib.dump(E1_8_4_noise_10, "E1_8_4_noise_10", compress=3)
joblib.dump(t1, "E1_8_4t_10", compress=3)

E1_8_8_noise_10 = introduce_deviations(E1_8_8, noise_parameters)
t2 = imp.apply_im_plain(E1_8_8_noise_10, None)
joblib.dump(E1_8_4_noise_10, "E1_8_8_noise_10", compress=3)
joblib.dump(t2, "E1_8_8t_10", compress=3)

E1_8_16_noise_10 = introduce_deviations(E1_8_16, noise_parameters)
t3 = imp.apply_im_plain(E1_8_16_noise_10, None)
joblib.dump(E1_8_16_noise_10, "E1_8_16_noise_10", compress=3)
joblib.dump(t3, "E1_8_16t_10", compress=3)

E1_16_4_noise_10 = introduce_deviations(E1_16_4, noise_parameters)
t4 = imp.apply_im_plain(E1_16_4_noise_10, None)
joblib.dump(E1_16_4_noise_10, "E1_16_4_noise_10", compress=3)
joblib.dump(t4, "E1_16_4t_10", compress=3)

E1_16_8_noise_10 = introduce_deviations(E1_16_8, noise_parameters)
t5 = imp.apply_im_plain(E1_16_8_noise_10, None)
joblib.dump(E1_16_8_noise_10, "E1_16_8_noise_10", compress=3)
joblib.dump(t5, "E1_16_8t_10", compress=3)

E1_16_16_noise_10 = introduce_deviations(E1_16_16, noise_parameters)
t6 = imp.apply_im_plain(E1_16_16_noise_10, None)
joblib.dump(E1_16_16_noise_10, "E1_16_16_noise_10", compress=3)
joblib.dump(t6, "E1_16_16t_10", compress=3)
"""


# load logs and generate models
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "roadtraffic100traces.csv"))
E1_8_4_noise_10 = conv_factory.apply(stream)
#E1_8_4_noise_10 = joblib.load("E1_8_4")
E1_8_8_noise_10 = joblib.load("E1_8_8")
E1_8_16_noise_10 = joblib.load("E1_8_16")
E1_16_4_noise_10 = joblib.load("E1_16_4")
E1_16_8_noise_10 = joblib.load("E1_16_8")
E1_16_16_noise_10 = joblib.load("E1_16_16")
print("loaded logs")
# generate models:
tree1 = inductive_miner.apply_tree(E1_8_4_noise_10, None)
tree2 = inductive_miner.apply_tree(E1_8_8_noise_10, None)
tree3 = inductive_miner.apply_tree(E1_8_16_noise_10, None)
tree4 = inductive_miner.apply_tree(E1_16_4_noise_10, None)
tree5 = inductive_miner.apply_tree(E1_16_8_noise_10, None)
tree6 = inductive_miner.apply_tree(E1_16_16_noise_10, None)
#joblib.dump(tree6, "infrequent03_30 tree 6 fitness error ")
print("generated trees")
net1, initial_marking1, final_marking1 = inductive_miner.apply(E1_8_4_noise_10)
net2, initial_marking2, final_marking2 = inductive_miner.apply(E1_8_8_noise_10)
net3, initial_marking3, final_marking3 = inductive_miner.apply(E1_8_16_noise_10)
net4, initial_marking4, final_marking4 = inductive_miner.apply(E1_16_4_noise_10)
net5, initial_marking5, final_marking5 = inductive_miner.apply(E1_16_8_noise_10)
net6, initial_marking6, final_marking6 = inductive_miner.apply(E1_16_16_noise_10)
print("converted to petri nets")
# measure quality of models
fitness1 = fitness_factory.apply(E1_8_4_noise_10, net1, initial_marking1, final_marking1)
print("fitness1 calculated")
fitness2 = fitness_factory.apply(E1_8_8_noise_10, net2, initial_marking2, final_marking2)
print("fitness2 calculated")
fitness3 = fitness_factory.apply(E1_8_16_noise_10, net3, initial_marking3, final_marking3)
print("fitness3 calculated")
fitness4 = fitness_factory.apply(E1_16_4_noise_10, net4, initial_marking4, final_marking4)
print("fitness4 calculated")
fitness5 = fitness_factory.apply(E1_16_8_noise_10, net5, initial_marking5, final_marking5)
print("fitness5 calculated")
#fitness6 = "Error"
fitness6 = fitness_factory.apply(E1_16_16_noise_10, net6, initial_marking6, final_marking6)
print("fitness6 calculated")
print('fitness: ', fitness1['log_fitness'], fitness2['log_fitness'], fitness3['log_fitness'], fitness4['log_fitness'],
      fitness5['log_fitness'], fitness6['log_fitness'])
precision1 = precision_factory.apply(E1_8_4_noise_10, net1, initial_marking1, final_marking1)
print("P1 done")
precision2 = precision_factory.apply(E1_8_8_noise_10, net2, initial_marking2, final_marking2)
print("P2 done")
#precision3 = precision_factory.apply(E1_8_16_noise_10, net3, initial_marking3, final_marking3)
precision3 = "Error"
print("P3 done")
precision4 = precision_factory.apply(E1_16_4_noise_10, net4, initial_marking4, final_marking4)
print("P4 done")
precision5 = precision_factory.apply(E1_16_8_noise_10, net5, initial_marking5, final_marking5)
print("P5 done")
#precision6 = "Error"
precision6 = precision_factory.apply(E1_16_16_noise_10, net6, initial_marking6, final_marking6)
print("precision: ", precision1, precision2, precision3, precision4, precision5, precision6)
simplicity1 = simple_factory.apply(net1)
simplicity2 = simple_factory.apply(net2)
simplicity3 = simple_factory.apply(net3)
simplicity4 = simple_factory.apply(net4)
simplicity5 = simple_factory.apply(net5)
simplicity6 = simple_factory.apply(net6)
print('simplicity: ', simplicity1, simplicity2, simplicity3, simplicity4, simplicity5, simplicity6)
generalization1 = generalization_factory.apply(E1_8_4_noise_10, net1, initial_marking1, final_marking1)
print("G1 done")
generalization2 = generalization_factory.apply(E1_8_8_noise_10, net2, initial_marking2, final_marking2)
print("G2 done")
generalization3 = generalization_factory.apply(E1_8_16_noise_10, net3, initial_marking3, final_marking3)
print("G3 done")
generalization4 = generalization_factory.apply(E1_16_4_noise_10, net4, initial_marking4, final_marking4)
print("G4 done")
generalization5 = generalization_factory.apply(E1_16_8_noise_10, net5, initial_marking5, final_marking5)
print("G5 done")
generalization6 = generalization_factory.apply(E1_16_16_noise_10, net6, initial_marking6, final_marking6)
#generalization6 = "Error"
print("G6 done")
print('generalization: ', generalization1, generalization2, generalization3, generalization4, generalization5,
      generalization6)

csvData = [['Fitness', 'Precision', 'Generalization', 'Simplicity'],
           [fitness1['log_fitness'], precision1, simplicity1, generalization1],
           [fitness2['log_fitness'], precision2, simplicity2, generalization2],
           [fitness3['log_fitness'], precision3, simplicity3, generalization3],
           [fitness4['log_fitness'], precision4, simplicity4, generalization4],
           [fitness5['log_fitness'], precision5, simplicity5, generalization5],
           [fitness6['log_fitness'], precision6, simplicity6, generalization6]]

with open('dfg_0.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(csvData)
csvFile.close()
