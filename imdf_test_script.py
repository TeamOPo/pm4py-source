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



# generate logs:

parameters = {"min_rec_depth": 100}
random_tree = tree_gen.apply()
net, initial_marking, final_marking = imp.apply_plain_petrinet(random_tree)
log = playout_factory.apply(net, initial_marking, parameters={"noTraces": 30, "maxTraceLength": 50})
print(split.show_nice_log(log))
print(len(split.show_nice_log(log)))
# stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "reviewing.csv"))
# log = conv_factory.apply(stream)
# log = xes_import_factory.apply("tests\\compressed_input_data\\03_repairExample\\repairExample.xes")
noise_parameters = {"p_dev_activity": 0.5, "p_dev_time": 0.5, "p_dev_additional": 0.5}
log_with_noise = introduce_deviations(log, noise_parameters)


# apply im_plain
tree = imp.apply_im_plain(log, None)
tree_noise = imp.apply_im_plain(log_with_noise, None)
# joblib.dump(tree_noise, "tree_object", compress=3)
# apply im_infrequent
tree_if_no_noise_1 = imf.apply_im_infrequent(log, 0.3, None)
tree_if_1 = imf.apply_im_infrequent(log_with_noise, 0.3, None)
tree_if_no_noise_5 = imf.apply_im_infrequent(log, 0.6, None)
tree_if_5 = imf.apply_im_infrequent(log_with_noise, 0.6, None)
tree_if_no_noise_9 = imf.apply_im_infrequent(log, 0.9, None)
tree_if_9 = imf.apply_im_infrequent(log_with_noise, 0.9, None)
# apply im_dfg
tree_dfg_no_noise = inductive_miner.apply_tree(log)
tree_dfg = inductive_miner.apply_tree(log_with_noise)


# show petri_net
net, initial_marking, final_marking = imp.apply_plain_petrinet(tree)
net_1, initial_marking_1, final_marking_1 = imp.apply_plain_petrinet(tree_if_no_noise_1)
net_5, initial_marking_5, final_marking_5 = imp.apply_plain_petrinet(tree_if_no_noise_5)
net_9, initial_marking_9, final_marking_9 = imp.apply_plain_petrinet(tree_if_no_noise_9)
net_dfg, initial_marking_dfg, final_marking_dfg = inductive_miner.apply(log)

net_noise, initial_marking_noise, final_marking_noise = imp.apply_plain_petrinet(tree_noise)
net_noise_1, initial_marking_noise_1, final_marking_noise_1 = imf.apply_infrequent_petrinet(tree_if_1)
net_noise_5, initial_marking_noise_5, final_marking_noise_5 = imf.apply_infrequent_petrinet(tree_if_5)
net_noise_9, initial_marking_noise_9, final_marking_noise_9 = imf.apply_infrequent_petrinet(tree_if_9)
net_noise_dfg, initial_marking_noise_dfg, final_marking_noise_dfg = inductive_miner.apply(log_with_noise)



# calculate & print metrics

print('metrics no noise: ')
fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
simplicity = simple_factory.apply(net)
generalization = generalization_factory.apply(log,  net, initial_marking, final_marking)
precision = precision_factory.apply(log, net, initial_marking, final_marking)

fitness_no_noise_1 = fitness_factory.apply(log, net_1, initial_marking_1, final_marking_1)
simplicity_no_noise_1 = simple_factory.apply(net_1)
generalization_no_noise_1 = generalization_factory.apply(log,  net_1, initial_marking_1, final_marking_1)
precision_no_noise_1 = precision_factory.apply(log, net_1, initial_marking_1, final_marking_1)

fitness_no_noise_5 = fitness_factory.apply(log, net_noise_5, initial_marking_noise_5, final_marking_noise_5)
simplicity_no_noise_5 = simple_factory.apply(net_5)
generalization_no_noise_5 = generalization_factory.apply(log,  net_noise_5, initial_marking_noise_5, final_marking_noise_5)
precision_no_noise_5 = precision_factory.apply(log, net_noise_5, initial_marking_noise_5, final_marking_noise_5)

