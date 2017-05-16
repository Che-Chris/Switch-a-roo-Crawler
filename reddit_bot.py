#!/usr/bin/env python
import praw
import pdb
import re
import os

from bs4 import BeautifulSoup

reddit = praw.Reddit('bot1')
# subreddit = reddit.subreddit('learnpython')
pattern = 'a-roo|aroo|eroo|e-roo'

def getNextLink(comment):
    soup = BeautifulSoup(comment.body_html, 'html.parser')
    for link in soup.find_all('a'):
        if 'https://www.reddit.com' in link.get('href'):
            return link.get('href')
    return None

def hasLink(comment):
    soup = BeautifulSoup(comment.body_html, 'html.parse')
    return len(soup.find_all('a')) > 0

if not os.path.isfile('posts_replied_to.txt'):
    posts_replied_to = []
else:
    with open('posts_replied_to.txt', 'r') as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split('\n')
        posts_replied_to = list(filter(None, posts_replied_to))

comment_ids = []
chain_length = 0

start_link = input("Enter a link to start.\n")
start_submission = reddit.submission(url=start_link)
start_submission.comments.replace_more(limit=None)
for comment in start_submission.comments.list():
    if comment.id not in comment_ids:
        comment_ids.append(comment.id)
    if re.search(pattern, comment.body, re.IGNORECASE) and hasLink(comment):
        print('IN REGEX MATCHING 1')
        next_link = getNextLink(comment)
        final_comment = comment.body
        final_url = comment.permalink()
        chain_length += 1
        break
    else:
        next_link = "Test"

try:
    while 'https://www.reddit.com' in next_link:
        next_submission = reddit.submission(url=next_link)
        next_submission.comments.replace_more(limit=None)
        next_comments = next_submission.comments.list()
        for comment in next_comments:
            if comment.id not in comment_ids:
                comment_ids.append(comment.id)

            if re.search(pattern, comment.body, re.IGNORECASE) and hasLink(comment):
                print('IN REGEX MATCHING 2')
                next_link = getNextLink(comment)
                final_comment = comment.body
                final_url = comment.permalink()
                chain_length += 1
                break
except TypeError:
    print("Caught type error.")
    pass

print('Origin comment: {}'.format(final_comment))
print('Chain length: {}'.format(chain_length))
print('Final url: {}'.format(final_url))

    # if submission.id not in posts_replied_to:
    #     if re.search('i love python', submission.title, re.IGNORECASE):
    #         # submission.reply('Me too!')
    #         print('Bot is replying to: {}'.format(submission.title))
    #         posts_replied_to.append(submission.id)

with open('posts_replied_to.txt', 'w') as f:
    for comment_id in comment_ids:
        f.write(comment_id + '\n')