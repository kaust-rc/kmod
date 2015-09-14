#!/usr/bin/env python

import os
import re
import sys
import yaml

import pprint

import yaml


if len(sys.argv) >= 2 and sys.argv[1] == 'debug':
    print 'Argument List: %s' % (sys.argv)
    DEBUG = True
    args = sys.argv[2:]
else:
    DEBUG = False
    args = sys.argv[1:]


cmd = args[0] if len(args) >= 1 else None
mod = args[1] if len(args) >= 2 else None
vers = args[2] if len(args) >= 3 else None





keywords = ['prepend', 'append', 'env']



cmds = ['load', 'unload', 'show', 'avail', 'purge', 'list']



keywords = ['prepend', 'append', 'setenv', 'prereq', 'postreq', 'conflict', 'alias']
meta = ['groups', 'bundles', 'name', 'versions', 'preload-yaml', 'verbosity']
forbidden = ['group', 'bundle', ]  #version, name???



class Module(object):


    def __init__(self, mod='common'):
        self.pp = pprint.PrettyPrinter(indent=4)
       
        self.filename = mod + '.yaml'
    
        self.load_yaml()


        self.validate_config()

        #sets self.macros = macro variables, ie not keywords or meta info
        self.get_macros()

        if DEBUG:
            print cmd, mod, vers
            self.pp_config()



    def load_yaml(self):
        self.config = yaml.load(file(self.filename))


    def pp_config(self):
        self.pp.pprint(self.config)


    def validate_config(self):
        for i in self.config.keys():
            if '$' in i:
                print i*5
                raise Exception
        for i in forbidden:
            if i in self.config:
                print i*5
                raise Exception


    def export(self):
        pass


    def get_path(self):
        """
        Test function just to get a prepend-path
        """
        path = self.config['prepend']['PATH']
        
        print self.interpolate(path)


    def get_macros(self):
        tmp = [i for i in self.config]# if i not in meta]
        tmp = [i for i in tmp if i not in keywords]

        self.macros = dict()
        for i in tmp:
            self.macros[i] = str(self.config[i])

        for i in tmp:
            self.macros[i] = self.interpolate_macros(self.macros[i])
        


    def interpolate_macros(self, val):
        """
        Interpolates the macros themselves,
            if they contain macros in each other
        """
        #If there are more than 20 deep macros then change the yamp
        for i in range(20):

            val = self.interpolate(val)
            if '$' not in val:
                return val

        raise Exception("Too much depth in recursion")        


    def interpolate(self, val):
        """
        Scans the val for macro variables, and substitutes
        """
        found = [ i[1:] for i in val.split('/') if i.startswith('$')]

        if not found:
            print 'not found ', val
            return val

        notfound = list()
        for i in found:
            if i in self.macros:
                val = val.replace('$' + i, self.macros[i])
            else:
                notfound.append(i)

        if notfound:
            print 'ERROR ' + str(notfound) + 'not in macros'
            raise Exception

        return val



    def get_val(self, val):
        val = self.interpolate(val)
        if '$' in val:
            print 'error $ still in val'
            raise Exception
        return val

    def resolved(self):
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






def prepend(env, val):
    if env not in os.environ:
        os.environ[env] = val
        return

    envvar = os.environ[env].split(':')
    envvar.insert(0, val)
    os.environ[env] = ':'.join(envvar)


def remove(env, val):
    if env not in os.environ:
        return

    envval = os.environ[env].split(':')

    if val in envval:
        envval.remove(val)
        #to remove every instance
        #envval = [i for i in envval if i != val]

    os.environ[env] = ':'.join(envval)



def main():

    if cmd == 'load':


        for var in config.get('prepend', []):
            if isinstance(config['prepend'][var], list):
                for val in config['prepend'][var]:
                    prepend(var, val)

            elif isinstance(config['prepend'][var], str):
                prepend(var, val)

        prepend('LOADEDMODULES', mod)


        export = ' '.join(['%s="%s"' % (i, os.environ[i]) for i in config['prepend']])
        export += ' LOADEDMODULES="%s"' % (os.environ['LOADEDMODULES'])

        if export:
            print 'export %s' % (export)


    elif cmd == 'unload':
        for var in config.get('prepend', []):
            if isinstance(config['prepend'][var], list):
                for val in config['prepend'][var]:
                    remove(var, val)

            elif isinstance(config['prepend'][var], str):
                remove(var, val)

        remove('LOADEDMODULES', mod)


        export = ' '.join(['%s="%s"' % (i, os.environ[i]) for i in config['prepend'] if os.environ[i] != ''])
        export += ' LOADEDMODULES="%s"' % (os.environ['LOADEDMODULES'])

        #TODO add regex for multiple '\:.*'
        export = export.replace('::', ':')
        if export:
            print 'export %s' % (export)

        
        unset = ' '.join(['%s' % (i) for i in config['prepend'] if os.environ[i] == ''])
        if unset:
            print "unset %s" % (unset)





if __name__=='__main__':
    m = Module('gcc')
    m.pp_config()

    m.resolved()

