
import os

BaseDir = os.getcwd() + "/Data"



class System():
    PAGE_COUNT   = 10
    PER_PAGE     = 100

    
    CmmtSet      = BaseDir + "/CmmtSet"
    if not os.path.exists (CmmtSet):
        os.mkdir (CmmtSet)
    
    TagSet       = BaseDir + "/TagSet"
    if not os.path.exists (TagSet):
        os.mkdir (TagSet)
        
    OriginalRepo = BaseDir + "/Repository_List.csv"
    
    START_YEAR   = 0
    STAS_START_YEAR   = 2011
    
    STATS_LIMITTED = 20*1024

    @staticmethod
    def mkdir(path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
    @staticmethod        
    def setdir(dir):
        isExists=os.path.exists(dir)
        if not isExists:
            os.makedirs(dir)
        return dir
        
    @staticmethod
    def setdir_cmmt(dir):
        NewDir = System.CmmtSet + "/" + dir
        return System.setdir (NewDir)
        
    @staticmethod
    def setdir_cmmt_content(dir):
        NewDir = System.CmmtSet + "/" + dir + "/Content"
        return System.setdir (NewDir)
    
    @staticmethod
    def setdir_cmmt_stats(dir):
        NewDir = System.CmmtSet + "/" + dir + "/Stats"
        return System.setdir (NewDir)

    @staticmethod
    def is_exist(file):
        isExists = os.path.exists(file)
        if (not isExists):
            return False
        
        fsize = os.path.getsize(file)/1024
        if (fsize == 0):
            return False
        return True      
        
    @staticmethod
    def set_tag(tag):
        NewDir = System.TagSet
        System.setdir (NewDir)
        file = open(NewDir + "/" + tag,'w')
        file.close()
        
    @staticmethod
    def access_tag(tag):
        tagPath = System.TagSet + "/" + tag
        isExists = os.path.exists(tagPath)
        if not isExists:
            return False
        return True

