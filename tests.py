#!/usr/bin/env python


import unittest

from k_env_modules import interpolate_vars, interpolate, load_yaml


class testInterpolateVars(unittest.TestCase):

    def set_up(self):
        self.config = load_yaml('gcc.yaml') 


    def test_interpolate(self):
        self.assertEqual(config['app_dir'], "/opt/share/gcc/4.8.1")




if __name__ == '__main__':
    unittest.main()


