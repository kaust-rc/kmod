#!/usr/bin/env python

__author__ = "Niall OByrnes"
__version__ = "0.0.1"

import logging


import os
import re
import sys
import yaml as pyyaml
import pprint

from help_text import help_text


from load_yaml import LoadYaml
#import logging
#logging.basicConfig(level=logging.DEBUG,
#       format='%(asctime)s %(levelname)s %(message)s')



#module [cmd]  a list of the allowable commands
cmds = ['load', 'unload', 'show', 'avail', 'purge', 'list', 'help', 'version']

#Admin command
acmds = ['report', 'validate', 'network']


#Keywords reserved for module application
keyword_strings = ['setenv']
keyword_lists = ['prepend', 'append', 'prereq', 'postreq', 'conflict', 'alias']

#Parameters reserved for module application
meta_strings = ['name', 'default_version']#, 'verbosity']
meta_lists = ['groups', 'bundles', 'active_versions', 'preload-yaml',]

#Give error for these for now
confusion = ['names', 'bundle', 'group']

#Module program keywords
mod_keywords = ['version']



#TODO should be picked up from admin.yaml, or an environment variable or something
#DIR = '/opt/share/kmodules/'
#DIR = 'yaml/'
DIR = 'tests/'



LOG_FILENAME = 'logging_example.out'
logging.basicConfig(filename=LOG_FILENAME,
                            level=logging.DEBUG,
                                                )

class BaseModule(object):


    def __init__(self, *args):


        self.args = [i.lower() for i in args[0]]

        if self.args[0] in cmds:
            logging.info('Running  %s %s', self.args[0], self.args)
            self.call_function()         





    def call_function(self):
        """
        Checks and calls the function from the args
        """


        getattr(self, self.args[0])()



    def load(self):
        self._load()



    def _load(self):
        """
        Executes the module load command
        """
        self.args.pop(0)
        it = iter(range(len(self.args[1:])))

        for i in it:


            #Try with version
            l = LoadYaml(self.args[i], self.args[i+1])
            l.load()
            if l.yaml:

                print 'DEBUG FOUND', l.module, l.version

                #This causes the iter to skip the version arg,
                # on the next iteration
                if len(self.args) > i+2:  
                    next(it)

            else:
                #Try without version
                l = LoadYaml(self.args[i])            
                l.load()
                if l.yaml:
                    print "DEBUG FOUND", l.module
                else:
                    print "DEBUG NOT FOUND", self.args[i]


            self._env_load(l.module, l.version, l.yaml)



    def _env_load(self, mod, version, yaml):
        evaltxt = ''

        export_set = set(['LOADEDMODULES'])

        self._append('LOADEDMODULES', mod)

        for env in yaml.get('prepend', []):
            for val in yaml['prepend'][env]:
                self._prepend(env, val)
                export_set.add(env)

        
        for env in yaml.get('append', []):
            for val in yaml['append'][env]:
                self._append(env, val)
                export_set.add(env)

        export = ""
        for i in export_set:
            export += '%s="%s" ' % (i, os.environ[i])


        alias = ""
        for alias in yaml.get('alias', []):
            for val in yaml['alias'][alias]:
                alias += '%s="%s" ' % (alias, val)


        if export:
            evaltxt = 'export ' + export
        if alias:
            if evaltxt:
                evaltxt = "%s ; alias %s" % (evaltxt, alias)
            else:
                evaltxt = "alias %s" % (alias)


        self._eval(evaltxt)



    def unload(self):
        self._unload()


    def _unload(self):
        for var in yaml.get('prepend', []):
            for val in yaml['prepend'][var]:
                self.remove(var, val)


        self.remove('LOADEDMODULES', self.mod)


        export = ' '.join(['%s="%s"' % (i, os.environ[i]) for i in yaml['prepend'] if os.environ[i] != ''])
        export += ' LOADEDMODULES="%s"' % (os.environ['LOADEDMODULES'])

        #TODO add regex for multiple '\:.*'
        export = export.replace('::', ':')
        if export:
            print 'export %s' % (export)


        unset = ' '.join(['%s' % (i) for i in yaml['prepend'] if os.environ[i] == ''])
        if unset:
            print "unset %s" % (unset)







    def _echo(self, msg):
        """
        The output of this program is run (eval) from a bash function so,
            any output text should be echo'd
        """
        print "echo %s" % msg


    def _export(self, export):
        """
        The output of this program is run (eval) from a bash function so,
            any output should be exported 
        """
        print "export %s" % export


    def _eval(self, cmds):
        print cmds



    def _error(self, msg):
        """
        Should print to stderr???
        """
        self._echo('ERROR: ' + msg)
        exit(1)




    def help(self):
        """
        Prints the help message
        """
        self._echo(help_text())


    def version(self):
        """
        Prints the version
        """
        self._echo("VERSION=%s" % __version__)





    def load_config(self, mod):
        """
        Loads the yaml file and interpolates the macro variables
        """

        self.load_mod_file(mod)

        self.validate_config()

        self._get_version()

        #nested_macros()

        #self.interpolate_macros()



    def validate_config(self):
        for i in mod_keywords:
            if i in yaml:
                raise Exception
        for i in confusion:
            if i in yaml:
                raise Exception





    def _prepend(self, env, val):
        os.environ[env] = "%s:%s" % (val, os.environ.get(env, ''))


    def _append(self, env, val):
        os.environ[env] = "%s:%s" % (os.environ.get(env, ''), val)


    def _alias(self, env, val):
        alias = "%s='%s'" % (env, val)




    def remove(self, env, val):
        if env not in os.environ:
            return

        envval = os.environ[env].split(':')

        if val in envval:
            envval.remove(val)
            #to remove every instance
            #envval = [i for i in envval if i != val]

        os.environ[env] = ':'.join(envval)



    def get_terminal_size(self):
        rows, columns = os.popen('stty size', 'r').read().split()

        return int(rows), int(columns)




    def avail(self):
        """
        """
        m = LoadYaml()
        print m.get_yaml_locations()
        m.get_all_yamls()

        rows, columns = self.get_terminal_size()
        #print yamls

        # TODO width should be max length of a module/version
        width = 36

        prt = []
        for y in m.yaml_files:
            m = y.get('module', {})
            for v in y.get('active_versions', []):
                prt.append("%s/%s" % (m, v))

        n = columns/width
        print
        for p in [prt[i:i+n] for i in range(0, len(prt), n)]:
            for i in p:
                print "%-30s" % i,
            print
        print




class KMod(BaseModule):

    def __init__(self, *args):
        super(KMod, self).__init__(*args)


        #self.validate_config()

    def validate_config(self):
        for i in yaml.keys():
            if '$' in i:
                print i*5
                raise Exception
        for i in forbidden:
            if i in yaml:
                print i*5
                raise Exception


    def load(self):
        """
        Prints a formatted version of config
        """
        export = self._load()

        #prittyprint
        print 'export %s' % (export)



    def pp_config(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pp.pprint(yaml)



    def _print(self):
        self.load_mod_file(self.mod)
        self.pp_config()



    def _network(self):


        yaml = self.load_config()
        print yaml




class Module(BaseModule):

    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)
        pass





if __name__ == '__main__':

    os.environ['KMODROOT'] = 'tests/'

    m = KMod(sys.argv[1:])

    #debug
    #m = KMod('load', 'gcc', '4.8.1')

    #m.pp_config()
    #m.pp_resolved()

    #m.export()



