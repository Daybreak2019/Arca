#!/usr/bin/python
from lib.System import System
from lib.CommitCollector import CommitCollector
import csv
import pandas as pd
import json
import base64

class RetrvCommitContent(CommitCollector):
    def __init__(self, cmmtFile, Task, UserName, Token):
        self.cmmtFile = cmmtFile
        super(RetrvCommitContent, self).__init__(Task, UserName, Token)
        
    def parse_commits(self, commit_url):
        #print("Retrieving commit content for %s"  %(commit_url))
        result = self.http_get_call(commit_url)
        allitems = result['tree']
        for item in allitems:
            if item['type'] == 'tree':
                self.parse_commits(item['url'])
            else:                             
                result2 = self.http_get_call(item['url'])
                content = result2['content']
                content = base64.b64decode(content)
                
                record = {}
                record['path'] = item['path']
                record['type'] = item['type']
                record['content'] = content
                
                self.Output.append(record)
            
    def collect_commit_content(self, cmmtFile):
        cdf = pd.read_csv(cmmtFile)
        urls = cdf['commits']
        for url in urls:
            self.parse_commits(url)
            
    def process(self, id, url=None):
        repoId = str(id)
        repoCmmtDir = System.setdir_cmmt(repoId)
        self.collect_commit_content (self.cmmtFile)
        
        cmmtContentFile = repoCmmtDir + "/" + repoId + "_content.csv"
        self.save_file (cmmtContentFile)

    