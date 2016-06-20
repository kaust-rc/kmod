
#!/usr/bin/env python


import unittest

from load_yaml import LoadYaml





class testLoadYaml(unittest.TestCase):

    def setUp(self):
        self.m = LoadYaml()
        self.m.load_yaml_file('tests/gcc.yaml')

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

    def test_load_yaml(self):
    	yaml = self.m.load_yaml('gcc.yaml')
    	self.assertEqual(yaml['module'], 'gcc')

        #Test file is not yaml
        self.m.load_yaml('gcc.tcl')

        #test file not exists
    	self.m.load_yaml('file-not-exist.stupid')



    def test_load_yaml_as_text(self):
        text = self.m.test_load_yaml_as_text('gcc.yaml')
        self.assertEqual('gcc' in yaml)

        #test file not exists
        self.m.test_load_yaml_as_text('file-not-exist.stupid')




    def test_get_macro(self):
        self.assertFalse('prepend' in self.m._get_macros())




        

if __name__ == '__main__':
    unittest.main()


