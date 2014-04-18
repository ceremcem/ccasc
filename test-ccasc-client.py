__author__ = 'ceremcem'

import Pyro4
import pdb

try:
    oo = {}
    with open("pyro-dict.txt", 'rb') as f:
        for url in f.read().splitlines():
            name = url.split(".")[1]
            print("Object oo['%s'] added..." % name)
            oo[name] = Pyro4.Proxy("PYRO:%s@localhost:12345" % url)
    pdb.set_trace()
finally:
    print("Clean up...")
    for n, o in oo.iteritems():
        o._pyroRelease()


