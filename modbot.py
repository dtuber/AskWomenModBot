#!/usr/bin/python
import praw
import time
from pprint import pprint
import os

username = 'RachelTyrell'
PASSWORD = 'askwomenmodbot'
r = praw.Reddit(user_agent='TubesBot')
r.login(username,PASSWORD)
#already_done = []
keywords = ['bitch', 'slut', 'whore', 'cunt', 'nigger', 'dyke', 'faggot']

_hits = None
filename = 'ident_cache.txt'

def write_hits(filename):
    '''write ident hits back to a temporary file, then copy the file
    over where the old one was (we remove "filename", then we rename
    "filename.tmp" to "filename" to keep OS compatibility; Windows
    does not support atomic renames cause it's fucking stupid)'''
    f = open(filename + ".tmp", "w")
    for hit in _hits:
        f.write(hit + "\n")

    f.close()
    os.remove(filename)
    os.rename(filename + ".tmp", filename)

def check_hits(ident, filename=None):
    '''figure out if we've already replied to a certain
    ident before. supply filename if _hits is none, which
    it is initialized to (so the first call of this
    function needs to have the filename). return true
    if we replied to this ident before, according to our hit cache.'''
    global _hits
    if _hits is None:
        f = open(filename)
        _hits = f.readlines()
        f.close()
    for i in range(len(_hits)):
        _hits[i] = _hits[i].rstrip("\n\t ")
    if ident in _hits:
        return True
    return False

check_hits(None, filename)

def alert_comment_slurs(subreddit):
    #test to see if any recent comments have issues
    #TODO split comment into sentences, use regex to detect if a word is being used in context
    #/(is|was) a? dick/
    #sentence ~ /his.*dick/
    reddit_to_check = r.get_subreddit(subreddit)
    comments = reddit_to_check.get_comments()
    for x in comments:
        bool_test = any(string in x.body.lower() for string in keywords)
        exception = any('"'+string+'"' in x.body.lower() for string in keywords)
        if x.id not in _hits and bool_test and not exception:
           #print str(x.body) + " " + str(x.author)
            msg = 'This comment: ' + str(x.body) + ' contains inappropriate language, link here: ' + str(x.permalink) + ' This comment was made by: ' + str(x.author)
            print msg
            if not check_hits(x.id, filename):
                #r.send_message('/r/'+ subreddit, 'inappropriate comment detected', msg)
                x.report()
                _hits.append(x.id)

def post_is_question(subreddit):
    #checks to see if posts are questions
    question_words = ['who', 'what', 'when', 'where', 'why', 'have you ever', 'has anyone here ever', 'would this make me', '?']
    reddit_to_check = r.get_subreddit(subreddit)
    for submission in reddit_to_check.get_new(limit=10):
        title = submission.title.lower()
        has_question =  any(string in title for string in question_words)
        if submission.id not in _hits and not has_question:
            msg = 'This post: ' + str(submission.permalink) + ' was not a question, and was posted by: ' + str(submission.author)
            print msg
            if not check_hits(submission.id, filename):
                #r.send_message('/r/'+subreddit, 'improper post detected', msg)
                submission.report()
                _hits.append(submission.id)

def post_is_inappropriate(subreddit):
    #checks to see if posts are appropriate
    reddit_to_check = r.get_subreddit(subreddit)
    comments = reddit_to_check.get_new(limit=10)
    for x in comments:
        test = any(string in x.title.lower() + x.selftext.lower() for string in keywords)
        exception = any('"'+string+'"' in x.selftext.lower() + x.title.lower() for string in keywords)
        #title_exception = any('"'+string+'"' in x.title.lower() for string in keywords)
        if x.id not in _hits and test and not exception: #and not body_exception and not title_exception:
            msg = 'This post: ' + str(x.permalink) + ' contains inappropriate language.  This post was made by: ' + str(x.author)
            print msg
            if not check_hits(submission.id, filename):
                #r.send_message('/r/'+subreddit, 'inappropriate post detected', msg)
                x.report()
                _hits.append(x.id)


while True:
    print 'beginning check'
    alert_comment_slurs('askwomen')
    post_is_inappropriate('askwomen')
    post_is_question('askwomen')
    write_hits(filename)
    time.sleep(10)

