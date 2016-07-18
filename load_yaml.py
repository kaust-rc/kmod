"""
Module that loads the yaml for the module and version, and interpolates
the macro variables beginning with '$'  This is necessary to preserve
the usual Macro behavior in in the tcl modules.

It also needs to consider the of the $version parameter.  If this
is present then the original parameters in the yaml file need to be
overwritten.
"""


__author__ = "Niall OByrnes"
__version__ = "0.0.1"


import os
import re
import glob
import pprint
import itertools

# requires Python 2.7 -- see note below if you're using an earlier version
import collections

import yaml as pyyaml



def _tmp_error(code, message, admin_message=""):
    """
    TODO replace with proper logging later
    """
    if not admin_message:
        admin_message = message
    print 'User Error Message: ', message
    print 'Admin Error Message: ', admin_message
    #if code == 1:
    #    raise Exception


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
    ROOT = 'KMODROOT'

    #This yaml is loaded first and would contain macro parameters that 
    # apply to all modules, such as a $root_app_dir etc..
    COMMON_YAML = "common.yaml"

    #group_list is mandatory and should be a list, otherwise errors.
    GROUPS = "group_list"


    def __init__(self, args=""):

        #Combined file with inheritance and requested defaults/version etc
        #Load COMMON_YAML to get args_mask
        self.yaml = self.get_common_yaml()

        if not self.yaml.get('args_mask'):
            raise Exception

        args_dict = self.parse_args(self.yaml.get('args_mask', ""), args)

        self.module = args_dict.get('module')

        self.req_version = args_dict.get('version')

        self.yaml.update(args_dict)


        self.filenames = list()
        self.yaml_files = list()
        self.groups = dict()

        self.versions = list()
        self.default_version = None
        
        #External inheritance.
        #Will contain and ordered list of external dependencies
        self.external_dependencies = list()

        #TODO add to DEBUG
        print self.module, self.req_version
        print self.yaml


    def get_yaml_locations(self):
        """
        Scans the directories under the environment variable KMODROOT
            and returns all directories
        """
        locs = [i[:-1] if i.endswith('/') else i
                for i in os.environ[LoadYaml.ROOT].split(':')]

        return locs


    def get_filenames_and_yamls(self):
        """
        Looks for the yaml file at module* and module*/*

        returns: list of filenames
                 list of yaml dicts
        """
        files = list()
        for loc in self.get_yaml_locations():
            files.extend(glob.glob("%s/%s*" % (loc, self.module)))

            files.extend(glob.glob("%s/%s/*" % (loc, self.module)))

        #TODO what to do with commn.yaml

        self._check_and_set_yaml(files)


    def get_all_yamls(self):
        """
        Gets all yaml files

        returns: list of filenames
                 list of yaml dicts
        """
        files = list()
        for loc in self.get_yaml_locations():
            files.extend(glob.glob("%s/*" % loc))

            files.extend(glob.glob("%s/*/*" % loc))


        self._check_and_set_yaml(files)





    def _check_and_set_yaml(self, files):
        """
        Scans the list of directories and sets the filenames and yamls
        It ignores files it cannot load or convert from yaml to python dict
        """
        for f in files:
            if os.path.isdir(f):
                continue

            yml = self.load_yaml(f)


            if yml:
                self.filenames.append(f)
                self.yaml_files.append(yml)



    def set_groups(self):
        """
        Allocates the group_lists
        """
        # TODO Does not add the versions yet, Should it?

        for yml in self.yaml_files:

            if LoadYaml.GROUPS in yml:

                #Add active_versions to the groups, TODO this is not correct
                #TODO separate the version=version from teh active versions
                for g in yml[LoadYaml.GROUPS]:
                    if g not in self.groups:
                        self.groups[g] = list()

                    #active_versions is mandatory
                    for v in yml['active_versions']:

                        self.groups[g].append('%s/%s' % (yml['module'], v))

                #TODO fix: look within versions for group_lists

                for possible_version in yml:
                    if LoadYaml.GROUPS in yml[possible_version]:

                        #Add the active_versions to the groups
                        for g in yml[possible_version][LoadYaml.GROUPS]:
                            if g not in self.groups:
                                self.groups[g] = list()

                                self.groups[g].append('%s/%s' % (possible_version, v))





    def load_yaml(self, filename):
        """
        Uses the pyyaml module to load the yaml file

        returns: the data dict
        """

        try:
            tmp = pyyaml.load(file(filename))
        except IOError:
            _tmp_error(1, "", "Cannot open file %s" % filename)
            return None
        except Exception:
            _tmp_error(0, "", "Probably not a valid yaml file %s" % filename)
            return None

        if not tmp:
            return tmp

        return tmp


    def get_common_yaml(self):
        """
        Finds the common.yaml file, and returns the dict. 
            raises an Exception if more than 1 is found

        returns: Dict
        """

        common = list()
        for loc in self.get_yaml_locations():
            common.extend(glob.glob("%s/%s" % (loc, LoadYaml.COMMON_YAML)))

        if len(common) > 1:
            #TODO
            raise Exception

        return self.load_yaml(common[0])


    def simple_validation(self):
        """
        A simple validation to check:
        1. 'version' is not used in any yaml files
        2. Only one 'default_version' used in any yaml files
        """
        default_version = None

        for i, yml in enumerate(self.yaml_files):

            # the $version macro is a special macro
            if 'version' in yml:
                msg = "Error: version defined in %s " % self.filenames[i][2:]
                msg += "'version' should not be defined in the yaml file."
                _tmp_error(1, "Error, contact helpdesk", msg)


            if yml.get('default_version'):
                if default_version:
                    _tmp_error(1, "Error, contact helpdesk",
                               "More than one default version defined")

                default_version = yml['default_version']


        #TODO determine uniqueness in versions


    def get_active_versions(self):
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
            if 'active_versions' in yml:
                versions = yml['active_versions']

                if not isinstance(versions, list):
                    # This creates list of lists, that corrospond to filename
                    self.versions.append([versions])
                else:
                    self.versions.append(versions)

            #TODO No check here.  Assumes simple_validation has been run
            if 'default_version' in yml:
                self.default_version = yml['default_version']

        self.versions = list(itertools.chain.from_iterable(self.versions))

        # This returns a flat list of versions
        return self.versions



    def determine_version(self):
        """
        Loads the yaml files and determines the correct file given
        the 1. requested or 2. default or 3. latest version
        """
        versions = self.get_active_versions()


        if self.req_version:
            if self.req_version not in versions:
                msg = "Request verison %s not found," % self.req_version
                msg += "or yaml invalid, ie versions parameter does not exist"
                _tmp_error(1, msg, msg)
            else:
                return self.req_version

        elif self.default_version:
            return self.default_version


        print "DEBUG ", versions
        # Return the latest verison
        versions.sort()
        return versions[-1]


    def parse_args(self, args_mask, args):
        """
        args_mask will be defined in the yaml file
        example args_mask: /module/version/

        """
        #TODO Possible add self.mask = re.compile(args_mask)

        m = re.match(args_mask, args)

        if m:
            found = m.groupdict()
        else:
            found = dict()

        # Do some validation
        return found


    def build_dependency(self, version=None):
        """
        Builds a network of versions
        """
        active_versions = self.get_active_versions()

        dep = dict()
        chain = dict()

        for yml in self.yaml_files:
            for v in active_versions:
                if (v in yml and 
                            'inherit' in yml[v]):
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
            """
            Small regress function, of limited scope
            """
            if len(chain[c]) > 1 and chain[c][-1] in dep:
                chain[c].append(dep[chain[c][-1]])
                regress(chain, c)
            else:
                return

        for c in chain:
            regress(chain, c)


        return chain


    def upsert(self, dic1, dic2, debug=False):
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
                if debug and key in dic1:
                    print "Upserting key - %s: '%s' with '%s'" % (key, dic1[key], val2)
                dic1[key] = val2


    def combine_yaml(self, version):
        """
        Combines many yaml files into one yaml file.
        This upserts without any order, so any "top-level"
            parameters will be overwritten.

        This should report a debug message to the admin in case there is any
            unintended overwriting of top level parameters.
        """
        active_versions = self.get_active_versions()


        if version not in active_versions:
            _tmp_error(1, "Error", "Requested version does not exist")

        versions_yaml = dict()


        self.yaml = self.get_common_yaml()

        #TODO This will overwrite any top-level parameters, in no particular
        #order.  TODO Need to think about this
        for yml in self.yaml_files:
            self.upsert(self.yaml, yml, debug=True)


    def version(self):
        return self.version


    def list_insert_0(self, l, i):
        if isinstance(i, str):
            l.insert(0, i)

        elif isinstance(i, list):
            l = dep.extend(i)        



    def _conditionals(self):
        """
        This method, scans and case keys (with a '=') and applies the 
        case.
        """
        cases = [c for c in self.yaml if '=' in c]
        for c in cases:
            k, v = c.split('=')

            if getattr(self, k, None) == v:
                print "Loading data for %s = %s" % (k, v)

                self.upsert(self.yaml, self.yaml[c])
        
            if c.startswith('version='):
                del self.yaml[c]


    def _dump_yaml_files_as_text(self):
        """
        returns: string
        """
        text = ""
        for yml in self.yaml_files:
            text += pyyaml.dump(yml)
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
        text = pyyaml.dump(self.yaml)

        for i in self.yaml:

            if not isinstance(self.yaml[i], str):
                continue

            regex = re.compile("\%s%s" % (LoadYaml.MACRO, i))
            text = regex.sub(self.yaml[i], text)

        #macro $version is NOT user defined 
        regex = re.compile("\%sversion" % (LoadYaml.MACRO))
        text = regex.sub(version, text)


        if LoadYaml.MACRO in text:
            print "undefined macro left in file"
            #TODO FIX
            pass#raise Exception

        self.yaml = pyyaml.load(text)



    def uname_hardware():
        """
        TODO SHould this be in kmod????
        """
        print "This should be called in kmod, not LoadYaml"
        raise Exception()


    def load(self):
        """
        The main callable method.
        1. Loads the common yaml, and intreprets the args_mask to
               determine module and version
        2. Searches for all relevant yaml files module* and module/*
        3. Loads all relevant yaml files, for the module
        4. If a version is not requested, it is determined by a
               marked default, or the 'highest' version
        5a. Finds the relevant version in either a file or a 'version=x.x.x'

        5b. If there is inheritance in this yaml data, then organises a
                chain of relevant verison to preload
        5c. Upserts the version specific yaml in order of the inheritance chain
        6. Replaces all macro parameters
        """

        self.get_filenames_and_yamls()
        self.simple_validation()

        #TODO CHECK THIS, it needs to set the determined version
        version = self.determine_version()
        self.version = version


        #TODO check this
        self.combine_yaml(version)

        self._conditionals()

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
        print '\n'*3
        

    def get_resolved_yaml(self):
        self.load()
        return self.yaml







if __name__ == '__main__':
    import sys

    os.environ['KMODROOT'] = 'test_yaml/'


    if len(sys.argv) > 2:
        args = ' '.join(sys.argv[1:])
    else:
        args = 'gcc 4.8.1'


    print "Debug executing module load %s" % args
    m = LoadYaml(args)


    print "Printing all the found module yaml files"    
    m.get_filenames_and_yamls()
    m.simple_validation()
    m.pp_yaml_files()


    version = m.determine_version()
    print "Loading version", version


    print "Prints the loaded common.yaml file"
    m.pp_yaml()



    print "Printing the combined data"
    m.combine_yaml(version)
    m.pp_yaml()


    print "Printing the conditionals resolved data"
    m._conditionals()
    m.pp_yaml()


    print "Printing the macro resolved data"
    m._sed_macros(version)
    m.pp_yaml()
