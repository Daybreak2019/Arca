#!/usr/bin/python

import sys, getopt
from progressbar import ProgressBar
from lib.System import System
from lib.CollectRepo import CollectRepo
from lib.TaskDistributer import TaskDistributer

def CollectRepository(year=0):
    print(">>>>>>>>>>>> CollectRepo fom github...")
    # Retrieves repo data from Github by page
    CR = CollectRepo(System.OriginalRepo)
    CR.collect_repositories()

def CollectCommits(startNo=0, endNo=65535):
    print(">>>>>>>>>>>> CollectCommits...")
    TD = TaskDistributer (System.OriginalRepo, startNo, endNo)
    TD.distributer ()
    

def AnalyzeCommits():
    print(">>>>>>>>>>>> AnalyzeCommits...")


def main(argv):
    step = ''
    by_year = False
    startNo = 0
    endNo   = 0
   
    #########################################################
    # get step
    #########################################################
    try:
        opts, args = getopt.getopt(argv,"hs:b:e:",["step="])
    except getopt.GetoptError:
        print ("run.py -s <step_name>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ("arca.py -s all      ---  do all steps");
            print ("arca.py -s repo     ---  collect repositories from github");
            print ("arca.py -s commits  ---  collect commits for all repositories");
            print ("arca.py -s analysis ---  analyze the commit content");
            sys.exit()
        elif opt in ("-s", "--step"):
            step = arg;
        elif opt in ("-b", "--begin-no"):
            startNo = int(arg);
        elif opt in ("-e", "--end-no"):
            endNo = int(arg);

    #########################################################
    # collect and analysis
    #########################################################
    if (step == "all"):
        CollectRepository ()
        CollectCommits()
        AnalyzeCommits()
            
    elif (step == "repo"):
        CollectRepository ()
                
    elif (step == "commits"):
        CollectCommits(startNo, endNo)
        
    elif (step == "analysis"):
        AnalyzeCommits()
        
    else:
        print ("arca.py -s <all/repo/commits/analysis>")  
   

if __name__ == "__main__":
   main(sys.argv[1:])
