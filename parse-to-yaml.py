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
    'GeneralLibSetup',
    'GeneralCompilerSetup',
    'puts stderr',
    ]


def add2list(param, config):
    """
    conflict a b c
    prereq a
    """

    name, val = param[0], param[1:]
    name = MAP[name]


    if name in config:
        config[name].extend(val)
    else:
        config[name] = val



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



def get_default(root, grp, mod):
    """
    Gets the defualt version from the file .modulerc from the 
    format like this:

    module-version netcdf/4.1.3 default
    """
    try:
        with open(root + grp + '/' + mod + '/.modulerc', 'r') as desc:
            line = desc.readlines()
    except:
        return ''

    line = line[1] if line[1] != '\n' else line[2]

    default = line.split()[1].split('/')[1]
    return default





def parse_base(basefile, mod):

    config = dict()
    
    grp = basefile.split('-')[0]
    grp = grp.split('/')[-1]


    with open(basefile) as f:
        if '$app_dir' in f.read():
            config['app_dir'] = '/opt/share/module/' + mod



    with open(basefile) as f:
        cannot_parse = list()

        for line in f:
            
            #Replace some old function variables
            line = line.replace('module_name', 'module')
            line = line.replace('${app_dir}', '$app_dir')
            line = line.replace('${version}', '$version')


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
    config['versions'] = versions[mod][basefile].keys()
    config['default_version'] = get_default(root, grp, mod)


    try:
        with open(root + mod + '/.desc', 'r') as desc:
            desc = desc.read()
    except:
        desc = ''
    config['desc'] = desc.strip()



    #Write the group *-extra to module file
    config['groups'] = basefile.split('/')[4]

    #Write the file to disc
    if len(versions[mod]) > 1:
        filename = 'yaml/' + mod + basefile.split('/')[-1] + '.yaml'
    else:
        filename = 'yaml/' + mod + '.yaml'


    with open(filename, 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False))
            

    if cannot_parse:
        print filename
        print '\n'.join(cannot_parse)
        print '\n'

    return config






def get_versions(root, grp, mod):
    """
    Scans the module directory and build the version dict 

    {mod: {basefile : [list, of, versions], groups: group}


    TODO: FIGURE OUT WHAT TO DO WITH AVAIL and module load extra

    """
    versions[mod] = dict()

    d1 = root + grp + '-extra/' + mod
    d2 = root + grp + '/' + mod
    for v in os.listdir(d1):
        if not os.path.islink(d1 + '/' + v):
            continue

        base = os.readlink(d1 + '/' + v)

        base = d1 + '/' + base

        if base not in versions[mod]:
            versions[mod][base] = dict()

        
        versions[mod][base][v] = [grp+'-extra']


        if os.path.islink(d2 + '/' + v):
            versions[mod][base][v].append(grp)





data = dict()
versions = dict()
pp = pprint.PrettyPrinter(indent=4)
root = '/opt/share/modules/' 

for r in ['applications', 'compilers', 'libs']:

    mods = os.listdir(root + r + '-extra/')
    for m in mods:
        get_versions(root, r, m)

#Print the version data
#pp.pprint(versions)


for mod in versions:
    for basefile in versions[mod]:
        data[mod] = parse_base(basefile, mod)
#pp.pprint(data)


#create the group files
for r in ['applications', 'compilers', 'libs']:
    config = {'group': r, 'modules': list()}
    for m in versions:
        for b in versions[m]:
            for v in versions[m][b]:
                for g in versions[m][b][v]:
                    if not g.endswith('-extra'):
                        if g == r:
                            config['modules'].append(m)

    with open('yaml/' + r + '.yaml', 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False))





for i in versions:
    if len(versions[i]) > 1:
        print 'multiple versions of basefile for module ', i





