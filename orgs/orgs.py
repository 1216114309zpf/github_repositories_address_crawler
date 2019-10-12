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


#############
# Constants #
#############

BASEURL = "https://api.github.com/orgs/" #The basic URL to use the GitHub API
ORGS = ["alibaba","google","microsoft","huawei","apple","xiaomi","tencent","ibm","facebook","paypal","nasa","netease","sap","nodejs","twitter"]
PARAMETERS = "&per_page=100" #Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERYS = 10 #The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_CSV_FILE = "./repositories.csv" #Path to the CSV file generated as output
TARGET = 50000
countOfRepositories = 0



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
repositories = csv.writer(csvfile, delimiter=',')

def processORG(org):
    midURL = BASEURL + org + "/repos?per_page=100"
    currentPage = 1
    while True:
        url = midURL + "&page=" + str(currentPage)
        currentPage = currentPage + 1
        dataRead = simplejson.loads(getUrl(url))
        if len(dataRead) < 20:
            return
        for repo in dataRead:
            if repo['size'] > 0 and (not repo['fork']):
                global countOfRepositories 
                countOfRepositories = countOfRepositories + 1
                repoURL = repo['html_url']
                repositories.writerow([org, repoURL])
                if countOfRepositories >= TARGET:
                    return
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)

def getRepoFromORGS(orgs):
    for org in range(1, len(orgs)+1):
	print "Processing org " + ORGS[org - 1] + " "  + str(org) + " of " + str(len(ORGS)) + " ..."
        processORG(ORGS[org - 1])
        global countOfRepositories
        if countOfRepositories > TARGET:
            break

getRepoFromORGS(ORGS)
           

print "DONE! " + str(countOfRepositories) + " repositories have been processed."
csvfile.close()