fitness_no_noise_9 = fitness_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
simplicity_no_noise_9 = simple_factory.apply(net_9)
generalization_no_noise_9 = generalization_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
precision_no_noise_9 = precision_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)

fitness_no_noise_dfg = fitness_factory.apply(log, net_dfg, initial_marking_dfg, final_marking_dfg)
simplicity_no_noise_dfg = simple_factory.apply(net_dfg)
generalization_no_noise_dfg = generalization_factory.apply(log,  net_dfg, initial_marking_dfg, final_marking_dfg)
precision_no_noise_dfg = precision_factory.apply(log, net_dfg, initial_marking_dfg, final_marking_dfg)
print('fitness: ', fitness['log_fitness'], fitness_no_noise_1['log_fitness'], fitness_no_noise_5['log_fitness'],
      fitness_no_noise_9['log_fitness'], fitness_no_noise_dfg['log_fitness'])
print('simplicity: ', simplicity,  simplicity_no_noise_1, simplicity_no_noise_5, simplicity_no_noise_9,
      simplicity_no_noise_dfg)
print('generalization: ', generalization, generalization_no_noise_1, generalization_no_noise_5,
      generalization_no_noise_9, generalization_no_noise_dfg)
print('precision: ', precision, precision_no_noise_1, precision_no_noise_5, precision_no_noise_9,
      precision_no_noise_dfg)


print('metrics noise: ')
fitness_noise = fitness_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)
simplicity_noise = simple_factory.apply(net_noise)
generalization_noise = generalization_factory.apply(log_with_noise,  net_noise, initial_marking_noise, final_marking_noise)
precision_noise = precision_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)

fitness_1 = fitness_factory.apply(log_with_noise, net_1, initial_marking_1, final_marking_1)
simplicity_1 = simple_factory.apply(net_1)
generalization_1 = generalization_factory.apply(log_with_noise,  net_1, initial_marking_1, final_marking_1)
precision_1 = precision_factory.apply(log_with_noise, net_1, initial_marking_1, final_marking_1)

fitness_5 = fitness_factory.apply(log_with_noise, net_noise_5, initial_marking_noise_5, final_marking_noise_5)
simplicity_5 = simple_factory.apply(net_5)
generalization_5 = generalization_factory.apply(log_with_noise,  net_noise_5, initial_marking_noise_5, final_marking_noise_5)
precision_5 = precision_factory.apply(log_with_noise, net_noise_5, initial_marking_noise_5, final_marking_noise_5)

fitness_9 = fitness_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
simplicity_9 = simple_factory.apply(net_9)
generalization_9 = generalization_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
precision_9 = precision_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)

fitness_dfg = fitness_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)
simplicity_dfg = simple_factory.apply(net_dfg)
generalization_dfg = generalization_factory.apply(log_with_noise,  net_dfg, initial_marking_dfg, final_marking_dfg)
precision_dfg = precision_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)

print('fitness: ', fitness_noise['log_fitness'], fitness_1['log_fitness'], fitness_5['log_fitness'],
      fitness_9['log_fitness'], fitness_dfg['log_fitness'])
print('simplicity: ', simplicity_noise,  simplicity_1, simplicity_5, simplicity_9,
      simplicity_dfg)
print('generalization: ', generalization_noise, generalization_1, generalization_5,
      generalization_9, generalization_dfg)
print('precision: ', precision_noise, precision_1, precision_5, precision_9,
      precision_dfg)










