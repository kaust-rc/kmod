#!/usr/bin/env python

import os
import unittest

from load_yaml import LoadYaml



class TestLoadYaml1(unittest.TestCase):

    def setUp(self):
        self.m = LoadYaml('gcc')


    def test_get_yaml_locations(self):
        os.environ[self.m.ROOT] = '/a/s/d/f:b:c/:/s/'

        self.assertItemsEqual(self.m.get_yaml_locations(),
            ['/a/s/d/f', 'b', 'c', '/s'])


    def mock_get_yaml_locations(self):
        return ['../test_yaml']


    def test_get_filenames_and_yamls(self):
        self.m.get_yaml_locations = self.mock_get_yaml_locations
    
        self.m.get_filenames_and_yamls()

        self.assertItemsEqual(self.m.filenames,
            ['../test_yaml/gcc.yaml', '../test_yaml/gcc/test.5.0.1.yaml'])

        self.assertEqual(len(self.m.yaml_files), 2)


    def test_get_all_yamls(self):
        self.m.get_yaml_locations = self.mock_get_yaml_locations

        self.m.get_all_yamls()

        self.assertItemsEqual(self.m.filenames, 
            ['../test_yaml/gcc.yaml',
                '../test_yaml/gcc/test.5.0.1.yaml',
                '../test_yaml/vmd.yaml',
                '../test_yaml/wien2k.yaml',
                '../test_yaml/common.yaml'])


    def test_get_common_yaml(self):
        self.m.get_yaml_locations = self.mock_get_yaml_locations
        common = self.m.get_common_yaml()

        self.assertItemsEqual(common, {'apps_root':'/opt/share'})



class TestLoadYaml2(unittest.TestCase):
    """
    These tests rely on the test/example yaml files in the tests folder
    """

    def setUp(self):
        self.m = LoadYaml('gcc')
        os.environ[self.m.ROOT] = '../test_yaml'
        self.m.get_filenames_and_yamls()


    def test_simple_validation(self):

        self.m.yaml_files[1]['default_version'] = 'Second_default_version'
        self.assertRaises(Exception, self.m.simple_validation)


        #Note this is version and not versions
        self.m.yaml_files[0]['version'] = 'error'
        self.assertRaises(Exception, self.m.simple_validation)


    def test_get_active_versions(self):
        versions = self.m.get_active_versions()

        self.assertItemsEqual(versions,
            ['4.6.0_k01', '4.8.1', '4.6.0', '5.0.1', '5.1.0'])



    def test_determine_version(self):



        #Check returns the default defined in yaml, when none requested
        self.assertEqual(self.m.determine_version(),  '4.8.1')

        #Check returns when a version requested
        self.m.req_version = '4.6.0_k01'
        self.assertEqual(self.m.determine_version(),  '4.6.0_k01')



        #Check when none requested or no default defined
        self.m.req_version = None
        for i in self.m.yaml_files:
            if 'default_version' in i:
                i.pop('default_version')

        #Should returns the last item of a sorted list
        self.assertEqual(self.m.determine_version(),  '5.1.0')



    def test_load_yaml(self):
    	yaml = self.m.load_yaml('gcc.yaml')
    	self.assertEqual(yaml['module'], 'gcc')


        #tTODO est file not exists
        #self.assertRaises(Exception, self.m.load_yaml('file.not.exist'))


        


    def test_build_dependency(self):
        def return_set(deps):
            result  = set()
            for i, j in deps:
                result.add(i)
                result.add(j)
            return list(result) 

        deps = (    (5,4),
                    (3,2),
                    (4,3),
                    (6,3),
                )

        expected_result = {
            5:[5,4,3,2],
            4:[4,3,2],
            3:[3,2],
            6:[6,3,2],
        }



        self.m.yaml_files = [ {i:{'inherit':j}} for i, j in deps]
        def mock_get_active_versions():
            return return_set(deps)
        self.m.get_active_versions = mock_get_active_versions

        result = self.m.build_dependency()
        self.assertEqual(expected_result, result)


        #Test just asking for one dependency
        result = self.m.build_dependency(5)
        self.assertEqual({5: expected_result[5]}, result)



    """
    TODO TODO 
    def test_build_dependency_Error_Circular(self):
        def return_set(deps):
            result  = set()
            for i, j in deps:
                result.add(i)
                result.add(j)
            return list(result) 

        deps = (    (5,4),
                    (4,5),
                )

        expected_result = {
            5:[5,4,],
        }


        self.m.yaml_files = [ {i:{'inherit':j}} for i, j in deps]
        def mock_get_active_versions():
            return return_set(deps)
        self.m.get_active_versions = mock_get_active_versions

        result = self.m.build_dependency()
        self.assertEqual(expected_result, result)
    """


    def test_build_dependency_test_files(self):
        expected_result = {
            '5.0.1': ['5.0.1', '4.8.1'], 
            '5.1.0': ['5.1.0', '5.0.1', '4.8.1']
            }
        result = self.m.build_dependency()
        self.assertEqual(expected_result, result)

        #Check with no dependency
        result = self.m.build_dependency('4.8.0')
        self.assertEqual(dict(), result)


        #Test just one version
        expected_result.pop('5.0.1')
        result = self.m.build_dependency('5.1.0')
        self.assertEqual(expected_result, result)





    def test_combine_yaml(self):

        self.m.combine_yaml('5.1.0')

        self.assertEqual(self.m.yaml['prepend']['PATH'], ['$app_dir/bin'])
        self.assertEqual(self.m.yaml['myver'], 'overwriting nonsense')
        #self.assertFalse(self.m.yaml.get('5.1.0'))


    """
    def test_combine_yaml_Error_not_exist(self):
        #TODO catch error
        self.m.test_combine_yaml('vers.not.exist')
    """


    def test_dump_yaml_files_as_text(self):
        self.m.combine_yaml('5.1.0')
        text = self.m._dump_yaml_files_as_text()
        self.assertTrue("MANPATH: [$app_dir/share/man]" in text)
        self.assertTrue("default_version: 4.8.1" in text)


    def test_sed_macros(self):
        self.m.combine_yaml('5.1.0')
        self.m._sed_macros('5.1.0')

        self.assertEqual(self.m.yaml['prepend']['INFOPATH'], 
            ["/opt/share/gcc/5.1.0/el6/share/info"])




if __name__ == '__main__':
    unittest.main()


