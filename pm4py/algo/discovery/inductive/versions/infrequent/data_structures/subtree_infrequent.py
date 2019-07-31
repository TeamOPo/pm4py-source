from copy import copy, deepcopy
import networkx as nx
from pm4py.objects.log.util import xes as xes_util
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_activities_from_dfg, \
    get_connected_components, infer_start_activities, infer_end_activities
from pm4py.algo.discovery.dfg.utils.dfg_utils import get_ingoing_edges, get_outgoing_edges
from pm4py.algo.discovery.dfg.utils.dfg_utils import negate, get_activities_self_loop
from pm4py.algo.discovery.inductive.versions.plain_version.data_structures.subtree_plain import SubtreePlain
from pm4py.algo.discovery.dfg.versions import native as dfg_inst
from pm4py.algo.filtering.dfg.dfg_filtering import clean_dfg_based_on_noise_thresh
from pm4py.algo.discovery.inductive.versions.plain_version import base_case, fall_through
from pm4py import util as pmutil
from pm4py.algo.discovery.inductive.versions.plain_version import splitting as split
from pm4py.algo.filtering.log.attributes import attributes_filter
import numpy as np
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.algo.filtering.log.end_activities import end_activities_filter
from pm4py.algo.filtering.log.start_activities import start_activities_filter

from pm4py.algo.discovery.inductive.versions.infrequent import splitting_infrequent


