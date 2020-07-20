
from lib.System import System
from datetime import datetime, timedelta
from time import sleep
import requests
from progressbar import ProgressBar
# Reads/Writes in a CSV formatted file
import csv  
import sys   
import os
import re
# Allows code to read in large CSV files
csv.field_size_limit(sys.maxsize)
PAGE_COUNT  = System.PAGE_COUNT
PER_PAGE    = System.PER_PAGE

UPDATE_ACTIVE = "active"
UPDATE_MAX    = "max"
UPDATE_MIN    = "min"

class CollectRepo():

    Fields = ['id', 'size', 'created_at', 'forks',
              'open_issues', 'subscribers_count',
              'stargazers_count', 'language_dictionary',
              'owner_type', 'url',
              'pushed_at', 'topics', 'description']

    def __init__(self, RepoPath):
        self.list_of_repositories = []
        self.file_name = RepoPath
        self.updated_time = {}
        self.cur_year = 0
        self.date_created = ""
        self.username = ""
        self.password = ""
        self.stars = []

    def collect_repositories(self):
        self.stars = ["11501..*",   "7501..9500", "6501..7500", "5501..6500",  
                      "4501..5500", "4001..4500", "3801..4000", "3601..3800", 
                      "3401..3600", "3201..3400", "3001..3200", "2800..3000", 
                      "2601..2800", "2401..2600", "2201..2400", "2001..2200",
                      "1901..2000", "1801..1900", "1701..1800", "1601..1700",
                      "1501..1600", "1401..1500", "1301..1400", "1201..1300", 
                      "1151..1200", "1101..1150", "1051..1100", "1001..1050",
                      "951..1000",  "901..950",   "851..900",   "826..850",
                      "801..825",   "776..800",   "751..775",   "726..750",   
                      "701..725",   "676..700",   "651..675",   "626..650",
                      "601..625",   "576..600",   "551..575",   "526..550",
                      "501..525"]

        # Obtains initial 'unclean' repositories
        self.get_active_repos()
        
        # Initial amount of 'unclean' repositories obtained
        original_repo_count = len(self.list_of_repositories)
        print("%d Repositories have been read in from Github" % original_repo_count)
        # Updates some of the values and adds new ones for each repository
        self.update_repositories()
        
        # Updates all of the language of each repository to include all languages used and not just the top one
        list_of_languages = self.update_languages()
        # Changes some of the repository values that need to be further cleaned
        self.clean_repositories(list_of_languages)
        # Removes all the repositories that do not meet the minimum requirements to be deemed 'clean'
        self.remove_invalid_repositories()

        # Obtains and displays the final amount of repositories compared to the starting amount
        final_repo_count = len(self.list_of_repositories)
        print("Valid Repositories Remaining %d of %d [%.2f%%]" % (final_repo_count, original_repo_count,
                                                                  (final_repo_count / original_repo_count) * 100))

        self.write_csv()

    def update_repositories(self, field='url', repo_num=65535):
        print("Updating Repository Data[%s]..." %field)
        pbar = ProgressBar()
        index = 0
        for repo in pbar(self.list_of_repositories):
            url = repo[field]
            #print ("---> update_repositories: Url=" + url)
            result = self.http_get_call(url)
            self.list_of_repositories[index] = dict(result)
            index += 1
            if (index >= repo_num):
                break

    def update_languages(self):
        print("Updating Repository Language Data...")
        language_dict = {}
        pbar = ProgressBar()
        for repo in pbar(self.list_of_repositories):
            #print ("repo = " + str(repo))
            url = repo['languages_url']
            repo['language'] = self.http_get_call(url)
            #print ("---> update_languages: Url=" + url + "Language=" + str(repo['language']))
            language_dict.update(repo['language'])
        return [lang.lower() for lang in language_dict.keys()] 

    def get_date_updated(self, year=0, months=6):
        #print("Date Last Updated Time-Span (months): ", end="")
        #months = int(input())
        print("Date Update Time-Span (months): %d"  %months)
        days = months * 30

        date = datetime.strptime("2019-12-31", "%Y-%m-%d") - timedelta(days=days)
        self.updated_time[UPDATE_MAX] = "+pushed:<=" + date.strftime("%Y-%m-%d")
        self.updated_time[UPDATE_ACTIVE] = "+pushed:>=" + date.strftime("%Y-%m-%d")

        date = date - timedelta(days=12*30)
        self.updated_time[UPDATE_MIN] = "+pushed:>=" + date.strftime("%Y-%m-%d")
        self.cur_year = year

    def remove_invalid_repositories(self):
        updated_repos = []
        for repo in self.list_of_repositories:
            language_count = len(repo['language_dictionary'])
            character_count = len(str(repo['description']))
            if language_count > 1 and character_count > 20:
                updated_repos.append(repo)
        self.list_of_repositories = updated_repos
        
    def dictsort_key(self, original_dict, reverse=False):
        new_dict = {}
        for key in sorted(original_dict):
            new_dict[key] = original_dict[key]
        return new_dict
        
    def clean_text(self, text):
        # Change all the text to lower case
        text = text.lower()
        # Converts all '+' and '/' to the word 'and'
        text = re.sub(r'[+|/]', ' and ', text)
        # Removes all characters besides numbers, letters, and commas
        text = re.sub(r'[^\w\d,]', ' ', text)
        # Word Tokenization
        words = text.split()
        # Remove Non-alpha text
        words = [re.sub(r'[^a-z]', '', word) for word in words if word.isalnum()]
        # Joins tokenized string into one string
        text = ' '.join(words)
        return text

    def clean_repositories(self, langs):
        index = 0
        for repo in self.list_of_repositories:
            topics = [topic.lower() for topic in repo['topics']]
            # Removes all topics that are just programming language names
            repo['topics'] = [topic for topic in topics if topic not in langs]
            # Makes all languages lowercase
            language_dictionary = {language.lower(): val for language, val in repo['language'].items()}
            repo['language_dictionary'] = self.dictsort_key(language_dictionary)
            # Makes all descriptions proper strings
            description = str(repo['description'])
            repo['description'] = self.clean_text (description)
            # Sets 'owner' field to owner's 'type'
            repo['owner_type'] = repo['owner']['type']
            self.list_of_repositories[index] = {field: repo[field] for field in CollectRepo.Fields}
            index += 1

    def http_get_call(self, url):
        result = requests.get(url,
                              auth=(self.username, self.password),
                              headers={"Accept": "application/vnd.github.mercy-preview+json"})
        if (result.status_code != 200 and result.status_code != 422):
            print("Status Code %s: %s, URL: %s" % (result.status_code, result.reason, url))
            # Sleeps program for one hour and then makes call again when api is unrestricted
            sleep(300)
            return self.http_get_call(url)
        return result.json()

    def get_page_of_repos(self, updated_key, page_num, star_count):
        url = 'https://api.github.com/search/repositories?' \
              + 'q=stars:' + star_count + '+is:public+mirror:false' \
              + self.updated_time[updated_key] 

        if (updated_key == UPDATE_ACTIVE):
            url += self.date_created
        
        url += '&sort=stars&per_page=' + str(PER_PAGE) + '&order=desc' + '&page=' + str(page_num)  # 4250
        
        if page_num == 1:
            print(url)
        return self.http_get_call(url)

    def get_page_of_release(self, url, page_num):
        release_url = url + '/releases?' + 'per_page=100' + '&page=' + str(page_num)  # 4250
        if page_num == 1:
            print(release_url)
        return self.http_get_call(release_url)

    def get_repos(self, updated_key):
        print("---> [%s]Obtaining Repositories from Github, PAGE_COUNT[%d]..." %(updated_key, PAGE_COUNT))
        page_count = PAGE_COUNT+1        
        list_of_repositories = []
        for star_count in self.stars:
            # Reads in 100 repositories from 10 pages resulting in 1000 repositories
            for page_num in range(1, page_count, 1):
                # Gets repos from github in json format
                json_repos = self.get_page_of_repos(updated_key, page_num, star_count)
                # json_repos['items'] = list of repo dictionary objects OR is not a valid key
                if 'items' in json_repos:
                    # Append new repos to the end of 'list_of_repositories'
                    repos = json_repos['items']
                    list_of_repositories += repos
                    if (len(repos) < PER_PAGE):
                        break
                else:
                    break
            print ("star: %s  --->  retrive repositories: %d" %(star_count, len(list_of_repositories)));
        return list_of_repositories
        
    def get_date_updated(self, year=0, months=6):
        print("Date Update Time-Span (months): %d"  %months)
        days = months * 30

        date = datetime.strptime("2019-12-31", "%Y-%m-%d") - timedelta(days=days)
        self.updated_time[UPDATE_MAX] = "+pushed:<=" + date.strftime("%Y-%m-%d")
        self.updated_time[UPDATE_ACTIVE] = "+pushed:>=" + date.strftime("%Y-%m-%d")

        date = date - timedelta(days=12*30)
        self.updated_time[UPDATE_MIN] = "+pushed:>=" + date.strftime("%Y-%m-%d")
        self.cur_year = year

    def get_date_created(self):
        years = 2
        print("Date Created Time-Span (years): %d"  %years)
        days = years * 365.24
        date = datetime.today() - timedelta(days=days)
        self.date_created = "+created:<=" + date.strftime("%Y-%m-%d")

    def get_active_repos(self):
        self.get_date_created()
        self.get_date_updated()
        self.list_of_repositories = self.get_repos(UPDATE_ACTIVE)
                

    def write_csv(self):
        file = self.file_name
        print("---> Writing to" + file)       
        with open(file, 'w') as csv_file:
            writer = csv.writer(csv_file)
            # Writes the dictionary keys to the csv file
            writer.writerow(CollectRepo.Fields)
            # Writes all the values of each index of dict_repos as separate rows in the csv file
            for repository in self.list_of_repositories:
                row = []
                for field in CollectRepo.Fields:
                    row.append(repository[field])
                writer.writerow(row)
        csv_file.close()