"""
# import csv
# stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "running-example-long.csv"))
# log = conv_factory.apply(stream)

stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "examples", "weird.csv"))
log = conv_factory.apply(stream)


tree = imp.apply_im_plain(log, None)
#tree = imf.apply_im_infrequent(log, 0.3, None)
tree_parameters = {"format": "PDF"}
gviz = pt_vis_factory.apply(tree, tree_parameters)
pt_vis_factory.view(gviz)



# import xmex
# log = xes_import_factory.apply("tests\\compressed_input_data\\running-example-long.xes")


# add noise to log
noise_parameters = {"p_dev_activity": 0.4, "p_dev_time": 0.7, "p_dev_additional": 0.5}
log_with_noise = introduce_deviations(log, noise_parameters)
joblib.dump(log_with_noise, "Log with Noise", compress=3)
print('log: ', len(log))
print('log_noise: ', len(log_with_noise))
"""
# debugging section
"""
log_fitness = joblib.load("fitness_example")
print(split.show_nice_log(log))
tree_noise = imp.apply_im_plain(log, None)
net_noise, initial_marking_noise, final_marking_noise = imp.apply_plain_petrinet(tree_noise)
print(fitness_factory.apply(log, net_noise, initial_marking_noise, final_marking_noise))
"""

"""
net, initial_marking, final_marking = imp.apply_plain_petrinet(tree)
print(tree)
print(fitness_factory.apply(log, net, initial_marking, final_marking))
"""



# find the traces that can't be replayed:
"""
log_with_traces_only_once = []
for trace in log:
    if split.show_nice_trace(trace) not in log_with_traces_only_once:
        log_with_traces_only_once.append(split.show_nice_trace(trace))
print(len(log), len(log_with_traces_only_once))

unfit = []
for trace in log:
    if split.show_nice_trace(trace) in log_with_traces_only_once:
        replay_result = token_replay.apply([trace], net_noise, initial_marking_noise, final_marking_noise)
        if not replay_result[0]["trace_is_fit"]:
            unfit.append((split.show_nice_trace(trace), list(replay_result))) 
        log_with_traces_only_once.remove(split.show_nice_trace(trace))
print(unfit)
"""






# built dict representation of log
"""
nl = {}
for trace in log_fitness:
    nt = []
    for element in trace:
        nt.append(element['concept:name'])
    nt_list = ''.join(", "+str(e) for e in nt)
    if nt_list in nl.keys():
        nl[nt_list] += 1
    else:
        nl[nt_list] = 1
print('normal log:  ', nl)
"""

"""
nl_n = {}
for trace in log_with_noise:
    nt = []
    for element in trace:
        nt.append(element['concept:name'])
    nt_list = ''.join(", "+str(e) for e in nt)
    if nt_list in nl_n.keys():
        nl_n[nt_list] += 1
    else:
        nl_n[nt_list] = 1
print('noise log: ', nl_n)
"""

