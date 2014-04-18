# -*- coding: utf8 -*-
__author__ = 'ceremcem'


import cca_logging
logger = cca_logging.logger


import time

import threading

from cca_signal import *
from cca_scyml import *
from cca_async_motor_task import *
from cca_parallel_task import *

from cca_yaml import *

import re


class CcascCompiler(object):

    def __init__(self, scyml_file):
        self.recipe = CcaYaml.loadf(scyml_file)

        self.tasks = []
        self.uniq_objects = {} # key: instance name, value : python object

    def get_events(self, sync_tasks, previous_events=""):
        try:
            if type(sync_tasks) == type(list()):
                try:
                    for item in sync_tasks:
                        #print("#%d :: Get event from list item" % iii, previous_events, item)
                        self.get_events(item, previous_events)
                except:
                    raise

            elif type(sync_tasks) == type(dict()):
                try:
                    for key, value in sync_tasks.iteritems():
                        #print("Key: ", key, "Value: ", value)
                        self.get_events(value, previous_events + ";" + key)
                except:
                    raise BaseException
            else:
                if type(sync_tasks) != type(None):
                    #series_tasks = sync_tasks.split(";")
                    separator = u"->"
                    series_tasks = re.split(ur"(" + separator + ur")", sync_tasks, re.UNICODE)
                    series_tasks = [x for x in series_tasks if x != separator]

                    #print(series_tasks, previous_events)

                    previous_condition = ""
                    for series_task in series_tasks:
                        previous_condition += ";" + series_task
                    simple_sync_task = previous_events + previous_condition
                    simple_sync_task = simple_sync_task[1:] # remove leading ";" sign
                    sst_list = simple_sync_task.split(";")
                    self.tasks.append(sst_list)

        except Exception as e:
            logger.error("Exception in get events %s" % e.message)
            raise BaseException


    def make_task_matrix(self):
        # in order to fill "tasks" list
        self.get_events(self.recipe)


    def convert_tasks_to_objects(self):
        self.make_task_matrix()
        # convert str to task object
        for pos, task in enumerate(self.tasks):
            self.tasks[pos] = map(cca_scyml.get_object, task)

    def create_special_objects(self):
        self.convert_tasks_to_objects()
        # rename all sleep functions in the same sync line
        for parallel_task_num, task_sequence in enumerate(self.tasks):
            pt = parallel_task_num
            new_seq = []
            for cpos, task in enumerate(task_sequence):
                if task["instance name"] == "sleep":
                    #logger.debug("Sleep function renamed to #%d" % pt)
                    task["instance name"] = "sleep%d%d" % (pt, cpos)
                new_seq.append(task)
            self.tasks[pt] = new_seq

    def create_uniq_obj_list(self):
        self.create_special_objects()
        for task_sequence in self.tasks:
            for o in task_sequence:
                object_name = o["instance name"]
                self.uniq_objects[object_name] = None

        for n, o in self.uniq_objects.iteritems():
            logger.debug("Object recognized: %s", n)

    def create_py_instances(self):
        self.create_uniq_obj_list()
        # create instances for unique objects
        # TODO: these objects should be created by config files
        for name, value in self.uniq_objects.iteritems():
            self.uniq_objects[name] = CcaAsyncMotorTask(name)



    def compile(self):
        self.create_py_instances()


    def get_pyobj(self, instance_name):
        return self.uniq_objects[instance_name]

    getobj = get_pyobj

    def print_tasks(self):
        print("")
        print("Task list as objects:")
        print("--------")
        for task in self.tasks:
            task_str = ""
            for o in task:
                obj = o
                task_str += obj["instance name"] + "." + obj["call"] + "(" + ''.join(obj["args"]) + ") "

            print(task_str)

    def make_parallel_tasks(self):
        ptasks = []
        for ptask in self.tasks:
            p = CcaParallelTask()
            p.task_list = ptask
            p.get_pyobj = self.get_pyobj
            ptasks.append(p)

        return ptasks

    def start_parallel_tasks(self):
        ptasks = self.make_parallel_tasks()
        # start all parallel tasks
        for ptask in ptasks:
            logger.debug("ptask started...")
            ptask.start()

