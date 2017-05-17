#!/usr/bin/env python
import praw
import pdb
import re
import os
import copy

from bs4 import BeautifulSoup

reddit = praw.Reddit('switch-a-roo crawler')
pattern = 'roo|r-oo'
DEFAULT_LINK = 'https://www.reddit.com/r/saskatoon/comments/6ak88m/saskatoon_man_in_hospital_after_machete_attack/dhg26wk/?context=4'

def getNextLink(comment):
    soup = BeautifulSoup(comment.body_html, 'html.parser')
    for link in soup.find_all('a'):
        if 'https://www.reddit.com' in link.get('href') and re.search(pattern, link.contents[0], re.IGNORECASE):
            return link.get('href')
    return None

def hasLink(comment):
    soup = BeautifulSoup(comment.body_html, 'html.parser')
    return len(soup.find_all('a')) > 0

urls = []

start_link = input("Enter a link to start.\n")
max_length = int(input("How many links do you want to find?\n"))

if start_link.strip() == '':
    print('Using default link.')
    start_link = DEFAULT_LINK

start_submission = reddit.submission(url=start_link)
start_submission.comments.replace_more(limit=None)

for comment in start_submission.comments.list():
    if re.search(pattern, comment.body, re.IGNORECASE) and hasLink(comment):
        next_link = getNextLink(comment)

        if '/?' in next_link:
            next_id = next_link.split('comments/')[1].split('?')[0].split('/')[-2]
        elif '?' in next_link:
            next_id = next_link.split('comments/')[1].split('?')[0].split('/')[-1]
        else:
            next_id = next_link.split('comments/')[1].split('/')[-2]

        break
    else:
        next_link = None

counter = 0
prev_id = ''

while 'https://www.reddit.com' in next_link and counter < max_length:
    print(next_id)
    print(next_link)

    if prev_id == next_id:
        print('Something went wrong. Exiting...')
        break

    next_comment = reddit.comment(id=next_id)

    while not next_comment.is_root:
        next_comment = next_comment.parent()

    next_comment.refresh()
    next_comments = next_comment.replies[:]

    while next_comments:
        comment = next_comments.pop(0)
        if isinstance(comment, praw.models.MoreComments):
            comment = comment.comments()
            next_comments.extend(comment) # This is potentially bad...changing data type of comment?
            continue
        next_comments.extend(comment.replies)

        if re.search(pattern, comment.body, re.IGNORECASE) and hasLink(comment):
            next_link = getNextLink(comment)
            urls.append(next_link)

            if next_link is None:
                continue

            counter += 1

            prev_id = next_id
            if '/?' in next_link:
                next_id = next_link.split('comments/')[1].split('?')[0].split('/')[-2]
            elif '?' in next_link:
                next_id = next_link.split('comments/')[1].split('?')[0].split('/')[-1]
            else:
                next_id = next_link.split('comments/')[1].split('/')[-2]

            break

with open ('./chain.txt', 'w') as f:
    for i, url in enumerate(urls, start=1):
        f.write('{}: {}\n'.format(i, url))
