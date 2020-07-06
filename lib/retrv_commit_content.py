import requests
import os
import csv
import pandas as pd
import json
import base64

class RetrvCommitContent():
    def __init__(self, repo_id):    
        self.repo_id  = repo_id 
        
        self.username = "***********"
        self.token = "****************************"
        
        self.commit_content = []
        
    def http_get_call(self, url):
        result = requests.get(url,
                              auth=(self.username, self.token),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        
        return result.json()
    
    def write_csv(self):
        file = str(self.repo_id) + '_content' +'.csv'

        with open(file, 'w', encoding='utf-8', newline="") as csv_file:
        
            writer = csv.writer(csv_file)

            header = list(self.commit_content[0].keys()) 
            writer.writerow(header)
            
            for commit in self.commit_content:
                if commit != None:
                    row = list(commit.values())
                    writer.writerow(row)
        csv_file.close()
        
    def parse_commits(self, commit_url):
        print("Retrieving commit content for %s"  %(commit_url))
        result = self.http_get_call(commit_url)

        allitems = result['tree']
        
        for item in allitems:
            if item['type'] == 'tree':
                self.parse_commits(item['url'])
            else:                             
                result2 = self.http_get_call(item['url'])
                content = result2['content']
                content = base64.b64decode(content)

                record = {}
                record['path'] = item['path']
                record['type'] = item['type']
                record['content'] = content
                
                self.commit_content.append(record)
            
    def collect_commit_content(self):
        commitsfile = self.repo_id + ".csv"
        cdf = pd.read_csv(commitsfile)
        urls = cdf['commits']
        for url in urls:
            content = self.parse_commits(url)
        self.write_csv()

#Test for a single file            
#RCC = RetrvCommitContent('18047027')
#RCC.collect_commit_content()

#Automate for each repository
df = pd.read_csv('Repository_List.csv')
ids = df['id']

for repo_id in ids:
    RCC = RetrvCommitContent(str(repo_id))
    RCC.collect_commit_content()
