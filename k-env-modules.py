#!/usr/bin/env python

import sys, os
import re
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

#TODO should be, to allow multiple apps varsions etc...
#cmd = args[0] if len(args) >= 1 else None
#mod_vers = args[1:]


config = yaml.load(file(mod + '.yaml'))

if DEBUG:
    print cmd, mod, vers

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(config)


cmds = ['load', 'unload', 'show', 'avail', 'purge', 'list']
keywords = ['prepend', 'append', 'env']



def load_yaml(mod):
    replace = re.compile(r'\$([a-z|_|-]*?)[\/| |\$\.\,]')

    d = config
    if 'prepend' in d:
        prepend = d['prepend']



    def macro2(val, keys):
        found = re.findall(replace, val)
        for i in found:
            if i in keys:
                val = val.replace('$'+str(i), str(d[i]))
            else:
                print i + "not found"
                raise Exception
        return val

    keys2 = keys[:0]
    for k in keys:
        keys2.append(macro2(d[k], keys2))
    print keys2

    for key in prepend:
        if isinstance(prepend[key], list):
            for val in prepend[key]:

                print 'prepend', key, macro2(val, keys2)


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







