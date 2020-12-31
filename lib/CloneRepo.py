#!/usr/bin/python

from lib.System import System
import csv
import sys
import os
import requests
import pandas as pd
from time import sleep

class Diff ():
    def __init__(self, file, content):
        self.file = file
        self.content = content

class Commit ():
    def __init__(self, id, sha, author, date, message):
        self.id      = id
        self.sha     = sha
        self.author	 = author
        self.date	 = date
        self.message = message

        self.Diffs   = []

    def AddDiff (self, DF):
        self.Diffs.append (DF)
        

class CloneRepo():
    def __init__(self, RepoPath):
        self.RepoPath = RepoPath        
        self.RepoList = []
        self.UserName = "wangtong0908"
        self.Token    = "8ad9a6cddbd384072d2410d3f32dad4455c67d64"

        self.Commits  = []
        self.Exts = ['.h', '.c', '.cpp', '.cc', '.i', '.js', '.css', '.json', '.sh', '.jsx', '.xml', '.yml',
                     '.jade', '.scss', '.coffee', '.py', '.php', '.php3', '.ps1', '.zsh', '.bash', ".sh", '.pl', 
                     '.go', '.sh', '.java', '.asp', '.aspx', '.ashx', '.cs', '.html', 'cls', 'csc', '.cxx', 
                     '.hpp', '.jsp', '.pas', '.phtml', '.s', '.vbs']
        self.BaseDir = os.getcwd ()

    def GetCmmtDir (self, RepoId):
        RepoCmmtDir = self.BaseDir + "/Data/CmmtSet/" + str (RepoId) + "/"
        if not os.path.exists (RepoCmmtDir):
            os.mkdir (RepoCmmtDir)
        return RepoCmmtDir


    def WriteContent (self, CmmtDir, Cmmt):
        CntDir = CmmtDir + "Content/"
        if not os.path.exists (CntDir):
            os.mkdir (CntDir)
        
        FileName = CntDir + str (Cmmt.id) + ".csv"
        Header = ['file', 'content']
        with open(FileName, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for Dif in Cmmt.Diffs:
                row = [Dif.file, Dif.content]
                writer.writerow(row)
        CsvFile.close()

    def WriteCommts (self, RepoId):
        RepoCmmtDir = self.GetCmmtDir (RepoId)
        CmmtFile = RepoCmmtDir + str (RepoId) + ".csv"
        Header = ['id', 'sha', 'author', 'date', 'message']
        with open(CmmtFile, 'w', encoding='utf-8') as CsvFile:       
            writer = csv.writer(CsvFile)
            writer.writerow(Header)  
            for cmmt in self.Commits:
                row = [cmmt.id, cmmt.sha, cmmt.author, cmmt.date, cmmt.message]
                writer.writerow(row)

                if len (cmmt.Diffs) != 0:
                    self.WriteContent (RepoCmmtDir, cmmt)
        CsvFile.close()

    def is_continue (self, errcode):
        codes = [404, 500]
        if (errcode in codes):
            return False
        else:
            return True


    def IsInExt (self, Ext):
        lower = Ext.lower ()
        if lower in self.Exts:
            return True
        else:
            return False

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
        
        with open(LogFile, 'r', encoding='latin1') as Lfile:
            state = 0
            Cmmt = None
            Message = ""
            Index   = 0
            Df      = None
            DfContent = ""
            for line in Lfile:
                if line[0:7] == "commit ":
                    if Df != None:
                        Df.content = DfContent
                        Cmmt.AddDiff (Df)
                        #print (DfContent)
                        Df = None
                        DfContent = ""
                                
                    Id  = len(self.Commits)
                    Sha = line[8:-1]
                    Cmmt = Commit (Id, Sha, None, None, None)
                    self.Commits.append (Cmmt)
                    state = 0
                elif line[0:8] == "Author: ":
                    Cmmt.author = line[9:-1]
                elif line[0:6] == "Date: ":
                    Cmmt.date = line[7:-1]
                    state = 1
                    Message = ""
                else:
                    if len (line) < 6 :
                        if Message != "":
                           Cmmt.message = Message
                           state = 2
                           Message = ""
                           #print (Cmmt.sha, " -> ", Cmmt.message)
                        continue

                    # message
                    if state == 1:
                        Message += line

                    #diff
                    if state == 2:
                        if line[0:12] == "diff --git a":
                            if Df != None:
                                Df.content = DfContent
                                Cmmt.AddDiff (Df)
                                Df = None
                                DfContent = ""
                                #print (DfContent)
                            Path, Name = os.path.split(line[13:-1])
                            File, Ext  = os.path.splitext(Name)
                            self.Extersion [Ext] = True
                            if self.IsInExt (Ext):
                                Df = Diff (Name, "") 
                            
                            continue
                    #diff content
                    if Df != None:
                        DfContent += line
                 

    def CloneLog (self, RepoId, RepoDir):
        Repo = RepoDir + "/" + os.listdir(RepoDir)[0]     
        os.chdir(Repo)

        LogFile = str (RepoId) + ".log"
        LogCmd = "git log -20000 --date=iso -p > " + LogFile
        os.system (LogCmd)
        print (LogCmd)
        self.ParseLog (LogFile)
        self.WriteCommts (RepoId)
        os.remove (LogFile)
        self.Commits  = []
    
        
    def Clone (self):
        self.Extersion = {}
        self.GetRepoList ()
        BaseDir = self.BaseDir + "/Data/Repository/"
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

            if System.access_tag (str(repo['id'])):
                continue
            self.CloneLog (repo['id'], RepoDir)
            System.set_tag (str(repo['id']))


    
