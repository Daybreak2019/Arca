
import os


class System():
    PAGE_COUNT   = 10
    PER_PAGE     = 100

    BaseDir      = "./Data"
    OriginalRepo = BaseDir + "/RepositoryList.csv"

    @staticmethod
    def mkdir(path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
        
    @staticmethod
    def setdir(dir):
        NewDir = System.BaseDir + "/" + dir
        isExists=os.path.exists(NewDir)
        if not isExists:
            os.makedirs(NewDir)

