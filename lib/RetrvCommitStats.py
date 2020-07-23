#!/usr/bin/python

from lib.System import System
from lib.CommitCollector import CommitCollector
import requests
import os
import csv
import pandas as pd
import json

class RetrvCommitStats(CommitCollector):

    def __init__(self, cmmtFile, Task, UserName, Token):
        self.cmmtFile = cmmtFile
        super(RetrvCommitStats, self).__init__(Task, UserName, Token)
   
    #Collect statistics for all files changed in given commit
    def parse_stats(self, commit_url):
        result = self.http_get_call(commit_url)
        if (result == None):
            return
        
        files = result['files']
        for file in files:
            stats = {}
            if (self.is_filtered (file['filename'])):
                continue
            stats['filename'] = file['filename']
            stats['status'] = file['status']
            stats['additions'] = file['additions']
            stats['deletions'] = file['deletions']
            stats['changes'] = file['changes']
            if('patch' in file.keys()):
                stats['patch'] = file['patch']
            else:
                stats['patch'] = ""
            stats['contents_url'] = file['contents_url']
            
            self.Output.append(stats)
 
    #Iterate over all the commits in the repository and
    #collect commit statistics by constructing the url
    #which compares commits with their parent(s)
    def process(self, RepoId, RepoUrl=None):
        cdf = pd.read_csv(self.cmmtFile)       
        for index, row in cdf.iterrows():
            #if the commit is a merge with two parents
            if(',' in str(row['parents'])):
                parent1 = row['parents'].split(',')[0]
                parent2 = row['parents'].split(' ')[1]
                stats_url1 = RepoUrl + "/compare/" + parent1 + "..." + row['sha']
                stats_url2 = RepoUrl + "/compare/" + parent2 + "..." + row['sha']
                self.parse_stats(stats_url1)
                self.parse_stats(stats_url2)
            #only one parent
            else:
                stats_url = RepoUrl + "/compare/" + str(row['parents']) + "..." + row['sha']
                #make sure we have not reached the last commit
                if ("nan" not in stats_url):
                    self.parse_stats(stats_url)
                    
            if (len(self.Output) == 0):
                continue
                
            StatFile = self.get_stats_path (RepoId, index)
            self.write_csv (StatFile)
            print ("\t[Task%d-%d/%d]Stats -> %d" %(self.Task, index, cdf.shape[0], len(self.Output)))
            self.Output = []



