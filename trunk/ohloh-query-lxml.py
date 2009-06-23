#!/usr/bin/env python
# encoding: utf-8
"""
ohloh-query-lxml.py

There is a dependency on lxml and BeautifulSoup. On OS X you can get these with MacPorts or easy_install-2.5.

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
    
    def request_scrape(self, resource):
        full_resource = resource # + '?' + '&api_key=' + self.api_key
        return self.conn.request(full_resource)
    
    def request_api(self, resource):
        full_resource = resource + '?' + '&api_key=' + self.api_key
        return self.conn.request(full_resource)
        
    def single_api(self, path, ident):
        return self.request_api(path + '/' + str(ident) + '.xml')
        
    def multiple_api(self, path, query):
        return self.request_api(path + '.xml?query=' + query)
        
    def project(self, ident):
        return self.single_api('projects', ident)
        
    def projects(self, query):
        return self.multiple_api('projects', query)
        
    def account(self, ident):
        return self.single_api('accounts', ident)
    
    def accounts(self, query):
        return self.multiple_api('accounts', query)
    
    def projects_contributers(self, ident):
        return self.request_api('projects' + '/' + str(ident) + '/' + 'contributors' + '.xml?sort=commits')
        
    # def contributor_language_fact(self):
    #     return self.request_api('projects' + '/' + str(ident) + '/' + 'contributors' + '.xml?sort=commits')
    #     # extract contributor_language_fact in 'result > contributor_fact > contributor_language_facts'
    #     # for each contributor_language_fact extract man_months
    
    def language_scrape(self, ident):
        return self.request_scrape('languages/' + str(ident))

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
    
    ## Hack hack hack
    # sel = CSSSelector('result > contributor_fact')
    # for fact in sel(root):
    #     print 'Contributer name: ' + fact['contributor_name'].text


def get_language_by_project(ohloh, ident):
    data = ohloh.project(ident)

    if not data:
        sys.exit("No data")

    root = ohloh.parse_xml(data)
    # print lxml.etree.tostring(root, pretty_print=True)
    
    sel = CSSSelector('analysis > main_language_id')
    # for language in sel(root):
    #     print 'main language: ' + language.text
    
    return sel(root)


def get_programmers_by_languages(ohloh, lang_list):
    for language_id in lang_list:
        data = ohloh.language_scrape(language_id.text)
        
        if not data:
            sys.exit("No data")
        
        root = ohloh.parse_xml(data)
        # print lxml.etree.tostring(root, pretty_print=True)
        
        ## Most Experienced Contributors
        sel = CSSSelector('div.col.span_6.piano > div.inset > a.contributor > div.name')
        for programmer in sel(root):
            print 'programmer: ' + programmer.text
        
    pass


def main():
    api_key = '1xe6mtGfqDLsq7tMdV2hg'
    
    proj_ident = 1 # Subversion
    
    ohloh = Ohloh(api_key)
    print_project_name(ohloh, proj_ident)
    # print_project_contributers(ohloh, proj_ident)
    
    ## Find programming language(s) used by project
    language_list = get_language_by_project(ohloh, proj_ident)
    for language_id in language_list:
        print 'Main language: ' + language_id.text

    ## Find programmers who can program (all) these languages
    programmer_list = get_programmers_by_languages(ohloh, language_list)
    
    ## Remove inactive programmers
    ## Remove over-active programmers


if __name__ == '__main__':
    main()
