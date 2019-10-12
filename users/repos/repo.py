# This script allows to crawl information and repositories from GitHub using the GitHub REST API (https://developer.github.com/v3/search/).
#
# Given a query, the script downloads for each repository returned by the query its ZIP file.
# In addition, it also generates a CSV file containing the list of repositories queried.
# For each query, GitHub returns a json file which is processed by this script to get information about repositories.
#
# The GitHub API limits the queries to get 100 elements per page and up to 1,000 elements in total.
# To get more than 1,000 elements, the main query should be splitted in multiple subqueries using different time windows through the constant SUBQUERIES (it is a list of subqueries).
#
# As example, constant values are set to get the repositories on GitHub of the user 'rsain'.


#############
# Libraries #
#############

import wget
import time
import simplejson
import csv
import pycurl
import math
from StringIO import StringIO
import Queue as queue
import sys
#############
# Constants #
#############

BASEURL = "https://api.github.com/" #The basic URL to use the GitHub API
ORGS = ["alibaba","google","microsoft","huawei","apple","xiaomi","tencent","ibm","facebook","paypal","nasa","netease","sap","nodejs","twitter"]
PARAMETERS = "&per_page=100" #Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERYS = 5 #The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_CSV_FILE = "./repos.csv" #Path to the CSV file generated as output
USER_FILE = "./users.csv"
TARGET = 50000
countOfRepos = 0



#############
# Functions #
#############

def getUrl (url) :
	''' Given a URL it returns its body '''
	buffer = StringIO()
	c = pycurl.Curl()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEDATA, buffer)
	c.perform()
	c.close()
	body = buffer.getvalue()

	return body


#Output CSV file which will contain information about repositories
csvfile = open(OUTPUT_CSV_FILE, 'wb')
repos_writer = csv.writer(csvfile, delimiter=',')


def achieveTarget():
    return countOfRepos >= TARGET


def getReposFromUser(user):
    repos = []
    reposURL = BASEURL + "users/" + user + "/repos?per_page=100"
    sleeping()
    print "Getting repos of User " + user
    dataRead = simplejson.loads(getUrl(reposURL))
    for repo in dataRead:
        if repo['size'] > 0 and (not repo['fork']):
            repos.append(repo['html_url'])
    return repos

def sleeping():
    print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
    time.sleep(DELAY_BETWEEN_QUERYS)

def getRepos():
    usersQue = queue.Queue(8000)
    with open(USER_FILE, "r") as f:
        reader = csv.reader(f)
        try:
            for row in reader:
                usersQue.put(row[0])
        except csv.Error as e:
            sys.exit('file {}, line {}: {}'.format(OLD_QUEUE, reader.line_num, e))
    while usersQue.qsize() > 0:
        currentUser = usersQue.get()
        print "Processing user " + str(currentUser)
        try:
            repos = getReposFromUser(currentUser)
        except TypeError:
            csvfile.close()
            sys.exit(0)
        if achieveTarget():
            return
        for repo in repos:
            global countOfRepos
            countOfRepos = countOfRepos + 1
            print "Add repo " + repo
            print "Repos count is " + str(countOfRepos) + " now"
            repos_writer.writerow([repo])

getRepos()

print "DONE! " + str(countOfRepos) + " users have been processed."
csvfile.close()
