# -*- coding: utf8 -*-
__author__ = 'ceremcem'


import cca_logging
logger = cca_logging.logger


import time

import threading

from cca_signal import *
from cca_scyml import *
from cca_async_motor_task import *

import yaml

import re


class CcaParallelTask(threading.Thread):

    def __init__(self):
        super(CcaParallelTask, self).__init__();
        self.task_list = None

    def run(self):
        try:
            allow_exec = CcaSignal(0)
            wait_for_signal_result = {}
            was_successfull_before_interrupt = {}
            reached_stage = [0]
            stage_completed = {}
            while True:

                # start searching from beginning
                reached_stage[0] = -1

                for seq, task in enumerate(self.task_list):

                    if seq not in stage_completed:
                        stage_completed[seq] = CcaSignal()

                    inst_name = task["instance name"]
                    pyobj = self.get_pyobj(inst_name)
                    ss_name = task["call"] # signal/state name
                    is_signal = cca_scyml.isSignal(ss_name)
                    args = task["args"]

                    # if there is a stage become not completed, further stages
                    # can not be completed
                    for i in range(seq):
                        if not stage_completed[i].val:
                            stage_completed[i+1].val = False

                    if seq > 0:
                        allow_exec = stage_completed[seq - 1]
                    else:
                        allow_exec = CcaSignal(True)

                    reached_stage = [-1]
                    for i in range(seq):
                        if stage_completed[i].val:
                            reached_stage[0] += 1
                        else:
                            break

                    # check if state is ok to continue
                    if not is_signal:
                        state_name = ss_name
                        # then it is a state
                        stage_completed[seq].val = pyobj.In(state_name)


                        #if allow_exec.val and not stage_completed[seq].val:
                        #    print("%s : %d/ Waiting for [%d] %s->%s" % (str(datetime.datetime.now()), reached_stage[0], seq, inst_name, state_name))
                    else:
                        # it's a signal
                        signal_name = ss_name

                        pyobj.send(cca_scyml.allow_exec_signal, allow_exec)

                        # time to exec
                        if allow_exec.r_edge():
                            logger.info(">> SEND: %s->%s%s" % (inst_name, signal_name, args))
                            pyobj.send(signal_name, *args)

                        # then wait for continue state
                        if allow_exec.val and not stage_completed[seq].val:
                            stage_completed[seq].val = pyobj.In_continue_state_for(signal_name, *args)
                            #if not :
                            #    #print("%s : %d/Waiting for [%d] %s->%s (continue state)" % (str(datetime.datetime.now()), reached_stage[0], seq, inst_name, continue_state))
                            #    pass
                            #else:
                            #     = True
                        if stage_completed[seq].r_edge():
                            logger.debug("in continue state for %s->%s%s signal, continuing..." % (inst_name, signal_name, args))


                    time.sleep(.05)

                max_stage = len(self.task_list) - 1
                if stage_completed[max_stage].r_edge():
                    logger.debug("Finished all tasks")

        except Exception as e:
            logger.error("Exception in parallel task:", e)
            raise BaseException

