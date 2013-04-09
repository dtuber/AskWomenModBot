#!/usr/bin/python
import praw
import time
from pprint import pprint
import os

# importing local modules
import parser

username = 'RachelTyrell'
PASSWORD = 'askwomenmodbot'
r = praw.Reddit(user_agent='TubesBot')
r.login(username,PASSWORD)
#already_done = []
keywords = ['bitch', 'slut', 'whore', 'cunt', 'nigger', 'dyke', 'faggot', 'dick']

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
    global _hits
    #test to see if any recent comments have issues
    #TODO split comment into sentences, use regex to detect if a word is being used in context
    #/(is|was) a? dick/
    #sentence ~ /his.*dick/
    reddit_to_check = r.get_subreddit(subreddit)
    comments = reddit_to_check.get_comments()
    for x in comments:
	# already seen this comment? skip it then
	if check_hits(x.id): continue
	resultant = parser.slur_detect(str(x.body))
	if resultant is not None:
	    msg = 'This comment: ' + str(x.permalink) + \
	        ' with body: ' + str(x.body) + \
	        "\nmade by:" + str(x.author) + \
	        'contains inappropriate language, keywords: ' + str(resultant)
	    print msg
	    x.report()
	    _hits.append(x.id)
        #exception = any('"'+string+'"' in x.body.lower() for string in keywords)

def post_is_question(subreddit):
    #checks to see if posts are questions
    question_words = ['who', 'what', 'when', 'where', 'why', 'have you ever', 'has anyone here ever', 'would this make me']
    reddit_to_check = r.get_subreddit(subreddit)
    for submission in reddit_to_check.get_new(limit=10):
        title = submission.title.lower()
        has_question =  any(string in title for string in question_words)
        if not check_hits(submission.id) and not has_question and not '?' in submission.title:
            msg = 'This post: ' + str(submission.permalink) + ' was not a question, and was posted by: ' + str(submission.author)
            print msg
            if not check_hits(submission.id):
                #r.send_message('/r/'+subreddit, 'improper post detected', msg)
                submission.report()
                _hits.append(submission.id)
        elif not check_hits(submission.id) and not '?' in submission.title and 'http://www.reddit.com' in submission.selftext.lower():
            msg = 'This post : ' + str(submission.permalink) + ' contained a link in the body, and was posted by: ' + str(submission.author)
            print msg
            if not check_hits(submission.id):
                submission.report()
                _hits.append(submission.id)

def post_is_inappropriate(subreddit):
    #checks to see if posts are appropriate
    reddit_to_check = r.get_subreddit(subreddit)
    comments = reddit_to_check.get_new(limit=10)
    for x in comments:
        test = any(string in x.title.lower() + x.selftext.lower() for string in keywords)
        #exception = any('"'+string+'"' in x.selftext.lower() + x.title.lower() for string in keywords)
        #title_exception = any('"'+string+'"' in x.title.lower() for string in keywords)
        if not check_hits(x.id) and test: #and not body_exception and not title_exception:
            msg = 'This post: ' + str(x.permalink) + ' contains inappropriate language.  This post was made by: ' + str(x.author)
            print msg
            if not check_hits(x.id):
                #r.send_message('/r/'+subreddit, 'inappropriate post detected', msg)
                x.report()
                _hits.append(x.id)

def PUA_posts(subreddit):
    # same basic idea, but we're checking for anything related to PUA, and sending modmail because it could get ugly
    reddit_to_check = r.get_subreddit(subreddit)
    for x in reddit_to_check.get_new(limit=10):
        title = x.title.lower()
        body = x.selftext.lower()
        PUA_keywords = ['PUA', 'seddit', 'r/seduction', 'pick up artists']
        has_PUA = any(string in body for string in PUA_keywords) or any(string in title for string in PUA_keywords)
        if not check_hits(x.id) and has_PUA:
            msg = 'Hey, this is your friendly neighborhood mod bot.  Just wanted to you to know that a thread containing content related to PUA has popped up, and might need some non-bot intervention.  The link is here: ' + str(x.permalink) + '\n\n Have a nice day!'
            r.send_message('RampagingKoala', 'PUA thread detected', msg)
            _hits.append(x.id)

counter = 0;
while True:
    print 'beginning check ' + str(counter) + ' at: ' + str(time.ctime())
    alert_comment_slurs('askwomen')
    post_is_inappropriate('askwomen')
    post_is_question('askwomen')
    PUA_posts('askwomen')
    write_hits(filename)
    print 'check ' + str(counter) + ' completed!'
    time.sleep(1800)
    counter = counter + 1
    '''if counter % 24 == 0:
        #sends a daily mod bot update containing all the links it found
        msg = 'Hi, this is your friendly neighborhood mod bot.  This is an update on what I found.\n\n'
        for x in _hits:
            #TODO is there a way to post the offensive text, and to determine whether or not the marked ID is a post or comment?
            msg += str(x) + '\n\n'
        msg +='That is all I have found for today.  I shall check in tomorrow.  Regards, RachelTyrell'
        r.send_message('RampagingKoala', 'daily mod bot update', msg)
        # since we've already written all the hits to the log, we can safely remove them from the hits list, and reset it to save memory
        _hits = []
    #TODO modify loop to check more often during peak hours, and increment the counter by decimals during that time
    # for example, during peak hours, check once every 30 minutes, and increment by .5
	print 'check ' + str(counter) + ' completed!'
	time.sleep(3600)
    counter = counter + 1'''

# vim: set expandtab:ts=4
