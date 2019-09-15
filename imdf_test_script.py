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


# import csv
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "running-example-long.csv"))
log = conv_factory.apply(stream)

# import xmex
# log = xes_import_factory.apply("tests\\compressed_input_data\\running-example-long.xes")


# add noise to log
noise_parameters = {"p_dev_activity": 0.2, "p_dev_time": 0.4, "p_dev_additional": 0.5}
log_with_noise = introduce_deviations(log, noise_parameters)
# joblib.dump(log_with_noise, "Log with Noise", compress=3)
# log_fitness = joblib.load("fitness_example")

# built dict representation of log
"""
nl = {}
for trace in log:
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


# apply im_plain
# tree = imp.apply_im_plain(log, None)
tree_noise = imp.apply_im_plain(log_with_noise, None)
# joblib.dump(tree_noise, "tree_object", compress=3)
# apply im_infrequent
tree_if = imf.apply_im_infrequent(log_with_noise, 0.35, None)

# apply im_dfg
tree_dfg = inductive_miner.apply_tree(log_with_noise)


# show tree
tree_parameters = {"format": "PDF"}
"""
gviz = pt_vis_factory.apply(tree, tree_parameters)
pt_vis_factory.view(gviz)

gviz_noise = pt_vis_factory.apply(tree_noise, tree_parameters)
pt_vis_factory.view(gviz_noise)

gviz_noise_if = pt_vis_factory.apply(tree_if, tree_parameters)
pt_vis_factory.view(gviz_noise_if)
"""

# show petri_net
# net, initial_marking, final_marking = imp.apply_plain_petrinet(tree)
net_noise, initial_marking_noise, final_marking_noise = imp.apply_plain_petrinet(tree_noise)
net_if, initial_marking_if, final_marking_if = imf.apply_infrequent_petrinet(tree_if)
net_dfg, initial_marking_dfg, final_marking_dfg = inductive_miner.apply(log_with_noise)

# gviz_net = pn_vis_factory.apply(net_noise, initial_marking_noise, final_marking_noise)
# pn_vis_factory.view(gviz_net)


# calculate & print metrics
# fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
fitness_noise = fitness_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)
fitness_if = fitness_factory.apply(log_with_noise, net_if, initial_marking_if, final_marking_if)
fitness_dfg = fitness_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)
print('fitness: ', fitness_noise, fitness_if, fitness_dfg)

# simplicity = simple_factory.apply(net)
simplicity_noise = simple_factory.apply(net_noise)
simplicity_if = simple_factory.apply(net_if)
simplicity_dfg = simple_factory.apply(net_dfg)
print('simplicity: ',  simplicity_noise, simplicity_if, simplicity_dfg)
# generalization = generalization_factory.apply(log,  net, initial_marking, final_marking)
generalization_noise = generalization_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)
generalization_if = generalization_factory.apply(log_with_noise, net_if, initial_marking_if, final_marking_if)
generalization_dfg = generalization_factory.apply(log_with_noise,  net_dfg, initial_marking_dfg, final_marking_dfg)
print('generalization: ',  generalization_noise, generalization_if, generalization_dfg)
# precision = precision_factory.apply(log, net, initial_marking, final_marking)
precision_noise = precision_factory.apply(log_with_noise, net_noise, initial_marking_noise, final_marking_noise)
precision_if = precision_factory.apply(log_with_noise, net_if, initial_marking_if, final_marking_if)
precision_dfg = precision_factory.apply(log_with_noise, net_dfg, initial_marking_dfg, final_marking_dfg)
print('precision: ',  precision_noise, precision_if, precision_dfg)




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