"""
# apply im_plain
tree = imp.apply_im_plain(log, None)
tree_noise = imp.apply_im_plain(log_with_noise, None)
# joblib.dump(tree_noise, "tree_object", compress=3)
# apply im_infrequent
tree_if_no_noise_1 = imf.apply_im_infrequent(log, 0.1, None)
tree_if_1 = imf.apply_im_infrequent(log_with_noise, 0.1, None)
tree_if_no_noise_5 = imf.apply_im_infrequent(log, 0.5, None)
tree_if_5 = imf.apply_im_infrequent(log_with_noise, 0.5, None)
tree_if_no_noise_9 = imf.apply_im_infrequent(log, 0.9, None)
tree_if_9 = imf.apply_im_infrequent(log_with_noise, 0.9, None)
# apply im_dfg
tree_dfg_no_noise = inductive_miner.apply_tree(log)
tree_dfg = inductive_miner.apply_tree(log_with_noise)


# show tree
tree_parameters = {"format": "PDF"}
# no noise:
gviz = pt_vis_factory.apply(tree, tree_parameters)
pt_vis_factory.view(gviz)
gviz_noise_if = pt_vis_factory.apply(tree_if_no_noise_1, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_if = pt_vis_factory.apply(tree_if_no_noise_5, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_if = pt_vis_factory.apply(tree_if_no_noise_9, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_if = pt_vis_factory.apply(tree_dfg_no_noise, tree_parameters)
pt_vis_factory.view(gviz_noise_if)

# noise:
gviz_noise = pt_vis_factory.apply(tree_noise, tree_parameters)
pt_vis_factory.view(gviz_noise)
gviz_noise_if = pt_vis_factory.apply(tree_if_1, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_if = pt_vis_factory.apply(tree_if_5, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_if = pt_vis_factory.apply(tree_if_9, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
gviz_noise_dfg = pt_vis_factory.apply(tree_dfg, tree_parameters)
pt_vis_factory.view(gviz_noise_dfg)


# show petri_net
net, initial_marking, final_marking = imp.apply_plain_petrinet(tree)
net_1, initial_marking_1, final_marking_1 = imp.apply_plain_petrinet(tree_if_no_noise_1)
net_5, initial_marking_5, final_marking_5 = imp.apply_plain_petrinet(tree_if_no_noise_5)
net_9, initial_marking_9, final_marking_9 = imp.apply_plain_petrinet(tree_if_no_noise_9)
net_dfg, initial_marking_dfg, final_marking_dfg = inductive_miner.apply(log)

net_noise, initial_marking_noise, final_marking_noise = imp.apply_plain_petrinet(tree_noise)
net_noise_1, initial_marking_noise_1, final_marking_noise_1 = imf.apply_infrequent_petrinet(tree_if_1)
net_noise_5, initial_marking_noise_5, final_marking_noise_5 = imf.apply_infrequent_petrinet(tree_if_5)
net_noise_9, initial_marking_noise_9, final_marking_noise_9 = imf.apply_infrequent_petrinet(tree_if_9)
net_noise_dfg, initial_marking_noise_dfg, final_marking_noise_dfg = inductive_miner.apply(log_with_noise)

# gviz_net = pn_vis_factory.apply(net_noise, initial_marking_noise, final_marking_noise)
# pn_vis_factory.view(gviz_net)


# calculate & print metrics

print('metrics no noise: ')
fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
simplicity = simple_factory.apply(net)
generalization = generalization_factory.apply(log,  net, initial_marking, final_marking)
precision = precision_factory.apply(log, net, initial_marking, final_marking)

fitness_no_noise_1 = fitness_factory.apply(log, net_1, initial_marking_1, final_marking_1)
simplicity_no_noise_1 = simple_factory.apply(net_1)
generalization_no_noise_1 = generalization_factory.apply(log,  net_1, initial_marking_1, final_marking_1)
precision_no_noise_1 = precision_factory.apply(log, net_1, initial_marking_1, final_marking_1)

fitness_no_noise_5 = fitness_factory.apply(log, net_noise_5, initial_marking_noise_5, final_marking_noise_5)
simplicity_no_noise_5 = simple_factory.apply(net_5)
generalization_no_noise_5 = generalization_factory.apply(log,  net_noise_5, initial_marking_noise_5, final_marking_noise_5)
precision_no_noise_5 = precision_factory.apply(log, net_noise_5, initial_marking_noise_5, final_marking_noise_5)

fitness_no_noise_9 = fitness_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
simplicity_no_noise_9 = simple_factory.apply(net_9)
generalization_no_noise_9 = generalization_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
precision_no_noise_9 = precision_factory.apply(log, net_noise_9, initial_marking_noise_9, final_marking_noise_9)

fitness_no_noise_dfg = fitness_factory.apply(log, net_dfg, initial_marking_dfg, final_marking_dfg)
simplicity_no_noise_dfg = simple_factory.apply(net_dfg)
generalization_no_noise_dfg = generalization_factory.apply(log,  net_dfg, initial_marking_dfg, final_marking_dfg)
precision_no_noise_dfg = precision_factory.apply(log, net_dfg, initial_marking_dfg, final_marking_dfg)
print('fitness: ', fitness['log_fitness'], fitness_no_noise_1['log_fitness'], fitness_no_noise_5['log_fitness'],
      fitness_no_noise_9['log_fitness'], fitness_no_noise_dfg['log_fitness'])
print('simplicity: ', simplicity,  simplicity_no_noise_1, simplicity_no_noise_5, simplicity_no_noise_9,
      simplicity_no_noise_dfg)
print('generalization: ', generalization, generalization_no_noise_1, generalization_no_noise_5,
      generalization_no_noise_9, generalization_no_noise_dfg)
print('precision: ', precision, precision_no_noise_1, precision_no_noise_5, precision_no_noise_9,
      precision_no_noise_dfg)


print('metrics noise: ')
fitness_noise = fitness_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)
simplicity_noise = simple_factory.apply(net_noise)
generalization_noise = generalization_factory.apply(log_with_noise,  net_noise, initial_marking_noise, final_marking_noise)
precision_noise = precision_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)

fitness_1 = fitness_factory.apply(log_with_noise, net_1, initial_marking_1, final_marking_1)
simplicity_1 = simple_factory.apply(net_1)
generalization_1 = generalization_factory.apply(log_with_noise,  net_1, initial_marking_1, final_marking_1)
precision_1 = precision_factory.apply(log_with_noise, net_1, initial_marking_1, final_marking_1)

fitness_5 = fitness_factory.apply(log_with_noise, net_noise_5, initial_marking_noise_5, final_marking_noise_5)
simplicity_5 = simple_factory.apply(net_5)
generalization_5 = generalization_factory.apply(log_with_noise,  net_noise_5, initial_marking_noise_5, final_marking_noise_5)
precision_5 = precision_factory.apply(log_with_noise, net_noise_5, initial_marking_noise_5, final_marking_noise_5)

fitness_9 = fitness_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
simplicity_9 = simple_factory.apply(net_9)
generalization_9 = generalization_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)
precision_9 = precision_factory.apply(log_with_noise, net_noise_9, initial_marking_noise_9, final_marking_noise_9)

fitness_dfg = fitness_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)
simplicity_dfg = simple_factory.apply(net_dfg)
generalization_dfg = generalization_factory.apply(log_with_noise,  net_dfg, initial_marking_dfg, final_marking_dfg)
precision_dfg = precision_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)

print('fitness: ', fitness_noise['log_fitness'], fitness_1['log_fitness'], fitness_5['log_fitness'],
      fitness_9['log_fitness'], fitness_dfg['log_fitness'])
print('simplicity: ', simplicity_noise,  simplicity_1, simplicity_5, simplicity_9,
      simplicity_dfg)
print('generalization: ', generalization_noise, generalization_1, generalization_5,
      generalization_9, generalization_dfg)
print('precision: ', precision_noise, precision_1, precision_5, precision_9,
      precision_dfg)

"""




