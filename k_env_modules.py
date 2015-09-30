#!/usr/bin/env python

__author__ = "Niall OByrnes"
__version__ = "0.0.1"


import os
import re
import sys
import yaml
import pprint

from help_text import help_text

#import logging
#logging.basicConfig(level=logging.DEBUG,
#       format='%(asctime)s %(levelname)s %(message)s')


#module [cmd]  a list of the allowable commands
cmds = ['load', 'unload', 'show', 'avail', 'purge', 'list', 'help', 'version']

#Admin command
acmds = ['report', 'validate']


#Keywords reserved for module application
keyword_strings = ['setenv']
keyword_lists = ['prepend', 'append', 'prereq', 'postreq', 'conflict', 'alias']

#Parameters reserved for module application
meta_strings = ['name', 'default_version']#, 'verbosity']
meta_lists = ['groups', 'bundles', 'versions', 'preload-yaml',]

#Give error for these for now
confusion = ['names', 'bundle', 'group']

#Module program keywords
mod_keywords = ['version', 'case']



#TODO should be picked up from admin.yaml, or an environment variable or something
#DIR = '/opt/share/kmodules/'
#DIR = 'yaml/'
DIR = 'tests/'


class Module(object):


    def __init__(self, cmd='help', mod='', vers=''):

        self.cmd = cmd
        self.mod = mod
        self.req_version = vers


        self.call_function() 


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


    def _error(self, msg):
        """
        Should print to stderr???
        """
        self._echo(msg)
        exit(1)


    def call_function(self):
        """
        Checks and calls the function from the args

        With only a short number of commands, there are no overlap of
        switches and commands so its easy to jsut duplicate every
        command with a switch

        If more comands are added then maybe move to getopt    
        """
        cmd = self.cmd.replace('-', '')
        cmd = cmd.lower().strip()

        switch = [i[0] for i in cmds]
        if cmd in cmds:
            getattr(self, '_'+cmd)()

        elif cmd in switch:
            cmd = cmds[ switch.index(cmd) ]
            getattr(self, '_'+cmd)()

        else:
            self._error("ERROR: subcommand '%s' not recognised\n" % (cmd))


    def _help(self):
        """
        Prints the help message
        """
        self._echo(help_text())


    def _version(self):
        """
        Prints the version
        """
        self._echo("VERSION=%s" % __version__)


    def load_yaml_file(self, filename):
        """
        Errors should be ignored but logged.
        """
        self.filename = DIR + self.mod + '.yaml'
        try:
            config =  yaml.load(file(filename))

        except:
            self._error("cannot open module file %s" % self.filename)
            

        #TODO, some error checking, eg if file exists
        return config




    def _get_version(self):
        """
        If the same yaml file is used for multiple versions, then the version 
        keyword will be the loaded (or default) version

        default_version is the default version
        versions are the allowed versions

        if the user does module load version, then this version
            takes precedence of version, and is used as the macro $version 

        """
        if self.req_version:
            if 'versions' in self.config:
                if self.req_version not in self.config['versions']:

                    msg = "Requested version %s not available for %s.\n" % (self.req_version, self.mod)
                    msg += "Versions available %s" % (', '.join(self.config['versions']))
                    self._error(msg)
                else:
                    self.config['version'] = self.req_version


        elif 'default_version' in self.config:
            if 'versions' in self.config:
                if self.config['default_version'] not in self.config['versions']:

                    msg = "Error in module file, default version %s not available for %s.\n" % (self.config['default_version'], self.mod)
                    self._error(msg)

            self.config['version'] = self.config['default_version']

        else:
            #Cannot determine any version
            self.config['version'] = 'version_unavailable'
            return


    def load_config(self):
        """
        Loads the yaml file and interpolates the macro variables
        """
        self.config = self.load_yaml_file(DIR+'common.yaml')
        self.config.update(self.load_yaml_file(self.filename))

        self.validate_config()

        self._get_version()

        self.interpolate_macros()



    def validate_config(self):
        for i in mod_keywords:
            if i in self.config:
                raise Exception
        for i in confusion:
            if i in self.config:
                raise Exception


    def correct_types_in_config(self):
        """
        Ensure, setenv are strings
                prepend, postpend are lists
        Validate is more indept and is found in KModule
        """
        for i in keyword_lists:
            for l in self.config.get(i, list()):
                if isinstance(self.config[i][l], str):
                    self.config[i][l] = [ self.config[i][l] ]

        for i in keyword_strings:
            for s in self.config.get(i, ''):
                if isinstance(self.config[i][s], list):

                    #Takes the first entry
                    if len(self.config[i][s]) >= 1:
                        print "ERROR: Truncated %s %s" % (i, s)
                        self.config[i][s] = self.config[i][s][0]
                    else:
                        self.config[i][s] = ''

        #Ensure all macros are strings
        macs = self._get_macros()
        for i in macs:
            self.config[i] = str(self.config[i])


    def pp_config(self):
        self.pp = pprint.PrettyPrinter(indent=4)
        self.pp.pprint(self.config)


    def _get_macros(self):
        """
        The kwywords normally take a list, so it couldnt be used as a macro;
        Possible exception with setenv, as its just one variable.  However,
        if someone wants to use it as a macro, then set a macro and put
        the macro in the setenv

        Also macro variables must be a string
        """
        tmp = [i for i in self.config
                if i not in keyword_lists and 
                   i not in keyword_strings and
                   #i not in meta_strings and
                   i not in meta_lists and
                   not isinstance(self.config[i], dict) and
                   not isinstance(self.config[i], list)
                   ]


        return tmp



    def interpolate_macros(self):
        """
        Scans all parameters and inserts the macros
        """
        self.correct_types_in_config()

        #Possible macros
        macs = self._get_macros()

        for i in macs:
            if '$' in self.config[i]:
                self.config[i] = self.interpolate(i, self.config[i])

        #now test keywords
        for k in keyword_lists:
            if k not in self.config:
                continue
            for l in self.config[k]:
                for i,v in enumerate(self.config[k][l]):
                    if '$' in v:
                        self.config[k][l][i] = self.interpolate('atest', v)


    def interpolate(self, var, val):
        """
        Scans the val for macro variables, and substitutes
        """
        if '$' not in val:
            return val

        found = [ i[1:] for i in val.split('/') if i.startswith('$')]
        if var in found:
            self._error("Circular References in %s" % var)

        notfound = list()
        for i in found:
            if i in self.config:
                val = val.replace('$' + i, self.config[i])
            else:
                notfound.append(i)

        if notfound:
            self._error('ERROR %s not in macros' % (notfound))

        if '$' in val:
            val = self.interpolate(var, val)

        #TODO This will remove duplicate /'s But should it just report error???
        val = re.sub(r'\/{2,}', '/', val)
        return val



    def get_val(self, val):
        val = self.interpolate(val)
        if '$' in val:
            print 'error $ still in val'
            raise Exception
        return val


    def pp_resolved(self):
        """
        Temporary function for debug
        """
        for i in self.macros:
            print i, self.macros[i]

        for i in self.config:
            if i in self.macros:
                continue

            if isinstance(self.config[i], dict):
                for keyword in self.config[i]:
                    if isinstance(self.config[i][keyword], list):
                        for j in self.config[i][keyword]:
                            print j, self.interpolate(j)
            #else:
            #    print 'resolved', i, self.interpolate(self.config[i])


    def get_path(self):
        """
        Test function just to get a prepend-path
        """
        path = self.config['prepend']['PATH']

        print self.interpolate(path)


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



    def _load(self):
        """
        Executes the module load command
        """
        if not self.mod:
            self._error("Error: no module")

        self.load_config()

        export_set = set('LOADEDMODULES')

        for env in self.config.get('prepend', []):
            for val in self.config['prepend'][env]:
                self._prepend(env, val)
                export_set.update(env)

        for env in self.config.get('append', []):
            for val in self.config['append'][env]:
                self._append(env, val)
                export_set.update(env)

        for alias in self.config.get('alias', []):
            for val in self.config['alias'][alias]:
                pass


        self._append('LOADEDMODULES', self.mod)


        for i in export_set:
            export += ' '.join(['%s="%s"' % (i, os.environ[i]))


        self._export(export)








    def _unload(self):
        for var in self.config.get('prepend', []):
            for val in self.config['prepend'][var]:
                self.remove(var, val)


        self.remove('LOADEDMODULES', self.mod)


        export = ' '.join(['%s="%s"' % (i, os.environ[i]) for i in self.config['prepend'] if os.environ[i] != ''])
        export += ' LOADEDMODULES="%s"' % (os.environ['LOADEDMODULES'])

        #TODO add regex for multiple '\:.*'
        export = export.replace('::', ':')
        if export:
            print 'export %s' % (export)


        unset = ' '.join(['%s' % (i) for i in self.config['prepend'] if os.environ[i] == ''])
        if unset:
            print "unset %s" % (unset)





class KModule(Module):

    def __init__(self, *args, **kwargs):
        super(ChildB, self).__init__(*args[1:], **kwargs)

        print cmd, mod, vers
        self.pp_config()


        self.validate_config()

    def validate_config(self):
        for i in self.config.keys():
            if '$' in i:
                print i*5
                raise Exception
        for i in forbidden:
            if i in self.config:
                print i*5
                raise Exception


    def load(self):
        """
        Prints a formatted version of config
        """

        export = self._load()

        #prittyprint
        print 'export %s' % (export)





if __name__ == '__main__':




    if len(sys.argv) > 1 and sys.argv[1] == 'debug':
        m = KModule(*sys.argv[2:])
    else:
        m = Module(*sys.argv[1:])

    #debug
    #m = Module('load', 'gcc', '4.8.1')

    #m.pp_config()
    #m.pp_resolved()

    #m.export()



