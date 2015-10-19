

import networkx as nx
import os
import yaml

DIR = 'yaml/'



from py2neo import authenticate, Graph, Node, Relationship
from py2neo import neo4j


authenticate("localhost:7474", "neo4j", "niall")

graph = Graph("http://localhost:7474/db/data/")
graph.delete_all()

#graph.schema.create_uniqueness_constraint("App", "name")
#graph.schema.create_uniqueness_constraint("Version", "name")


def load_yaml_file(filename):
    """
    Errors should be ignored but logged.
    """
    try:
        config =  yaml.load(file(DIR+filename))

    except:
        print 'not found', filename


    #TODO, some error checking, eg if file exists
    return config



for filename in os.listdir(DIR): 
    #modfiles = [i for i in os.listdir(DIR) if mod in i and i.endswith('.yaml')]

    config = load_yaml_file(filename)
    
    if 'module' not in config:
        print "ERROR no moduel in file", filename
        continue
    mod = config['module']

    grp = config['groups'].split('-')[0]
    module = graph.merge_one(grp, 'name', mod)


    for v in config['versions']:
        vers = graph.merge_one(grp+'Version', 'name', v+mod)
        r = Relationship(module, 'has', vers)
        graph.create(r)
        for p in config.get('prereq', []):

            if '/' in p:
                premod = p.split('/')[0]
                prevers = p.split('/')[1]
            else:
                premod = p
                prevers = 'default'
            
            prereqv = graph.merge_one('Version', 'name', prevers+premod)
            pre = Relationship(vers, 'requires', prereqv) 

            graph.create(pre)






