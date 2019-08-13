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
import joblib
from pm4py.algo.simulation.playout import factory as playout_factory
from pm4py.algo.discovery.inductive.versions.infrequent.splitting_infrequent import show_nice_log as nice_log
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.evaluation.replay_fitness import factory as fitness_factory


# stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "im_plain-test.csv"))
# log = conv_factory.apply(stream)

'''

# run im.plain
log = xes_import_factory.apply("tests\\compressed_input_data\\teleclaims.xes")
print('Länge des Logs: ', len(log))
tree = imp.apply_im_plain(log, None)
print(tree)
gviz = pt_vis_factory.apply(tree)
pt_vis_factory.view(gviz)
net, initial_marking, final_marking = imp.apply_plain_petrinet(tree)
fitness = fitness_factory.apply(log, net, initial_marking, final_marking)
print('fitness: ', fitness)


# run im_infrequent:
log = xes_import_factory.apply("tests\\compressed_input_data\\running-example.xes")
# stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "test-infrequent_behaviour.csv"))
# log = conv_factory.apply(stream)
log_abstracted = []
for trace in log:
    new_trace = []
    for element in trace:
        new_trace.append(element['concept:name'])
    log_abstracted.append(new_trace)
# print('starting with ', log_abstracted)
tree = imf.apply_im_infrequent(log, 0.15, None)
print(tree)
net, im, fm = imf.apply_infrequent_petrinet(tree)
log_generated = playout_factory.apply(net, im, parameters={"noTraces": 10, "maxTraceLength": 50})
print('generated log: ', log_generated)
print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
joblib.dump(tree, "wabalabadubdub", compress=3)
# gviz = pt_vis_factory.apply(tree)
# pt_vis_factory.view(gviz)

'''

# run im.df
log = xes_import_factory.apply("tests\\compressed_input_data\\running-example.xes")
tree = inductive_miner.apply_tree(log)
# gviz = pt_vis_factory.apply(tree)
# pt_vis_factory.view(gviz)
net, im, fm = inductive_miner.apply(log)
joblib.dump(tree, "wabalabadubdub", compress=3)
loaded_tree = joblib.load("wabalabadubdub")
# gviz = pt_vis_factory.apply(tree)
# pt_vis_factory.view(gviz)
# gviz2 = pt_vis_factory.apply(loaded_tree)
# pt_vis_factory.view(gviz2)

alignments = align_factory.apply_log(log, net, im, fm)
print('aaaaaaa: ', alignments)
#gviz = pn_vis_factory.apply(net, im, fm)
#pn_vis_factory.view(gviz)
#gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency")
#dfg_vis_factory.view(gviz)

