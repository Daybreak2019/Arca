#!/usr/bin/python

import requests
import os
import csv
import pandas as pd
import json
import base64

class TaskDistributer():
    def __init__(self, Accounts=None):    
        self.accounts  = Accounts     
        self.repo_list = []
        
    def ReadRepoList(self):
        RepoPath = System.OriginalRepo
        df = pd.read_csv('Repository_List.csv')
        for index, row in df.iterrows():
            repo = {}
            repo['id']  = row['id']
            repo['url'] = row['url']
            self.repo_list.append (repo)
        printf ("Total %d Repositories" %len(self.repo_list))

    



    