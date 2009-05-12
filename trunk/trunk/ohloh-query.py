#!/usr/bin/env python
# encoding: utf-8
"""
ohloh-query.py

Created by Henk Poley on 2009-04-08.
Copyright (c) 2009 __MyCompanyName__. All rights reserved.
"""

import sys
import os
import httplib
import urlparse
import urllib
import urllib2
import base64

from BeautifulSoup import BeautifulSoup
import soupselect; soupselect.monkeypatch()

class Connection:
    def __init__(self, base_url):
        self.base_url = base_url

    def request(self, resource, method = "get", args = None):
        full_url = self.base_url + resource

        try:
            data = urllib2.urlopen(full_url).read()
        except urllib2.HTTPError, e:
            print "HTTP error: %d" % e.code
            return
        except urllib2.URLError, e:
            print "Network error: %s" % e.reason.args[1]
            return

        return urllib2.urlopen(full_url).read()

class Ohloh:
    def __init__(self, base_url, api_key):
        self.conn = Connection(base_url)
        self.api_key = api_key
    
    def request(self, resource):
        full_resource = resource + '?api_key=' + self.api_key
        return self.conn.request(full_resource)
        
    def single(self, path, id):
        return self.request(path + '/' + str(id) + '.xml')
        
    def multiple(self, path, query):
        return self.request(path + '.xml?query=' + query)
        
    def project(self, id):
        return self.single('projects', id)
        
    def projects(self, query):
        return self.multiple('projects', query)
        
    def account(self,id):
        return self.single('accounts', id)
    
    def accounts(self, query):
        return self.multiple('accounts', query)
    

def main():
    base_url = 'http://www.ohloh.net/'
    api_key = '1xe6mtGfqDLsq7tMdV2hg'
    # resource = 'projects/1.xml'

    conn = Ohloh(base_url, api_key)
    # data = conn.request(resource)
    data = conn.project(1)
    
    if not data:
        sys.exit("No data")
        
    soup = BeautifulSoup(data)
    print soup.findSelect('project > name') # returns bot project-name and used-project-names

    print soup.prettify()

if __name__ == '__main__':
    main()



