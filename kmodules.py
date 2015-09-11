#!/usr/bin/env python

import os
import re
import yaml

import pprint

import yaml

pp = pprint.PrettyPrinter(indent=4)



#common = yaml.load(file('common.yaml'))
#icc = yaml.load(file('icc.yaml'))
gcc = yaml.load(file('gcc.yaml'))


replace = re.compile(r'\$([a-z|_|-]*?)[\/| |\$\.\,]')

#pp.pprint(common)
#pp.pprint(icc)
pp.pprint(gcc)

keys = gcc.keys()

keywords = ['prepend', 'append', 'env']

d = gcc
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



