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
#from pm4py.algo.discovery.inductive.versions.plain_version import im_plain as imp



#log = xes_importer.apply(os.path.join("tests", "compressed_input_data", "04_reviewing.xes.gz"))
stream_big = csv_importer.import_event_stream(os.path.join("tests", "compressed_input_data", "04_reviewing.xes.gz"))
stream = csv_importer.import_event_stream(os.path.join("tests", "input_data", "test-parallel_cut.csv"))
#print(type(stream), flush=True)
log = conv_factory.apply(stream)
tree = inductive_miner.apply_tree(log)
#gviz = pt_vis_factory.apply(tree)
#pt_vis_factory.view(gviz)
net, im, fm = inductive_miner.apply(log)
#gviz = pn_vis_factory.apply(net, im, fm)
#pn_vis_factory.view(gviz)
dfg = dfg_factory.apply(log)
#gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency")
#dfg_vis_factory.view(gviz)

#sub = imp.apply_im_plain(log)
#gviz = pt_vis_factory.apply(sub)
#pt_vis_factory.view(gviz)
