import re
import unittest

from load_yaml import LoadYaml



class TestArgsMask(unittest.TestCase):

    def setUp(self):

        self.T = LoadYaml()

        self.default_mask = "(?P<module>.*)[\ \/](?P<version>.*)"


    def test_parse_args(self):

        test_data = ["vasp/5.3.5",
                     "vasp/5.3.5/",
                     "vasp 5.3.5",
                     "vasp 5.3.5/"]

        result = {'module': 'vasp',
                  'version': '5.3.5',
                 }

        for t in test_data:
            self.assertItemsEqual(self.T.parse_args(self.default_mask, t), result)



    """



    def test_parse_args_t1_short_input(self):

        t1 = "vasp/5.3.5/mpich-1.8.6-intel-2015"

        result = self.k.parse_args(m1)

        self.assertItemsEqual(result, {'module': 'vasp',
                                    'version': '5.3.5',
                                    'mpi': 'mpich',
                                    'mpi_version': '1.8.6',
                                    'mpicompiler': 'intel'
                                    'mpi_compiler_version': '2015'}
    """



