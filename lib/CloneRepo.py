#!/usr/bin/python

from lib.System import System
import csv
import sys
import os
import requests
import pandas as pd
from time import sleep

class CloneRepo():
    def __init__(self, RepoPath):
        self.RepoPath = RepoPath        
        self.RepoList = []
        self.UserName = "wangtong0908"
        self.Token    = "8ad9a6cddbd384072d2410d3f32dad4455c67d64"

    def is_continue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True

    def HttpCall (self, url):
        result = requests.get(url,
                              auth=(self.UserName, self.Token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (self.is_continue (result.status_code) == False):
            print("$$$%s: %s, URL: %s" % (result.status_code, result.reason, url))
            return None
        
        if (result.status_code != 200 and result.status_code != 422):
            print("%s: %s, URL: %s" % (result.status_code, result.reason, url))
            sleep(1200)
            return self.HttpCall(url)     
        return result.json()

    def GetClonePath (self, CloneRepoPath):
        RepoPath = "Data/" + self.RepoPath
        df = pd.read_csv(RepoPath)
        for index, row in df.iterrows():            
            repo = {}
            repo['id']  = row['id']
            
            ApiUrl = row['url']
            print ("[%d] Retrieve %s -> %s" %(index, row['id'], row['url']))
            Data = self.HttpCall (ApiUrl)
            if Data == None:
                continue
            repo['clone_url'] = Data['clone_url']
            self.RepoList.append (repo)

    def GetRepoList(self):
        CloneRepoPath = "Data/Clone" + self.RepoPath
        if not os.path.exists (CloneRepoPath):
            self.GetClonePath (CloneRepoPath)
            self.WriteCsv (self.RepoList, CloneRepoPath)
        else:           
            df = pd.read_csv(CloneRepoPath)
            for index, row in df.iterrows():            
                repo = {}
                repo['id']  = row['id']
                repo['clone_url'] = row['clone_url']
                self.RepoList.append (repo)           
        print ("Total %d Repositories" %len(self.RepoList))
        
    
    def WriteCsv (self, Data, FileName):
        with open(FileName, 'w', encoding='utf-8') as csv_file:       
            writer = csv.writer(csv_file)
            header = list(Data[0].keys()) 
            writer.writerow(header)            
            for item in Data:
                if item != None:
                    row = list(item.values())
                    writer.writerow(row)
        csv_file.close()


    def ParseLog (self, LogFile):
        pass

    def CloneLog (self, RepoId, RepoDir):
        Repo = RepoDir + "/" + os.listdir(RepoDir)[0]     
        os.chdir(Repo)

        LogFile = "../" + str (RepoId) + ".log"
        LogCmd = "git log -5 --date=iso -p > " + LogFile
        os.system (LogCmd)
        print (LogCmd)
        self.ParseLog (LogFile)

        
    def Clone (self):
        self.GetRepoList ()
        BaseDir = os.getcwd() + "/Data/Repository/"
        if not os.path.exists (BaseDir):
            os.mkdir (BaseDir)
        print (BaseDir)
        Id = 0
        for repo in self.RepoList:
            #print (repo['id'], " ---> ", repo['clone_url'])
            RepoDir = BaseDir + str(repo['id'])
            if not os.path.exists (RepoDir):
                os.mkdir (RepoDir)
            os.chdir(RepoDir)

            CloneCmd = "git clone " + repo['clone_url']
            print ("[", Id, "] --> ", CloneCmd)
            os.system (CloneCmd)
            Id += 1

            self.CloneLog (repo['id'], RepoDir)
            break

    
