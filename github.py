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
#############
# Constants #
#############

BASEURL = "https://api.github.com/" #The basic URL to use the GitHub API
ORGS = ["alibaba","google","microsoft","huawei","apple","xiaomi","tencent","ibm","facebook","paypal","nasa","netease","sap","nodejs","twitter"]
PARAMETERS = "&per_page=100" #Additional parameters for the query (by default 100 items per page)
DELAY_BETWEEN_QUERYS = 10 #The time to wait between different queries to GitHub (to avoid be banned)
OUTPUT_CSV_FILE = "./repositories.csv" #Path to the CSV file generated as output
TARGET = 50000
countOfRepositories = 0
SEEDUSERS = ["1216114309zpf"]



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
    midURL = BASEURL + "orgs/" + org + "/repos?per_page=100"
    currentPage = 1
    while True:
        url = midURL + "&page=" + str(currentPage)
        currentPage = currentPage + 1
        dataRead = simplejson.loads(getUrl(url))
        if len(dataRead) < 20:
            break
        for repo in dataRead:
            if repo['size'] > 0 and (not repo['fork']):
                global countOfRepositories 
                countOfRepositories = countOfRepositories + 1
                repoURL = repo['html_url']
                repositories.writerow([org, repoURL])
                if achieveTarget():
                    return
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)
    print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
    time.sleep(DELAY_BETWEEN_QUERYS)

def getRepoFromORGS(orgs):
    for org in range(1, len(orgs)+1):
	print "Processing org " + ORGS[org - 1] + " "  + str(org) + " of " + str(len(ORGS)) + " ..."
        processORG(ORGS[org - 1])
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)
        if achieveTarget():
            break

def achieveTarget():
    return countOfRepositories >= TARGET

def getRepoFromUser(user):
    midURL = BASEURL + "users/" + user + "/repos?per_page=100"
    currentPage = 1
    while True:
        url = midURL + "&page=" + str(currentPage)
        currentPage = currentPage + 1
        dataRead = simplejson.loads(getUrl(url))
        if len(dataRead) < 4 :
            return 
        for repo in dataRead:
            if repo['size'] > 0 and (not repo['fork']):
                global countOfRepositories
                countOfRepositories = countOfRepositories + 1
                repoURL = repo['html_url']
                repositories.writerow([user, repoURL])
                if achieveTarget():
                    return
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)


def getFriendsFromUser(user):
    friends = []
    followerURL = BASEURL + "users/" + user + "/followers?per_page=100"
    followingURL = BASEURL + "users/" + user + "/following?per_page=100"
    dataRead = simplejson.loads(getUrl(followerURL))
    for data in dataRead:
        friends.append(data['login'])
    print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
    time.sleep(DELAY_BETWEEN_QUERYS)
    dataRead = simplejson.loads(getUrl(followingURL))
    for data in dataRead:
        friends.append(data['login'])
    time.sleep(DELAY_BETWEEN_QUERYS)
    return friends


def getRepoFromUsers():
    candidateQue = queue.Queue(2000)
    dict = {"alibaba":True}
    for user in SEEDUSERS:
        candidateQue.put(user)
        dict[user] = True
    for org in ORGS:
        dict[org] = True
    while candidateQue.qsize() > 0:
        currentUser = candidateQue.get()
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)
        getRepoFromUser(currentUser)
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)
        friends = getFriendsFromUser(currentUser)
        print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
        time.sleep(DELAY_BETWEEN_QUERYS)
        if achieveTarget():
            return
        for friend in friends:
            if (not dict.has_key(friend)) and (not candidateQue.full()):
                dict[friend] = True
                candidateQue.put(friend)

#getRepoFromORGS(ORGS)
getRepoFromUsers()

print "DONE! " + str(countOfRepositories) + " repositories have been processed."
csvfile.close()
