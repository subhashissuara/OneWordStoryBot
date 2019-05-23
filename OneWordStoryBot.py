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
    template = '6751df8a-7973-11e9-aa61-0e650c368d90' # Basically theme ID of flair

    print("Collecting Posts from " + subreddit_name + "...\n")
    for i in range(len(result)):
        post_ids.append(result[i].id) # Gathers the ids of all posts in given time frame
    
    post_ids_size = len(post_ids)

    print("Searching for completed stories...\n")
    for j in range(post_ids_size): # Gathers id of all posts with 'the end' in comments made by author of the post
        submission = reddit.submission(post_ids[j])
        submission.comments.replace_more(limit=None)
        author = result[j].author
        for comment in submission.comments.list(): # Goes through comments of post; Note: .list() is used to flatten all hierarchy of comments into a single list
            comment_lower = comment.body.lower()
            keyword = re.search("the end", comment_lower) # Searches for 'the end' in the comments
            if keyword and comment.author == author:
                keywordpost_ids.append(post_ids[j]) # Appends to a different list to sort out the posts with keywords from all posts
            
            title = submission.title
            title_split = title.split()

            if len(title_split) == 1: # As per the rules of the subreddit, a story post's title should be of one word
                submission.flair.select(template, 'Story')

    for k in range(len(keywordpost_ids)):
        words = []
        story = []
        submission = reddit.submission(keywordpost_ids[k]) # Pulls the post using the post ID
        
        if submission.saved: # To prevent going through read posts again
            continue

        title = submission.title
        words.append(title)
        title_split = title.split()

        if len(title_split) == 1: # As per the rules of the subreddit, a story post's title should be of one word
            for comment in submission.comments.list(): # Goes through comments of post; Note: .list() is used to flatten all hierarchy of comments into a single list
                words.append(comment.body)
                parent = comment
                parent.reply_sort = 'old'
                parent.refresh()
                for reply in parent.replies.list(): # Collects the words for the story
                    words.append(reply.body)
                break
        for l in range(len(words)):
            if words[l].lower() == "the end":
                words[l] = words[l].lower()
                words.remove("the end") # To remove the words 'the end' from the story as the only case possible is when the author tries to comment the keywords
        story = ' '.join(words)
        story_with_fullstop = (story + '.')
        print("Baking and publishing a story by " + str(submission.author) + "!")
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
    