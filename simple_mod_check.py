#!/usr/bin/env python


import os
from subprocess import Popen, PIPE
from load_yaml import LoadYaml


def get_all_files():
    """
    Looks for the yaml file at module* and module*/*

    returns: list of filenames
             list of yaml dicts
    """
    m = LoadYaml()
    m.get_all_yamls()

    return m.filenames, m.yaml_files




#p = Popen('command', env=dict(os.environ, my_env_prop='value'))


def exec_simple_check():
    filenames, data = get_all_files()

    for yaml in data:
        module = yaml.get('module', 'Error')
        version = yaml.get('version', 'Error')

        execbin = yaml.get('exec', module)


        cmd = "module (){ eval $(python kmod.py $*); }; module purge && module load %s && %s --version" % (module, execbin)

        print cmd

        try:
        	proc = Popen(cmd, stdout=PIPE)
        	stdout = proc.stcout
        except:
            stdout = ""
            print "NOT WORKING", module, version

    	if version in stdout:
            print module, version, 'exec', execbin, 'found ', version



if __name__ == '__main__':
    import sys

    os.environ['KMODROOT'] = 'test_yaml/'

    exec_simple_check()








