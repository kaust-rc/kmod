"""
Module that loads the yaml for the module and version, and interpolates
the macro variables beginning with '$'  This is necessary to preserve
the usual Macro behavior in in the tcl modules.

It also needs to consider the of the $version parameter.  If this
is present then the original parameters in the yaml file need to be
overwritten.



"""
import glob
import yaml
from os.path import isfile


class LoadYaml(object):
    """
    Creates a class to:
        1. Load yaml as text
        2. Replace $macros
        3. Load text into yaml
    """

    MACRO = '$'


    def __init__(self, module, version):
        self.module = module
        self.req_version = version

        self.text = None
        self.yaml = None


    def get_yaml(self):
        """
        Loads the appropriate module and version

        returns: dict structure of env params
        """
        self.yaml = self.load_yaml_version()

        # These 2 funcs operate on self.text        
        self._sed_macros()
        self._insert_req_version()

        self.yaml = yaml.load(self.text)

        return self.yaml

    def get_possible_filenames(self, root='.'):
        """
        Looks for the yaml file at module* and module*/*

        returns: list of filenames
        """

        #TODO remove directories
        self.files = glob.glob("%s/%s*" % (root, module))

        self.files.extend(glob.glob("%s/%s/*" % (root, module)))


    def determine_version(self):
        """
        Loads the yaml files and determines the correct file given 
        the 1. requested or 2. default or 3. latest version
        """
        self.get_possible_filenames()

        files = list()
        versions = list()

        for f in self.files:
            yaml = self.load_yaml(f)
            possible_versions = yaml.get('versions', ['invalid'])

            if not isinstance(possible_versions, list):
                possible_versions = [possible_versions]

            for v in possible_versions:
                files.append(f)
                versions.append(v)

        # validate versions



        #If the requested version is in the file then return it            
        if self.req_version in versions:
            self.filename = found[0]
            return self.load_yaml(i)




        if len(found) == 1:

        elif len(found) > 1:
            print "Multiple versions found in files %s" % ", ".join(files)
            return list()
        else:
            print ("Request verison %s not found," % self.req_version,
                "or yaml invalid, ie versions parameter does not exist")
            return list()



        self.verison = 
        return self.verison





    def load_yaml_version(self):
        """

        """






    def load_yaml(self, filename):
        """
        Uses the pyyaml module to load the yaml file

        returns: the data dict
        """
        try:
            return yaml.load(file(filename))
        except IOError:
            print "Cannot open file %s" % filename
            return list()
        except:
            print "Probably not a valid yaml file %s" % filename
            return list()


    def load_yaml_as_text(self, filename):
        """
        Loads the yaml as text
        """
        try:
            with open(filename) as f:
                return f.read()
        except IOError:
            print "Cannot open file %s" % filename
            return ""
        except:
            print "Cannot open file %s as text" % filename
            return ""

    def _sed_macros(self):
        """
        Checks if every param is a macro in the file and replaces it
        This feature is intended to replace the tcl macros, and therfore
        most params will be macros. also no in-depth recursion
        is catered for:  ie $$macro probably wont work
        """
        self.text = self.load_yaml_as_text(self.filename)

        for i in self.yaml:
            # the $version macro is a special macro
            if i == 'version':
                print "Invalid use of version in file %s" % self.filename
                continue

            if not isinstance(self.yaml[i], str):
                continue
            
            regex = re.compile("\%s%s" % (self.MACRO, i))
            self.text = regex.sub(self.yaml[i], self.text)


        self.yaml = self.text

    def _insert_req_version(self):
        """
        Inserts the requested version into the $version macro
        """

        # Needs to handle default
        if self.req_version:
            version = self.req_version            
        elif 'default_version' in self.yaml:
            version = self.yaml['default_version']
        elif:
            #Load the latest verison
            pass


        regex = re.compile("\%sversion" % self.MACRO)
        self.text = regex.sub(version, self.text)


    def pp_yaml(self):
        """
        Pretty print the yaml, for parsing
        """
        pass







if __name__=='__main__':
    m = LoadYaml()
    m.load_yaml_file('tests/gcc.yaml')
