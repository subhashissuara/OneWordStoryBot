# ------------------------------------------
# Writtern by Subhashis Suara / QuantumBrute
# ------------------------------------------

from psaw import PushshiftAPI
import praw
import time
import re
import sys

# --------------------------------------------------------------------------------

subreddit_name = 'OneWordStory' # Mention the subreddit that bot should work on
limitno = 30000 # Set the maximum number of posts to get in the given timeframe
end_epoch = int(time.time()) # Current time
x = int(input("Enter the number of days you want to search for:"))
start_epoch = int(end_epoch - (60*60*24*x)) # Current time - the amount you mention in seconds

#---------------------------------------------------------------------------------

print("Starting Bot...")

reddit = praw.Reddit(client_id= ' ',         
		     client_secret= ' ',
		     username= ' ',
		     password= ' ',
		     user_agent= 'Created by u/QuantumBrute') # Login to reddit API

api = PushshiftAPI() # Variable to use the PushShiftAPI
subreddit = reddit.subreddit(subreddit_name)

print("From: "+ str(start_epoch))
print("Till: "+ str(end_epoch))
print("\n")

result = list(api.search_submissions(after=start_epoch, 
                                    before=end_epoch,
                                    subreddit=subreddit_name,
                                    filter=['author', 'id'],
                                    limit=limitno)) # Gets the data with the parameters mentioned from PushShift and makes it into a list

def makestory():
    post_ids = []
    keywordpost_ids = []
    counter = 0
    template = '6751df8a-7973-11e9-aa61-0e650c368d90'

    print("Collecting Posts from " + subreddit_name + "...\n")
    for i in range(len(result)):
        post_ids.append(result[i].id) # Gathers the ids of all posts in given time frame
    
    post_ids_size = len(post_ids)

    print("Searching for completed stories...\n")
    for j in range(post_ids_size): # Gathers id of all posts with 'the end' in comments made by author of the post
        submission = reddit.submission(post_ids[j])
        submission.comments.replace_more(limit = None)
        author = result[j].author

        title = submission.title
        title_split = title.split()

        if len(title_split) == 1:
            submission.flair.select(template, 'Story')

        for comment in submission.comments.list(): # Goes through comments of post; Note: .list() is used to flatten all hierarchy of comments into a single list
            comment_lower = comment.body.lower()
            keyword = re.search("the end", comment_lower) # Searches for 'the end' in the comments
            if keyword and comment.author == author:
                print("Completed story found! OP: u/" + author)
                keywordpost_ids.append(post_ids[j])
                break
    print("\n")

    for k in range(len(keywordpost_ids)):
        words = []
        story = []
        submission = reddit.submission(keywordpost_ids[k])
        
        if submission.saved:
            continue

        title = submission.title
        words.append(title)
        title_split = title.split()

        if len(title_split) == 1:
            submissions = submission.comments.list()
            while True:
                words.append(submissions[0].body)
                parent = submissions[0]
                parent.reply_sort = 'old'
                parent.refresh()
                parent.replies.replace_more(limit=None, threshold = 0)
                for reply in parent.replies.list():
                    words.append(reply.body)
                break

        for l in range(len(words)):
            word_lower = words[l].lower()
            if word_lower == "the end" or word_lower == "[deleted]" or word_lower == "[removed]":
                words.remove(words[l]) # To remove the unnecessary words 

        last_char = words[len(words) - 1]

        if last_char == '''"''' or last_char == "!" or last_char == "?" or last_char == '''."''':
            story = ' '.join(words)
            story_with_fullstop = story 
        else:
            story = ' '.join(words)
            story_with_fullstop = (story + '.')

        print("Baking and publishing a story by u/" + str(submission.author) + "!")
        bot_reply = submission.reply(story_with_fullstop)
        bot_reply.mod.distinguish(sticky=True)
        submission.save()
        counter += 1
    
    if counter == 0:
        print("\nOops... No stories found!")
    elif counter == 1:
        print("\nSuccessfully baked and published 1 story!")
    elif counter > 1:
        print("\nSuccessfully baked and published " + str(counter) + " stories!")

    print(' ')
    input("Press ENTER to exit...")
    sys.exit()

def main():
    makestory()
   

if __name__ == "__main__": 
    main()
