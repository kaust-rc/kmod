import unittest

import re

class Kmod(object):

    @classmethod
    def parse_args(cls, args_mask, args):
        """
        args_mask will be defined in the yaml file
        example args_mask: /$app/$app_version/
        """
        m = re.match(args_mask, args)

        found = m.groupdict()


        return found



class TestKmod(unittest.TestCase):

    def setUp(self):
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
            self.assertItemsEqual(Kmod.parse_args(self.default_mask, t), result)



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



