# -*- coding: utf8 -*-
__author__ = 'ceremcem'


import time
from cca_signal import *
from ccasc_compiler import *
import cca_logging
logger = cca_logging.logger

import Pyro4


if __name__ == "__main__":
    c = CcascCompiler("cca-statechart-test.yaml")
    c.compile()

    #c.print_tasks()

    # Action
    try:
        pyro_dict = {}
        for name, pyobj in c.uniq_objects.iteritems():
            name = name.replace(" ", "_")
            name = name.replace(u"ç", "c")
            name = name.replace(u"ı", "i")
            name = name.replace(u"ş", "s")
            name = name.replace(u"ö", "o")
            name = name.replace(u"ğ", "g")
            name = name.replace(u"ü", "u")
            logger.info("Object recognized: '" + name + "',")
            pyro_dict[pyobj] = "example.%s" % name

        with open("pyro-dict.txt", 'wb') as f:
            for o, url in pyro_dict.iteritems():
                f.write(url + '\n')



        c.start_parallel_tasks()

        """
        c.uniq_objects[u"Beyaz Havlu"].send("allow_exec", CcaSignal(True))
        c.uniq_objects["Sinyal A"].send("allow_exec", CcaSignal(True))
        #c.uniq_objects["Sinyal B"].send("allow_exec", CcaSignal(True))
        """
        #for name, o in c.uniq_objects.iteritems():
        #    c.uniq_objects[name].send("allow_exec", CcaSignal(True))

        c.uniq_objects[u"Beyaz Havlu"].send("allow_exec", CcaSignal(True))
        c.uniq_objects[u"sinyal a"].send("allow_exec", CcaSignal(True))
        c.uniq_objects[u"sinyal b"].send("allow_exec", CcaSignal(True))
        c.uniq_objects[u"sinyal c"].send("allow_exec", CcaSignal(True))


        import Pyro4
        Pyro4.Daemon.serveSimple(pyro_dict,ns = False, port=12345)


    except Exception as e:
        logger.error(e)
        Pyro4.core.Daemon.close()
