"""
Module that loads the yaml for the module and version, and interpolates
the macro variables beginning with '$'  This is necessary to preserve
the usual Macro behavior in in the tcl modules.

It also needs to consider the of the $version parameter.  If this
is present then the original parameters in the yaml file need to be
overwritten.


"""


import os
import re
import glob
import yaml
import pprint
import itertools
from os.path import isfile

# requires Python 2.7 -- see note below if you're using an earlier version
import collections


def _tmp_error(code, message, admin_message=""):
    """
    TODO replace with proper logging later
    """
    if not admin_message:
        admin_message = message
    print 'User Error Message: ', message
    print 'Admin Error Message: ', admin_message
    if code == 1:
        raise Exception


class LoadYaml(object):
    """
    Creates a class to:
        1. Load yaml as text
        2. Replace $macros
        3. Load text into yaml
    """
    #The prefix to a macro variable in the yaml files
    MACRO = '$'

    #The environment variable that holds a : separated list of locations
    # to look for yaml files
    ROOT = 'KMODULEROOT'


    def __init__(self, module, version=None):
        self.module = module
        self.req_version = version

        self.filenames = list()
        self.yaml_files = list()

        self.versions = list()
        self.default_version = None

        #Combined file with inheritance and requeste defaults/version etc
        self.yaml = dict()



    def get_filenames_and_yamls(self):
        """
        Looks for the yaml file at module* and module*/*

        returns: list of filenames
                 list of yaml dicts
        """
        locs = [i[:-1] if i.endswith('/') else i
                        for i in os.environ[LoadYaml.ROOT].split(':')]
        
        files = list()
        for loc in locs:
            files.extend(glob.glob("%s/%s*" % (loc, self.module)))

            files.extend(glob.glob("%s/%s/*" % (loc, self.module)))


        for f in files:
            if os.path.isdir(f):
                continue
            yaml = self.load_yaml(f)
            if not yaml:
                continue


            self.filenames.append(f)
            self.yaml_files.append(yaml)


    def simple_validation(self):
        """
        A simple validation to check:
        1. 'version' is not used in any yaml files (versionS is OK)
        2. Only one 'default_version' used in any yaml files
        """

        default_version = None

        for i, yml in enumerate(self.yaml_files):

            # the $version macro is a special macro
            if 'version' in yml:
                msg = "Invalid use of version in file %s " % self.filenames[i][2:]
                msg += "'version' should not be defined in the yaml file."
                _tmp_error(1, "Error, contact helpdesk", msg)            


            if yml.get('default_version'):
                if default_version:
                    _tmp_error(1, "Error, contact helpdesk",
                                "More than one default version defined")

                default_version = yml['default_version']


        #TODO determine uniqueness in versions



    def get_versions(self):
        """

        versions is a special keyword that is appended, rather than upserted

        Returns a list of versions
        AND sets the default_version

        return: list
        """
        self.versions = list()
        self.default_version = None


        for yml in self.yaml_files:

            # Creates a file and version parallel list
            if 'versions' in yml:
                versions = yml['versions']

                if not isinstance(versions, list):
                    self.versions.append([versions])
                else:
                    self.versions.append(versions)

            #TODO No check here.  Assumes simple_validation has been run
            if 'default_version' in yml:
                self.default_version = yml['default_version']


        return list(itertools.chain.from_iterable( self.versions ))





    def determine_version(self):
        """
        Loads the yaml files and determines the correct file given 
        the 1. requested or 2. default or 3. latest version
        """
        versions = self.get_versions()

        if self.req_version:
            if self.req_version not in versions:
                msg = "Request verison %s not found," % self.req_version
                msg += "or yaml invalid, ie versions parameter does not exist"
                _tmp_error(1, msg, msg)
            else:
                return self.req_version

        elif self.default_version:
            return self.default_version


        # Return the latest verison
        versions.sort()
        return versions[-1]




    def load_yaml(self, filename):
        """
        Uses the pyyaml module to load the yaml file

        returns: the data dict
        """            

        try:
            return yaml.load(file(filename))
        except IOError:
            _tmp_error(1, "", "Cannot open file %s" % filename)
            return None
        except:
            _tmp_error(0, "", "Probably not a valid yaml file %s" % filename)
            return None





    def build_dependency(self, version=None):
        """
        Builds a network of versions
        """
        avail_versions = self.get_versions()

        dep = dict()
        chain = dict()

        for yml in self.yaml_files:
            for v in avail_versions:
                if v in yml and 'inherit' in yml[v]:
                        #TODO check for multiple inherit keywords?  

                        #a depends on b
                        a = v
                        b = yml[v]['inherit']      
                        dep[a] = b

                        if version:
                            if v == version:
                                chain[a] = [a, b]
                        else:
                            chain[a] = [a, b]

        
        def regress(chain, c):
            if len(chain[c]) > 1 and chain[c][-1] in dep:
                chain[c].append(dep[ chain[c][-1] ])
                regress(chain, c)
            else:
                return
                

        for c in chain:  
            regress(chain, c)


        return chain


    def upsert(self, dic1, dic2, debug=None):
        """
        Modifies d1 in-place to contain values from d2.  If any value
        in d1 is a dictionary (or dict-like), *and* the corresponding
        value in d2 is also a dictionary, then merge them in-place.
        http://stackoverflow.com/questions/10703858/
                                python-merge-multi-level-dictionaries
        Python 2.7 minimum
        """
        for key, val2 in dic2.items():
            val1 = dic1.get(key)  # returns None if v1 has no value for this key
            if (isinstance(val1, collections.Mapping) and
                    isinstance(val2, collections.Mapping)):
                self.upsert(val1, val2)
            else:
                #if debug and key in dic1 and key != 'versions':
                #    print "Upserting key - %s: '%s' with '%s'" % (key, dic1[key], val2)
                dic1[key] = val2


    def combine_yaml(self, version):
        """
        Combines many yaml files in order depending on inheritance etc.

        TODO Think about behavior!!!
        Loads the common data in no order.  This might be dangerous!!

        Then overwrites depending on inherit keywords. This is OK


        """
        avail_versions = self.get_versions()
        
        if version not in avail_versions:
            _tmp_error(1, "Error", "Requested version does not exist")

        versions_yaml = dict()

        #TODO think about this, not much logic here, but maybe thats
        #the way it should be!
        for yml in self.yaml_files:
            x_yml = yml.copy()
            #removes the versions
            for v in avail_versions:
                if v in yml:
                    versions_yaml[v] = yml[v]
                    x_yml.pop(v)
            
            #TODO upsert not working.  appending a dict rather othan overwriting the contents
            self.upsert(self.yaml, x_yml, debug=True)


        deps = self.build_dependency(version)
        if not deps:
            deps = {version: [version]}


        #then upsert the versions, in reverse order [::-1]
        for i in deps[version][::-1]:
            if i in versions_yaml:
                self.upsert(self.yaml, versions_yaml[i])



    def _dump_yaml_files_as_text(self):
        """
        returns: string
        """
        text = ""
        for yml in self.yaml_files:
            text += yaml.dump(yml)
        return text


    def _sed_macros(self, version):
        """
        Checks if every param is a macro in the file and replaces it

        TODO Should convert the yaml to text,
            then sed teh $macro then reload as yaml


        This feature is intended to replace the tcl macros, and therfore
        most params will be macros. also no in-depth recursion
        is catered for:  ie $$macro probably wont work
        """
        text = yaml.dump(self.yaml)

        for i in self.yaml:

            if not isinstance(self.yaml[i], str):
                continue
            
            regex = re.compile("\%s%s" % (LoadYaml.MACRO, i))
            text = regex.sub(self.yaml[i], text)


        regex = re.compile("\%sversion" % (LoadYaml.MACRO))
        text = regex.sub(version, text)

        self.yaml = yaml.load(text)



    def load(self):
        self.get_filenames_and_yamls()
        self.simple_validation()

        version = self.determine_version()

        #TODO check this
        self.combine_yaml(version)

        self._sed_macros(version)



    def pp_yaml_files(self):
        """
        Pretty print the yaml files
        """
        pp = pprint.PrettyPrinter(indent=4)
        for i, y in enumerate(self.yaml_files):
            print '\n', self.filenames[i]
            pp.pprint(y)


    def pp_yaml(self):
        """
        Pretty print the self.yaml
        """
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.yaml)




if __name__=='__main__':


    os.environ['KMODULEROOT'] = 'tests/'
    m = LoadYaml('gcc', '5.1.0')
    m.load()
    print m.pp_yaml()





