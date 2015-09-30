#!/usr/bin/env python


import unittest

from k_env_modules import Module, KModule



class testModule(unittest.TestCase):


    def setUp(self):
        #self.config = load_yaml('gcc.yaml') 

        self.m = Module()

        self.test1 = {'name': 'test1',
                'prepend': {'PATH': 'path1',
                            'library_path': ['path2']},
                'setenv': {'MKL': 'env1',
                           'mkl_root': ['env2']},
                'unknown': {'a':1},
                     }


    def test_load_yaml_file(self):
        #File exists, and is loaded
        #File does not exist, should fail safely, and log error
        pass


    def test_load_config(self):
        pass


    def test_correct_types_in_config(self): 
        self.m.config = self.test1
        self.m.correct_types_in_config()

        self.test1_result = {'name': 'test1',
                'prepend': {'PATH': ['path1'],
                            'library_path': ['path2']},
                'setenv': {'MKL': 'env1',
                           'mkl_root': 'env2'},
                'unknown': {'a':1},
                     }

        self.assertDictEqual(self.m.config, self.test1_result)



class testInterpolateVars(unittest.TestCase):

    def setUp(self):
        self.m = Module()
        self.test1 = {
            'arch': 'x86_64',
            'apps_root': '/opt/share/',
            'version': 5.1,
            'app': 'gcc',
            'app_dir': '$apps_root/$app',
            'exec_dir': '$app_dir/$version/$arch',

            'prepend': {'PATH': ['$exec_dir', '$app_dir']},
            'append': {'PATH': ['$app_dir']},
            'invalid': {'PATH': ['$app_dir']},
                }


    def test_get_macro(self):
        self.m.config = self.test1
        self.assertFalse('prepend' in self.m._get_macros())

    def test_interpolate(self):
        self.m.config = self.test1
        self.m.interpolate_macros()

        self.assertEqual(self.m.config['app_dir'], "/opt/share/gcc")
        self.assertEqual(self.m.config['exec_dir'],
                                                "/opt/share/gcc/5.1/x86_64")

        self.assertListEqual(self.m.config['prepend']['PATH'], 
                            ["/opt/share/gcc/5.1/x86_64", '/opt/share/gcc'])

        self.assertListEqual(self.m.config['apend']['PATH'], 
                                                        ['/opt/share/gcc'])


    def test_interpolate_circular_fail(self):
        self.m.config = {'a': '$b', 'b': '$a'}
        with self.assertRaisesRegexp(SystemExit, '1'):
            self.m.interpolate_macros()

    def test_interpolate_not_found_fail(self):
        self.m.config = {'a': '$b'}
        with self.assertRaisesRegexp(SystemExit, '1'):
            self.m.interpolate_macros()



if __name__ == '__main__':
    unittest.main()


