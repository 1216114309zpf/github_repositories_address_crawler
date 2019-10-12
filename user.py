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
OUTPUT_CSV_FILE = "./users.csv" #Path to the CSV file generated as output
QUEUE_USER_FILE = "./queue_user.csv"
TARGET = 5000
countOfUsers = 0
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
csvfile = open(OUTPUT_CSV_FILE, 'a')
users = csv.writer(csvfile, delimiter=',')
csvqueuefile = open(QUEUE_USER_FILE, 'wb')
queue_users = csv.writer(csvqueuefile, delimiter=',')


def achieveTarget():
    return countOfUsers >= TARGET


def getFriendsFromUser(user):
    friends = []
    followerURL = BASEURL + "users/" + user + "/followers?per_page=100"
    followingURL = BASEURL + "users/" + user + "/following?per_page=100"
    sleeping()
    #print "Getting followers of User " + user
    #dataRead = simplejson.loads(getUrl(followerURL))
    #for data in dataRead:
     #   friends.append(data['login'])
    #sleeping()
    print "Getting following of User " + user
    dataRead = simplejson.loads(getUrl(followingURL))
    for data in dataRead:
        friends.append(data['login'])
    return friends

def sleeping():
    print "Sleeping " + str(DELAY_BETWEEN_QUERYS) + " seconds before the new query ..."
    time.sleep(DELAY_BETWEEN_QUERYS)

def getUsers():
    candidateQue = queue.Queue(5000)
    dict = {"alibaba":True}
    for user in SEEDUSERS:
        candidateQue.put(user)
        dict[user] = True
    for org in ORGS:
        dict[org] = True
    with open('./users.csv') as fp:
        line = fp.readline()
        while line:
            dict[line] = True
            line = fp.readline()
    with open('./queue_user.csv') as fp:
        line = fp.readline()
        while line:
            dic[line] = True
            candidateQue.put(line)
            line = fp.readline()
    while candidateQue.qsize() > 0:
        currentUser = candidateQue.get()
        print "Processing user " + str(currentUser)
        try:
            friends = getFriendsFromUser(currentUser)
        except TypeError:
            while candidateQue.qsize() > 0:
                queue_users.writerow([candidateQue.get()])
            return
        if achieveTarget():
            return
        for friend in friends:
            if (not dict.has_key(friend)) and (not candidateQue.full()):
                global countOfUsers
                countOfUsers = countOfUsers + 1
                print "Add User " + friend
                dict[friend] = True
                candidateQue.put(friend)
                users.writerow([friend])


getUsers()

print "DONE! " + str(countOfUsers) + " users have been processed."
csvfile.close()
