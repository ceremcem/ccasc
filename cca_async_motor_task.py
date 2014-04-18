# -*- coding: utf8 -*-
__author__ = 'ceremcem'

from cca_scyml import *
from cca_signal import *
import time
import threading

import cca_logging
logger = cca_logging.logger


class CcaAsyncMotorTask(object):
    def __init__(self, name):
        self.name = name
        # initial state: stopped
        self.current_state = cca_scyml.stopped_state

        self._duration = 0

        self._allow_exec_signal = CcaSignal(False)
        self._allow_exec_signals = {}

        self.allow_exec_lost_signal = cca_scyml.stop_signal

    def motor(self):
        # if successfully started:
        self.current_state = cca_scyml.started_state

        logger.info("%s - Started." % self.name)

        if self._duration > 0:
            begin = time.time()
            while begin + self._duration > time.time():
                pass
            #logger.debug("%s - Will stop normally..." % (self.name))
            self.stop()


    def In_continue_state_for(self, signal, *args):
        """
        returns wait state for the signal.
        if "signal" command is seen, this method
        tells us which signal we should wait for
        continue walking through the sync task list.
        """
        continue_state = ""
        if signal == cca_scyml.start_signal:
            if self.get_duration(*args) > 0:
                continue_state = cca_scyml.stopped_state
            else:
                continue_state = cca_scyml.started_state

        if signal == cca_scyml.stop_signal:
            continue_state = cca_scyml.stopped_state

        return self.In(continue_state)

    def get_duration(self, *args):
        try:
            duration = args[0] if len(args) > 0 else 0
            duration = str(duration).split()

            scalar = int(duration[0])
            unit = duration[1] if len(duration) > 1 else ""

            duration = scalar
        except:
            duration = 2
            logger.error("Error calculating duration")

        return duration

    # send a signal with its name
    def send(self, signal_name, *args):
        if signal_name == cca_scyml.start_signal:
            logger.debug("%s - Start signal caught" % (self.name))
            self.start(*args)
        elif signal_name == cca_scyml.stop_signal:
            logger.debug("%s - Stop signal caught" % (self.name))
            self.stop()
        elif signal_name == cca_scyml.allow_exec_signal:
            # if any signal allows execution, allow execution
            allow_signal = args[0]
            if allow_signal not in self._allow_exec_signals:
                self._allow_exec_signals[allow_signal] = None

            self._allow_exec_signals[allow_signal] = allow_signal.val

            result_allow_exec = False
            for signal, value in self._allow_exec_signals.iteritems():
                if value:
                    result_allow_exec = True

            self._allow_exec_signal.val = result_allow_exec
            if self._allow_exec_signal.r_edge():
                logger.debug("%s - Allow_exec signal CAME (signal id: %s)" % (self.name, str(id(allow_signal))))
            if self._allow_exec_signal.f_edge():
                logger.debug("%s - Allow_exec signal LOST (signal id: %s)" % (self.name, str(id(allow_signal))))

            # send appropriate signal upon allow_exec signal lost
            if self._allow_exec_signal.f_edge(): self.send(self.allow_exec_lost_signal)

    def In(self, state):
        return state == self.current_state

    # define events (signals)
    def start(self, *args):
        if self.In(cca_scyml.stopped_state) and self._allow_exec_signal.val:
            # switch to "starting" state
            self.current_state = cca_scyml.starting_state

            # run something, not blocking
            self._duration = self.get_duration(*args)
            threading.Thread(target=self.motor).start()
        else:
            logger.warning("%s.start(%s) signal captured but WON'T START" % (self.name, args))


    def stop(self):
        # switch to "stopping" state
        self.current_state = cca_scyml.stopping_state
        logger.info("%s stopping..." % self.name)

        # do works to stop

        # if successfully stopped:
        self.current_state = cca_scyml.stopped_state
        logger.info("%s stopped." % self.name)

if __name__ == "__main__":
    import msgpack
    import pickle
    x = CcaAsyncMotorTask("test")
    aaa = pickle.dumps(x, pickle.HIGHEST_PROTOCOL)

    bbb = pickle.loads(aaa)

    #bbb.send("start")
    import pdb
    pdb.set_trace()