# show dfg
"""
parameters = {}
if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
    parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
    parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
dfg = [(k, v) for k, v in dfg_inst.apply(log, parameters={
        pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
gviz_2 = dfg_vis_factory.apply(dfg, log=log, variant="frequency")
dfg_vis_factory.view(gviz_2)




# generate log from petri-net
log_generated = playout_factory.apply(net, initial_marking, parameters={"noTraces": 10, "maxTraceLength": 50})
"""

# print simple_log
"""
log_abstracted = []
for trace in log:
    new_trace = []
    for element in trace:
        new_trace.append(element['concept:name'])
    log_abstracted.append(new_trace)
# print('starting with ', log_abstracted)
"""

# save tree or log
"""
# joblib.dump(tree, "wabalabadubdub", compress=3)
# joblib.dump(log_generated, "hieristeinlog", compress=3)
"""




"""
# run im_infrequent:
log_generated = playout_factory.apply(net, im, parameters={"noTraces": 10, "maxTraceLength": 50})
print('generated log: ', log_generated)
print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
joblib.dump(tree, "wabalabadubdub", compress=3)
# gviz = pt_vis_factory.apply(tree)
# pt_vis_factory.view(gviz)


# run im.df
joblib.dump(tree, "wabalabadubdub", compress=3)
loaded_tree = joblib.load("wabalabadubdub")

alignments = align_factory.apply_log(log, net, im, fm)
print('aaaaaaa: ', alignments)

"""
