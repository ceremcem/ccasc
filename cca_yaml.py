# -*- coding: utf8 -*-
__author__ = 'ceremcem'

import cca_logging
logger = cca_logging.logger


import yaml
class CcaYaml():
    # TODO: make this class thread safe

    @staticmethod
    def dumpf(data, filename):

        with open(filename, 'wb') as f:
            yaml_data = yaml.safe_dump(data, default_flow_style=False, allow_unicode=True, width=80)
            #print(yaml_data)
            f.write(yaml_data)

    @staticmethod
    def loadf(yaml_filename):

        with open(yaml_filename, 'r') as f:
            content = f.read()
            data = yaml.load(content)
            #print(data)
            return data

if __name__ == "__main__":
    test_file = "../../control-app/egedoz-programs.yaml"
    with open(test_file, "rb") as f:
        c = f.read()
        from pprint import pprint
        yy = CcaYaml.loadf(test_file)
        pprint(yy)