#!/usr/bin/env python


import os
import glob
import cherrypy

from load_yaml import LoadYaml

import yaml







def get_all_files():
    """
    Looks for the yaml file at module* and module*/*

    returns: list of filenames
             list of yaml dicts
    """
    m = LoadYaml()
    m.get_all_yamls()


    print m.yaml_files

    return m.filenames, m.yaml_files



def admin_parse():
    filenames, data = get_all_files()

    html = "<html><table border=1>"
    for yml in data:
        mod = yml.get('module', 'Error')
        
        versions = yml.get('active_versions', [])
        
        vtext = ""
        for v in versions:
            vtext += "<td><a href='module/%s/%s'>%s</a></td>" % (mod, v, v)


        html += "<tr><td><a href='module/%s'>%s</a></td><td>%s</td></tr>" % (mod, mod, vtext)

    html += "</table></html>"
    return html






def mod_parse(mod, version):

    m = LoadYaml(mod, version)
    
    try:   
        m.load()

    except:
        txt = {"ERROR": "ERROR"}
    else:
        txt = m.yaml
    

    text = prettyTable(txt)

    return "<html>" + text + "</html>"





def desc():
    _, data = get_all_files()

    html = "<html><table border=1>"
    for yml in data:

        versions = ", ".join(yml.get('versions', []))
        

        html += "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (yml.get('module', 'No name'), versions, yml.get('desc'))

    html += "</table></html>"
    return html





#http://www.stevetrefethen.com/blog/pretty-printing-a-python-dictionary-to-html
def prettyTable(dictionary, cssClass=''):
        ''' pretty prints a dictionary into an HTML table(s) '''
        if isinstance(dictionary, str):
            return '<td>' + dictionary + '</td>'
        s = ['<table ']
        if cssClass != '':
            s.append('class="%s"' % (cssClass))
        s.append('>\n')
        for key, value in dictionary.iteritems():
            s.append('<tr>\n  <td valign="top"><strong>%s</strong></td>\n' % str(key))
            if isinstance(value, dict):
                if key == 'picture' or key == 'icon':
                    s.append('  <td valign="top"><img src="%s"></td>\n' % prettyTable(value, cssClass))
                else:
                    s.append('  <td valign="top">%s</td>\n' % prettyTable(value, cssClass))
            elif isinstance(value, list):
                s.append("<td><table>")
                for i in value:
                    s.append('<tr><td valign="top">%s</td></tr>\n' % prettyTable(i, cssClass))
                s.append('</table>')
            else:
                if key == 'picture' or key == 'icon':
                    s.append('  <td valign="top"><img src="%s"></td>\n' % value)
                else:
                    s.append('  <td valign="top">%s</td>\n' % value)
            s.append('</tr>\n')
        s.append('</table>')
        return '\n'.join(s)




class KModuleReport(object):
    @cherrypy.expose
    def index(self):
        return "<html><p><a href='admin'>Admin</a></p><p><a href='user'>User</a></p></html>"

    @cherrypy.expose
    def admin(self):
        return admin_parse()


    @cherrypy.expose
    def module(self, mod, version=None):
        return mod_parse(mod, version)


    @cherrypy.expose
    def user(self):
        return desc()


if __name__ == '__main__':
    #get_all_files()
    #print desc()
    cherrypy.quickstart(KModuleReport())