class SubtreeInfrequent(SubtreePlain):

    def check_cut_im_plain(self):
        conn_components = self.get_connected_components(self.ingoing, self.outgoing, self.activities)
        this_nx_graph = self.transform_dfg_to_directed_nx_graph()
        strongly_connected_components = [list(x) for x in nx.strongly_connected_components(this_nx_graph)]
        xor_cut = self.detect_xor(conn_components)
        if xor_cut[0]:
            return True, 'concurrent', xor_cut
        else:
            sequence_cut = self.detect_sequence(strongly_connected_components)
            if sequence_cut[0]:
                return True, 'sequential', sequence_cut
            else:
                parallel_cut = self.detect_concurrent()
                if parallel_cut[0]:
                    return True, 'parallel', parallel_cut
                else:
                    loop_cut = self.detect_loop()
                    if loop_cut[0]:
                        return True, 'loopCut', loop_cut
                    else:
                        return False, []

    def filter_dfg_on_threshold(self):
        # TODO check if dfg is really type list
        filtered_dfg = []
        for key, value in self.dfg:
            if value == self.noise_threshold or value > self.noise_threshold:
                filtered_dfg.append(key, value)
        print('filtered dfg ', self.dfg)
        print('with threshold ', self.noise_threshold, 'to: ', filtered_dfg)
        self.dfg = filtered_dfg

    def apply_cut_im_plain(self, type_of_cut, cut, activity_key):
        if type_of_cut == 'concurrent':
            print('detected plain concurrent_cut')
            self.detected_cut = 'concurrent'
            new_logs = split.split_xor(cut[1], self.log)
            print('splitted to: ', self.show_split(new_logs))
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                activities = attributes_filter.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                end_activities = list(
                    end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                self.children.append(
                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold, start_activities=start_activities,
                                 end_activities=end_activities,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))
        elif type_of_cut == 'sequential':
            new_logs = split.split_sequence(cut[1], self.log)
            self.detected_cut = "sequential"
            print('detected sequence_cut', cut[1])
            print('splitted to: ', self.show_split(new_logs))
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                activities = attributes_filter.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                end_activities = list(
                    end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                self.children.append(
                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold, start_activities=start_activities,
                                 end_activities=end_activities,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))
        elif type_of_cut == 'parallel':
            new_logs = split.split_parallel(cut[1], self.log)
            self.detected_cut = "parallel"
            print('detected parallel_cut', cut[1])
            print('splitted to: ', self.show_split(new_logs))
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                activities = attributes_filter.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                end_activities = list(
                    end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                self.children.append(
                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold, start_activities=start_activities,
                                 end_activities=end_activities,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))
        elif type_of_cut == 'loopCut':
            new_logs = split.split_loop(cut[1], self.log)
            self.detected_cut = "loopCut"
            print('detected loop', cut[1])
            print('splitted to: ', self.show_split(new_logs))
            for l in new_logs:
                new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                    pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                activities = attributes_filter.get_attribute_values(l, activity_key)
                start_activities = list(
                    start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                end_activities = list(
                    end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                self.children.append(
                    SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                 self.rec_depth + 1,
                                 noise_threshold=self.noise_threshold,
                                 start_activities=start_activities,
                                 end_activities=end_activities,
                                 initial_start_activities=self.initial_start_activities,
                                 initial_end_activities=self.initial_end_activities))

    def detect_cut(self,  second_iteration=False, parameters=None):
        if parameters is None:
            parameters = {}
        if pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY] = xes_util.DEFAULT_NAME_KEY
        if pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY not in parameters:
            parameters[pmutil.constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY] = parameters[
                pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]
        activity_key = parameters[pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY]

        # use the cutting and splitting functions of im_plain:
        found_plain_cut, type_of_cut, cut = self.check_cut_im_plain()
        if found_plain_cut:
            self.apply_cut_im_plain(type_of_cut, cut, activity_key)
        # if im_plain does not find a cut, we filter on our threshold and then again apply the im_cut detection
        # but this time, we have to use different splitting functions:
        else:
            self.filter_dfg_on_threshold()
            found_plain_cut, type_of_cut, cut = self.check_cut_im_plain()
            if found_plain_cut:
                if type_of_cut == 'concurrent':
                    print('detected inf concurrent_cut')
                    self.detected_cut = 'concurrent'
                    new_logs = splitting_infrequent.split_xor_infrequent(cut[1], self.log)
                    print('splitted to: ', self.show_split(new_logs))
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold, start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                elif type_of_cut == 'sequential':
                    new_logs = splitting_infrequent.split_sequence_infrequent(cut[1], self.log)
                    self.detected_cut = "sequential"
                    print('detected inf sequence_cut', cut[1])
                    print('splitted to: ', self.show_split(new_logs))
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold, start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                elif type_of_cut == 'parallel':
                    new_logs = splitting_infrequent.split_parallel_infrequent(cut[1], self.log)
                    self.detected_cut = "parallel"
                    print('detected inf parallel_cut', cut[1])
                    print('splitted to: ', self.show_split(new_logs))
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold, start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))
                elif type_of_cut == 'loopCut':
                    new_logs = splitting_infrequent.split_loop_infrequent(cut[1], self.log)
                    self.detected_cut = "loopCut"
                    print('detected inf loop', cut[1])
                    print('splitted to: ', self.show_split(new_logs))
                    for l in new_logs:
                        new_dfg = [(k, v) for k, v in dfg_inst.apply(l, parameters={
                            pmutil.constants.PARAMETER_CONSTANT_ACTIVITY_KEY: activity_key}).items() if v > 0]
                        activities = attributes_filter.get_attribute_values(l, activity_key)
                        start_activities = list(
                            start_activities_filter.get_start_activities(self.log, parameters=None).keys())
                        end_activities = list(
                            end_activities_filter.get_end_activities(self.log, parameters=None).keys())
                        self.children.append(
                            SubtreePlain(l, new_dfg, self.master_dfg, self.initial_dfg, activities, self.counts,
                                         self.rec_depth + 1,
                                         noise_threshold=self.noise_threshold,
                                         start_activities=start_activities,
                                         end_activities=end_activities,
                                         initial_start_activities=self.initial_start_activities,
                                         initial_end_activities=self.initial_end_activities))

            else:
                pass
                # TODO apply_fall_through_infrequent


def make_tree(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold, start_activities,
              end_activities, initial_start_activities, initial_end_activities):
    tree = SubtreeInfrequent(log, dfg, master_dfg, initial_dfg, activities, c, recursion_depth, noise_threshold,
                             start_activities, end_activities, initial_start_activities, initial_end_activities)
    return tree