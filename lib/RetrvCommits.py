#!/usr/bin/python

from lib.System import System
from lib.CommitCollector import CommitCollector
from lib.RetrvCommitContent import RetrvCommitContent
from lib.RetrvCommitStats import RetrvCommitStats
import os
import json
import pandas as pd


class RetrvCommits(CommitCollector):

    def __init__(self, Task, UserName, Token, RepoList):
        super(RetrvCommits, self).__init__(Task, UserName, Token, RepoList)

    #collect commit information displayed on given page
    #and add it to out list of commits for the given project
    def filter_commits(self, commits):
        commit_list = []
        
        for item in commits:
            commit_dict = {}
            
            commit_dict["sha"]     = item["sha"]
            commit_dict["author"]  = item["commit"]["author"]["name"]
            commit_dict["date"]    = item["commit"]["author"]["date"]
            commit_dict["message"] = item["commit"]["message"]
            commit_dict["commits"] = item["commit"]["tree"]["url"]
            #if no parents exist, set value to none
            if (len(item["parents"]) < 1):
               commit_dict["parents"] = None
            #if 1 parent exists, record sha
            elif (len(item["parents"]) == 1):
                commit_dict["parents"] = item["parents"][0]["sha"]
            #if 2 parents exist, records both shas separated by a comma and space
            else:
                commit_dict["parents"] = item["parents"][0]["sha"] + ", " + item["parents"][1]["sha"]
            #print (commit_dict)
            commit_list.append(commit_dict)
            
        return commit_list
    
    #Iterate over all pages of commit info to collect commits
    def collect_commits(self, url):    
        #print("Retrieve commits -> %s"  %(url))      
        page_num = 1
        while True:

            commits_url = url + "/commits?" + "per_page=100" + "&page=" + str(page_num)
            
            commits = self.http_get_call(commits_url)
            if (commits == None):
                break
            
            commit_num = len(commits)
            self.Output += self.filter_commits (commits)            
            
            page_num += 1
            if (commit_num < 100):
                break
     
    def save_file (self, RepoId):   
        CommitFile = self.get_commit_path (RepoId)
        self.write_csv (CommitFile)
        return CommitFile
        
    def process(self, RepoId, Url):
        self.collect_commits (Url)
        CmmitFile = self.save_file (RepoId)
        
        # content
        #print ("\t[Task%d]Srart Collect Commit Content -> %s" %(self.Task, Url))
        #RCC = RetrvCommitContent (CmmitFile, self.Task, self.UserName, self.Token)
        #RCC.process (RepoId)
        
        # stats
        print ("\t[Task%d]Srart Collect Commit Stats -> %s" %(self.Task, Url))
        RCS = RetrvCommitStats (CmmitFile, self.Task, self.UserName, self.Token)
        RCS.process (RepoId, Url)
        

