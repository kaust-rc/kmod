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



def get_default(root, mod):
    """
    Gets the defualt version from the file .modulerc from the 
    format like this:

    module-version netcdf/4.1.3 default
    """
    try:
        with open(root + mod + '/.modulerc', 'r') as desc:
            line = desc.readlines()
    except:
        return None

    line = line[1] if line[1] != '\n' else line[2]

    default = line.split()[1].split('/')[1]
    return default


def parse_base(root, mod, basefile, grp):


    config = dict()
    with open(root + '/' + mod + '/' + basefile) as f:
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
    config['versions'] = versions[mod][basefile]
    config['default_version'] = get_default(root, mod)

    config['groups'] = [grp]


    try:
        with open(root + mod + '/.desc', 'r') as desc:
            desc = desc.read()
    except:
        desc = ''
    config['desc'] = desc.strip()




    #Write the file to disc
    if len(versions[mod]) > 1:
        filename = 'yaml/' + mod + basefile + '.yaml'
    else:
        filename = 'yaml/' + mod + '.yaml'


    with open(filename, 'w') as outfile:
        outfile.write( yaml.dump(config, default_flow_style=False))
            


    return config



#    if cannot_parse:
#        print filename
#        print '\n'.join(cannot_parse)
#        print '\n'




def get_versions(root, grp, mod):
    """
    Scans the module directory and build the version dict 

    {mod: {basefile : [list, of, versions], groups: group}

    """
    versions[mod] = {'groups': grp + '-extra'}

    d = root + grp + '-extra/' + mod

    for i in os.listdir(d):
        if not os.path.islink(d + '/' + i):
            continue

        link = os.readlink(d + '/' + i)

        if link not in versions[mod]:
            versions[mod][link] = list()

        versions[mod][link].append(i)

    # TODO Test if any versions in groups






data = dict()
versions = dict()
pp = pprint.PrettyPrinter(indent=4)
root = '/opt/share/modules/' 

for r in ['applications', 'compilers', 'libs']:
    mods = os.listdir(root + r)
    for m in mods:
        get_versions(root, r, m)


pp.pprint(versions)
for mod in versions:
    for basefile in versions[mod]:
        if basefile == 'groups':
            continue
        root = '/opt/share/modules/' + versions[mod]['groups']
        print 'parsing', root, mod, basefile

        data[mod] = parse_base(root, mod, basefile, r)
            
exit()

pp.pprint(data)




for i in versions:
    if len(versions[i])>1:
        print 'multiple versions of module ', i

