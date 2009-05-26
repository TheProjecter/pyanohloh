#!/usr/bin/env python
# encoding: utf-8
"""
ohloh-query-lxml.py

Created by Henk Poley on 2009-04-22.
Copyright (c) 2009. All rights reserved.
"""

import sys
import urllib2

import lxml.html
import lxml.html.soupparser
import lxml.etree # lxml.etree.tostring(root, pretty_print=True)
from lxml.cssselect import CSSSelector

class Connection:
    def __init__(self, base_url):
        self.base_url = base_url

    def request(self, resource):
        full_url = self.base_url + resource

        try:
            data = urllib2.urlopen(full_url).read()
        except urllib2.HTTPError, error:
            print "HTTP error: %d" % error.code
            return
        except urllib2.URLError, error:
            print "Network error: %s" % error.reason.args[1]
            return

        return data


class Ohloh:
    def __init__(self, api_key):
        base_url = 'http://www.ohloh.net/'
        self.conn = Connection(base_url)
        self.api_key = api_key
    
    def request(self, resource):
        full_resource = resource + '?' + '&api_key=' + self.api_key
        return self.conn.request(full_resource)
        
    def single(self, path, ident):
        return self.request(path + '/' + str(ident) + '.xml')
        
    def multiple(self, path, query):
        return self.request(path + '.xml?query=' + query)
        
    def project(self, ident):
        return self.single('projects', ident)
        
    def projects(self, query):
        return self.multiple('projects', query)
        
    def account(self, ident):
        return self.single('accounts', ident)
    
    def accounts(self, query):
        return self.multiple('accounts', query)
    
    def projects_contributers(self, ident):
        return self.request('projects' + '/' + str(ident) + '/' + 'contributors' + '.xml?sort=commits')
        
    # def contributor_language_fact(self):
    #     return self.request('projects' + '/' + str(ident) + '/' + 'contributors' + '.xml?sort=commits')
    #     # extract contributor_language_fact in 'result > contributor_fact > contributor_language_facts'
    #     # for each contributor_language_fact extract man_months

    def parse_xml(self, data):
        root = lxml.html.fromstring(data)
    
        try:
            ignore = lxml.html.tostring(root, encoding=unicode)
        except UnicodeDecodeError:
            root = lxml.html.soupparser.fromstring(data)

        return root
    

def print_project_name(ohloh, ident):
    data = ohloh.project(ident)
    
    if not data:
        sys.exit("No data")
        
    root = ohloh.parse_xml(data)
    sel = CSSSelector('project > name')
    for name in sel(root):
        print 'Project name: ' + name.text


def print_project_contributers(ohloh, ident):
    data = ohloh.projects_contributers(ident)

    if not data:
        sys.exit("No data")

    root = ohloh.parse_xml(data)
    print lxml.etree.tostring(root, pretty_print=True)
    
    sel = CSSSelector('contributor_fact > contributor_name')
    for name in sel(root):
        print 'Contributer name: ' + name.text
    
    # Hack hack hack
    # sel = CSSSelector('result > contributor_fact')
    # for fact in sel(root):
    #     print 'Contributer name: ' + fact['contributor_name'].text


def main():
    api_key = '1xe6mtGfqDLsq7tMdV2hg'
    
    ohloh = Ohloh(api_key)
    print_project_name(ohloh, 1)  # 'projects/1.xml'
    print_project_contributers(ohloh, 1)


if __name__ == '__main__':
    main()
