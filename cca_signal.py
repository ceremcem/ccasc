__author__ = 'ceremcem'

import inspect
import threading

class CcaSignal(object):

    def __init__(self, initial_value=0):
        self.__val = bool(initial_value)
        self.__val0 = self.__val # previous value
        self.__readers_got_last_change = {}

    @property
    def val(self):
        return self.__val

    @val.setter
    def val(self, value):
        new_val = bool(value)
        if new_val != self.__val:
            self.__val0 = self.__val
            self.__val = new_val
            self.__readers_got_last_change = {}

    @property
    def pval(self):
        return self.__val0

    def _edge(self, reader_id):
        # TODO: if first reader came again, change should loose its importance, thus return "" for everyone
        # is there a rising/falling edge since last edge read?
        edge_status_for_reader = ""
        if reader_id not in self.__readers_got_last_change:
            if self.pval and not self.val:
                edge_status_for_reader = "f_edge"
            elif not self.pval and self.val:
                edge_status_for_reader = "r_edge"

            self.__readers_got_last_change[reader_id] = True

        return edge_status_for_reader

    def edge(self):
        f = inspect.currentframe().f_back
        thread_id = id(threading.currentThread())
        caller_id = (f.f_lineno, f.f_lasti, thread_id)
        #print(caller_id)
        return self._edge(caller_id)

    def r_edge(self):
        f = inspect.currentframe().f_back
        thread_id = id(threading.currentThread())
        caller_id = (f.f_lineno, f.f_lasti, thread_id)
        #print(caller_id)
        return self._edge(caller_id) == "r_edge"

    def f_edge(self):
        f = inspect.currentframe().f_back
        thread_id = id(threading.currentThread())
        caller_id = (f.f_lineno, f.f_lasti, thread_id)
        #print(caller_id)
        return self._edge(caller_id) == "f_edge"


def unit_test():
    import time

    a = CcaSignal()

    a.val = 1
    a.val = 0
    for i in range(3):
        print("a.val: %d" % a.val)
        print(a.edge(), a.edge(), a.edge(), a.edge(), a.edge(), a.edge())
        print(a.edge(), a.edge(), a.edge(), a.edge(), a.edge(), a.edge())
        print(a.edge(), a.edge(), a.edge(), a.edge(), a.edge(), a.edge())
        print(a.edge(), a.edge(), a.edge(), a.edge(), a.edge(), a.edge())
        time.sleep(1)

    """
    should print:

    a.val: 0
    ('f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge')
    ('f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge')
    ('f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge')
    ('f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge', 'f_edge')
    a.val: 0
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')
    a.val: 0
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')
    ('', '', '', '', '', '')

    """


def unit_test2():
    a = CcaSignal(0)
    a.val = 1
    print(a.r_edge(), a.f_edge())
    print(a.r_edge(), a.f_edge())
    a.val = 0
    print(a.r_edge(), a.f_edge())
    print(a.r_edge(), a.f_edge())

    """
    should print:
    (True, False)
    (True, False)
    (False, True)
    (False, True)
    """

def unit_test3():
    """
    This unit test shows us, any reader can detect edges only once
    """
    a = CcaSignal()
    a.val = 1
    for j in range(2):
        print("------------")
        for i in range(3):
            print(a.r_edge(), a.f_edge())

        print(a.r_edge(), a.f_edge())
        print(a.r_edge(), a.f_edge())
        print(a.r_edge(), a.f_edge())

    """
    should print:
    ------------
    (True, False)
    (False, False)
    (False, False)
    (True, False)
    (True, False)
    (True, False)
    ------------
    (False, False)
    (False, False)
    (False, False)
    (False, False)
    (False, False)
    (False, False)
    """

if __name__ == "__main__":
    #unit_test()
    #unit_test2()
    unit_test3()