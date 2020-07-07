#!/usr/bin/python

from lib.System import System
from progressbar import ProgressBar
import abc
import requests
import csv
from time import sleep

class CommitCollector(metaclass=abc.ABCMeta):
    def __init__(self, Task, UserName, Token, RepoList=None):
        self.Task     = Task
        self.UserName = UserName
        self.Token    = Token
        self.RepoList = RepoList
        self.Output   = []
    
    def http_get_call (self, url):
        result = requests.get(url,
                              auth=(self.UserName, self.Token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (result.status_code != 200 and result.status_code != 422):
            print("[Task%d]%s: %s, URL: %s" % (self.Task, result.status_code, result.reason, url))
            sleep(300)
            return self.http_get_call(url)     
        return result.json()
    
    def write_csv (self, FileName):
        with open(FileName, 'w', encoding='utf-8') as csv_file:
        
            writer = csv.writer(csv_file)

            header = list(self.Output[0].keys()) 
            writer.writerow(header)
            
            for item in self.Output:
                if item != None:
                    row = list(item.values())
                    writer.writerow(row)
        csv_file.close()
        
    def is_processed (self, id):
        return System.access_tag (str(id))
    
    @abc.abstractmethod
    def process(self, id, url=None):
        print("Abstract Method that is implemented by inheriting classes")
        
    def collect_data (self):
        No = 0;
        TotalNum = len (self.RepoList)
        for repo in self.RepoList:
            id = str(repo['id'])
            if (self.is_processed (id)):
                continue
            print ("[Task%d-%d/%d]repo -> %s : %s" %(self.Task, No, TotalNum, repo['id'], repo['url']))
            self.process(id, repo['url'])

            System.set_tag (id)
            No += 1


    