#!/usr/bin/python

from lib.System import System
from progressbar import ProgressBar
import threading

class Task(threading.Thread):
    def __init__(self, TaskNo, Account, RepoList):
        threading.Thread.__init__(self)
        self.Account  = Account
        self.RepoList = RepoList
        self.TaskNo   = TaskNo
        print ("Create Task %d" %TaskNo)
        
    def run(self):
        print ("[%d]Account: %s - %s" %(self.TaskNo, self.Account["Name"], self.Account["Token"]))
        
        



    