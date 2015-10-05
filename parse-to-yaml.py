#!/usr/bin/env python


import os
import yaml
import pprint

mod = 'icc'


MAP = {'append-path': 'append',
       'prepend-path': 'prepend',
       'setenv': 'setenv',
       'prereq': 'prereq',
       'set-alias': 'alias',
       'conflict': 'conflict',
       }


ignore = [
    "common_setup",
    "GeneralAppSetup",
    "} else {",
    "module load",
    ]

def add2list(param, config):
    name, val = param[:2]
    name = MAP[name]

    if name not in config:
        config[name] = dict()

    if val in config[name]:
        config[name].append(val)
    else:
        config[name] = [val] 



def add3list(param, config):
    name, key, val = param[:3]
    name = MAP[name]

    if name not in config:
        config[name] = dict()

    if key in config[name]:
        config[name][key].append(val)
    else:
        config[name][key] = [val] 


def additem(param, config):
    name, key, val = param[:3]
    name = MAP[name]

    if name not in config:
        config[name] = dict()

    config[name][key] = val

def parsit(mod, filename):
    config = dict()
    with open(filename + '/.base') as f:
        cannot_parse = list()

        for line in f:
            ignoreme = False
            line = line.strip()
            param = line.split()
            if not param:
                continue

            if line.startswith('#'):
                continue

            if line.startswith('if ![is-loaded'):
                continue

            for i in ignore:
                if i in line:
                    ignoreme = True
            if ignoreme:
                continue
            if line.startswith("}"):
                continue



            if param[0] in ['prepend-path', 'append-path']:
                add3list(param, config)

            elif param[0] in ['prereq', 'set-alias', 'conflict']:
                add2list(param, config)

            elif param[0] in ['setenv']:
                additem(param, config)

            elif param[0] == 'set':
                config[param[1]] = param[2]

            elif param[0] == 'module' and param[1] == 'add':
                if len(param) > 3:
                    
                    print "TOO MANY MODULE ADD"*3
                    print line
                    print param
                tmp = ['prereq']
                tmp.extend(param[2:])
                add2list(tmp, config)

            else:
                cannot_parse.append('Cannot Parse "%s"' % line)


    config['module'] = mod
    config['groups'] = ['applications']


    # Versions, need to check links then create yaml file for every .base*
    # report the apps with multiple bases IN USE  ie links to multiple base
    #os.path.islink('SE-10.1b')
    #>> os.readlink('SE-10.1b')
    #'.base'


    config['versions'] = list()

    base = list()
    for i in os.listdir(filename):
        if not os.path.islink(filename + '/' + i):
            continue
        
#        print mod + '  version  ' + i
        config['versions'].append(i)

        if i.startswith('.base'):
            base.append(i)
    if len(base) > 1:
        print mod, base



    with open('yaml/' + mod + '.yaml', 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False))
            
#    if cannot_parse:
#        print filename
#        print '\n'.join(cannot_parse)
#        print '\n'


root = '/opt/share/modules/applications-extra/'
dirs = os.listdir(root)


for d in dirs:
    filename = root + d
    parsit(d, filename)

    #pp = pprint.PrettyPrinter(indent=4)
    #pp.pprint(config)



