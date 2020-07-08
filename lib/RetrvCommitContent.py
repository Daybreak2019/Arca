#!/usr/bin/python
from lib.System import System
from lib.CommitCollector import CommitCollector
import csv
import pandas as pd
import json
import base64
import re

class RetrvCommitContent(CommitCollector):
    def __init__(self, cmmtFile, Task, UserName, Token):
        self.cmmtFile = cmmtFile
        super(RetrvCommitContent, self).__init__(Task, UserName, Token)
        
        #[".mailmap", ".nvmrc", ".md", ".git", ".lock"]
        self.FilterRule =  re.compile(r'(^\.[a-zA-Z]|\.lock|\.md$)')
        
    def is_filtered (self, FileName):
        #FilterList = 
        return self.FilterRule.match(FileName)
     
    def parse_commits(self, commit_url):
        result = self.http_get_call(commit_url)
        if (result == None):
            return
        
        allitems = result['tree']
        for item in allitems:
            if item['type'] == 'tree':
                #self.parse_commits(item['url'])
                pass
            else:
                if (self.is_filtered (item['path']) or
                    (item.__contains__('url') == False)):
                    continue
                    
                result2 = self.http_get_call(item['url'])
                if (result2 == None):
                    continue
                content = result2['content']
                content = base64.b64decode(content)
                
                record = {}
                record['path'] = item['path']
                record['type'] = item['type']
                record['content'] = content
                
                self.Output.append(record)
       
    def process(self, id, url=None):
        CommitIndex = 0
        cdf = pd.read_csv(self.cmmtFile)
        urls = cdf['commits']
        for url in urls:           
            self.parse_commits(url)
            if (len(self.Output) == 0):
                CommitIndex += 1
                continue
            
            ContentFile = self.get_content_path (id, CommitIndex)
            self.write_csv (ContentFile)
            print ("\t[Task%d-%d/%d]Content -> %d" %(self.Task, CommitIndex, len(urls), len(self.Output)))
            
            self.Output = []
            CommitIndex += 1
 

    