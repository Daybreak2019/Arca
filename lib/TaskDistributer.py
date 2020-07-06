#!/usr/bin/python

from lib.System import System
from lib.Task import Task
import pandas as pd



class TaskDistributer():
    def __init__(self, RepoPath):    
        self.Accounts = {"acielecki":"369e1093422f763f2745348139a4762218f62848",
                         "Daybreak2019":"765680b2e1ea165620822e86ea139f92384ee1ae",
                         "Eagle-2020":"c6af2d6f59d5d2a7f28e18df63a902b4990b817e"}
        self.RepoPath = RepoPath        
        self.RepoList = []
        
    def ReadRepoList(self):
        df = pd.read_csv(self.RepoPath)
        for index, row in df.iterrows():
            repo = {}
            repo['id']  = row['id']
            repo['url'] = row['url']
            self.RepoList.append (repo)
        print ("Total %d Repositories" %len(self.RepoList))
        
    def Distributer(self):
        self.ReadRepoList ()
        AccNum  = len(self.Accounts)
        RepoNum = len(self.RepoList)/AccNum
        
        TaskNo = 0
        Tasks  = []
        RepoList = [self.RepoList[i:i + AccNum] for i in range(0, len(self.RepoList), AccNum)]
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
            

    



    