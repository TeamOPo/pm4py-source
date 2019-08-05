from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.objects.log.importer.csv import factory as csv_importer
import os
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.process_tree import factory as pt_vis_factory
from pm4py.visualization.petrinet import factory as pn_vis_factory
from pm4py.algo.discovery.inductive.versions.dfg.data_structures import subtree_imdfb as subtree
from pm4py.objects.conversion.log import factory as conv_factory
from pm4py.algo.discovery.dfg import factory as dfg_factory
from pm4py.visualization.dfg import factory as dfg_vis_factory
from pm4py.algo.discovery.inductive.versions.plain_version import im_plain as imp
from pm4py.algo.discovery.inductive.versions.infrequent import im_infrequent as imf



#log = xes_importer.apply(os.path.join("tests", "compressed_input_data", "04_reviewing.xes.gz"))
stream_big = csv_importer.import_event_stream(os.path.join("tests", "compressed_input_data", "04_reviewing.xes.gz"))

#stream_loop = csv_importer.import_event_stream(os.path.join("tests", "input_data", "test-loop_cut.csv"))
#log_loop = conv_factory.apply(stream_loop)
#tree_loop = imp.apply_im_plain(log_loop)
#gviz = pt_vis_factory.apply(tree_loop)
#pt_vis_factory.view(tree_loop)


'''
# run im.plain
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "im_plain-test.csv"))
log = conv_factory.apply(stream)
log_abstracted = []
for trace in log:
    new_trace = []
    for element in trace:
        new_trace.append(element['concept:name'])
    log_abstracted.append(new_trace)
print('starting with ', log_abstracted)
tree = imp.apply_im_plain(log, None)
print(tree)
gviz = pt_vis_factory.apply(tree)
pt_vis_factory.view(gviz)


from pm4py.algo.discovery.inductive.versions.infrequent import splitting_infrequent as sif

stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "test-sequence-split-if.csv"))
log = conv_factory.apply(stream)
cut = [['A', 'B'], ['C']]
sif.split_sequence_infrequent(cut, log)



'''
# run im_infrequent:
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "test-infrequent_behaviour.csv"))
log = conv_factory.apply(stream)
log_abstracted = []
for trace in log:
    new_trace = []
    for element in trace:
        new_trace.append(element['concept:name'])
    log_abstracted.append(new_trace)
# print('starting with ', log_abstracted)
tree = imf.apply_im_infrequent(log, 0.15, None)
print(tree)
# gviz = pt_vis_factory.apply(tree)
# pt_vis_factory.view(gviz)

'''
# run im.df

stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "im_plain-test.csv"))
log = conv_factory.apply(stream)
tree = inductive_miner.apply_tree(log)
gviz = pt_vis_factory.apply(tree)
pt_vis_factory.view(gviz)
#net, im, fm = inductive_miner.apply(log)
#gviz = pn_vis_factory.apply(net, im, fm)
#pn_vis_factory.view(gviz)
dfg = dfg_factory.apply(log)
#gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency")
#dfg_vis_factory.view(gviz)

'''
