#!/usr/bin/python

from lib.System import System
from lib.Task import Task
import pandas as pd

class TaskDistributer():
    def __init__(self, RepoPath, startNo=0, endNo=65535):
        #"acielecki":"00f92e94cd9e2bd4d23f5307785b49b86eca18f3"
        self.Accounts = {}
        self.RepoPath = RepoPath        
        self.RepoList = []
        self.startNo  = startNo
        self.endNo    = endNo
        
    def read_repository_list(self):
        df = pd.read_csv(self.RepoPath)
        for index, row in df.iterrows():
            if index < self.startNo:
                continue
            
            repo = {}
            repo['id']  = row['id']
            repo['url'] = row['url']
            repo['created_at'] = row['created_at']
            self.RepoList.append (repo)
            
            if index >= self.endNo:
                break
        print ("Total %d Repositories" %len(self.RepoList))
        
    def distributer(self):
        self.read_repository_list ()
        AccNum  = len(self.Accounts)
        RepoNum = int (len(self.RepoList)/AccNum)
        print ("AccNum = %d, RepoNum = %d" %(AccNum, RepoNum))
        
        TaskNo = 0
        Tasks  = []
        RepoList = [self.RepoList[i:i + RepoNum] for i in range(0, len(self.RepoList), RepoNum)]    
        for Name, Token in self.Accounts.items():
            Account = {}
            Account["Name"]  = Name
            Account["Token"] = Token
            Repos = RepoList[TaskNo]
            SubTask = Task (TaskNo, Account, Repos)
            TaskNo += 1
            
            SubTask.start()
            Tasks.append(SubTask)
        
        for t in Tasks:
            t.join()
        print ("====> Exiting.")
            

    



    