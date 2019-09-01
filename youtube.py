from apiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import urllib.request
import json
from datetime import datetime
import time
import webbrowser
import random
import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

'''
This program comments on videos which meet set requirements given a search term.
This could be used for video spam, advertisement or just posting jokes on new videos
'''


api_key = "YOUR-API-KEY" 
client_secret_file = ("client_secret.json") #get from google api website

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"] #scope needed to make comments
storage = Storage('credentials.storage')

def authorize_credentials():

    # Fetch credentials from storage

    credentials = storage.get()
    # If the credentials doesn't exist in the storage location then run the flow

    if credentials is None or credentials.invalid:
        flow = flow_from_clientsecrets(client_secret_file, scope=scopes)
        http = httplib2.Http()
        credentials = run_flow(flow, storage, http=http)

    return credentials

credentials = authorize_credentials()

youtube = build("youtube", "v3", credentials=credentials)

#user inputted varaiables to customise the program

search = str(input("What To Search: ")) #the videos topic
subreq = int(input("Min Subs: "))
minutesBehind = int(input("How Recent Does It Have To Be In Minutes: "))
period = int(input("Time Between Runs In Minutes: "))
frequency = int(input("How Many Times Should It Run: "))
results = int(input("How many results, max 50: ")) #if you want to run it 24/7, with current quota budgets by google, period needs to be 1 hour and results needs to be about 5
sort = int(input("Newest(0), most relevent(1) or most viewed(2): "))


usedUrl = []

bannedPhrase = ["noob vs pro", "you laugh you lose", "C418", "song"] #ban videos with these in the title

#i chose to use this program to comment really unfunny minecraft comments on minecraft videos, however you can change it to be anything you want
comments = ["Why can't the Ender Dragon read a book?\nBecause he always starts at the End.\n\n\nI'll show myself out",
         "How does Steve get his exercise?\nHe runs around the block.\n\n\nI'll show myself out",
         "Have you heard of the creeper that went to a party?\nHe had a BLAST!\n\n\nI'll show myself out",
         "What's a ghast's favorite country?\nThe Nether-Lands!\n\n\nI'll show myself out",
         "What did Steve say as he faced off against a skeleton with his pickaxe?\nIve got a bone to pick with you.\n\n\nI'll show myself out",
         "Why did the Creeper cross the road?\nTo get to the other Sssssssside!\n\n\nI'll show myself out",
         "I would tell you a joke, but I Nether have the time.\n\n\n\nI'll show myself out",
         "What does a Minecraft turkey say?\nCobble, cobble, cobble!\n\n\nLike if you found this joke funny.\nComment if you thought it was stupid",
         ('What does a sheep say after you takes it wool?\n"Sheariously?"' +"\n\n\nOof, I'll show myself out"),
         "Why did Notch make a game with mining in it?\nHe thought it would be ore-some!\n\n\nLike if you found this joke funny.\nComment if you thought it was stupid",
         "Knock knock\nWho's there?\nCreeper\nCreeper who?\nBOOM!\n\nAwwww Man",
         "Love him or hate him,\nhes spitting facts.",
         "You keep me motivated to play mc.\nKeep up the great videos :D",
         "You keep me motivated.\nKeep up the great videos :D",
         "You should be in hermitcraft!\nLike if you agree",
         "I really enjoyed the video!\n\n\n\n*Like if you agree*",
         "I'm so obsessed with minecraft",
         "I love minecraft too much",
         "Great video!"]


def insert_comment(youtube, channel_id, video_id, text): #places the comment on the video
    insert_result = youtube.commentThreads().insert(
        part="snippet",
        body=dict(
            snippet=dict(
                channelId=channel_id,
                videoId=video_id,
                topLevelComment=dict(
                    snippet=dict(
                        textOriginal=text)
                )
            )
        )
    ).execute()

    comment = insert_result["snippet"]["topLevelComment"]
    author = comment["snippet"]["authorDisplayName"]
    text = comment["snippet"]["textDisplay"]
    #print("Inserted comment for %s: %s" % (author, text))
    

for i in range(frequency):
    #gets the time and day
    changedMinutesBehind = minutesBehind
    currentSecond= datetime.now().second
    currentMinute = datetime.now().minute
    currentHour = datetime.now().hour
    currentHour -= 1 #you may need to change this value, i have this as 1 as uk time is currently 1 hour ahead of gmt time
    currentDay = datetime.now().day
    currentMonth = datetime.now().month
    currentYear = datetime.now().year
    end_time = datetime(year=currentYear, month=currentMonth, day=currentDay, hour=currentHour, minute=currentMinute).strftime("%Y-%m-%dT%H:%M:%SZ") #the latest the video can be is the time of the search

    #makes sure that there is no data issues, for example 25 hours in a day. And subtracts the time of how frequent the video has to be
    while changedMinutesBehind >= 60:
        currentHour -= 1
        changedMinutesBehind -=60
    if changedMinutesBehind < currentMinute:
        currentMinute -= changedMinutesBehind
    while changedMinutesBehind > currentMinute:
        currentMinute = currentMinute - changedMinutesBehind + 60
        currentHour -= 1
    if currentHour < 0:
        currentDay -= 1
        currentHour += 24
    start_time = datetime(year=currentYear, month=currentMonth, day=currentDay, hour=currentHour, minute=currentMinute).strftime("%Y-%m-%dT%H:%M:%SZ")  #what time the video has to be posted after

    if sort == 0:
        req = youtube.search().list(q=search, part="snippet", type="video", maxResults=results, publishedAfter=start_time, publishedBefore=end_time, order="date")
        print("\nSearched, requred time = " + start_time + "-" + end_time + ", order = date\n")
    elif sort == 1:
        req = youtube.search().list(q=search, part="snippet", type="video", maxResults=results, publishedAfter=start_time, publishedBefore=end_time, order="relevance")
        print("\nSearched, requred time = " + start_time + "-" + end_time + ", order = relevance\n")
    else:
        req = youtube.search().list(q=search, part="snippet", type="video", maxResults=results, publishedAfter=start_time, publishedBefore=end_time, order="viewCount")
        print("\nSearched, requred time = " + start_time + "-" + end_time + ", order = viewCount\n")

    while True: #seaches for the video
        try:
            res = req.execute()
            break
        except: #retries every hour if theres no quota
            print("Ran out of quota\nWaiting 1 hour\nTime: ", datetime.now().hour, ":", datetime.now().minute)
            time.sleep(3600)
    
    count = 0
    for item in res["items"]: #for each video, get all the data needed
        count += 1
        banned = False
        Id = item["id"]
        videoId = Id["videoId"]
        snippet = item["snippet"]
        videoDate = snippet["publishedAt"]
        videoName = snippet["title"]
        channelId = snippet["channelId"]
        channelName = snippet["channelTitle"]
        live = snippet["liveBroadcastContent"]
        
        data = urllib.request.urlopen("https://www.googleapis.com/youtube/v3/channels?part=statistics&id="+channelId+"&key="+api_key).read()
        subs = json.loads(data)["items"][0]["statistics"]["subscriberCount"]

        #goes through each video requirement to see if it passes
        for phrase in bannedPhrase: 
            if (phrase.lower()) in (videoName.lower()):
                banned = True
                print("Contains banned phrase,", (phrase.lower()))
        f = open("videoId.txt","r")
        lines = f.readlines()
        for line in lines:
            if str(line) == str(videoId + "\n") or str(line) == str(videoId) or str(line) == str("\n" + videoId):
                banned = True
                print("Video Already used,", videoName)
        f.close()
        if int(subs) > subreq and banned == False:
            while True:
                try:
                    captions = youtube.captions().list(part="snippet", videoId=videoId).execute()
                    break
                except googleapiclient.errors.HttpError:
                    print("Ran out of quota\nWaiting 1 hour\nTime - ", datetime.now().hour, ":", datetime.now().minute)
                    time.sleep(3600)
            captionItems = captions["items"]
            try:
                captionItems = captionItems[0]
                captionSnippet = captionItems["snippet"]
                captionLanguage = captionSnippet["language"]
            except IndexError:
                print("No Captions, Video ID:", videoId)
                captionLanguage = "unknown"
                
            
            if live != "live" and live == "none" and captionLanguage == "en": #if it passed comment and print out the channels details
                print("Made a comment to - Channel Name: " + str(channelName) + " - Subs: " + str(subs) + " - Channel Id: " + str(channelId) + " - Video Name: " + str(videoName) + " - Video Id: " + str(videoId) + " - Video Date: " + str(videoDate))
                url = "https://www.youtube.com/watch?v=" + str(videoId)

                while True:
                    try:
                        insert_comment(youtube, channelId, videoId, comments[random.randint(0, (len(comments)-1))])
                        break
                    except IndexError:
                        print("IndexError")

                #adds the video id to a text file to make sure we dont make 2 comments on 1 video
                f = open("videoId.txt","a+")
                videoId = "\n" + str(videoId)
                f.write(videoId)
                f.close
        
            elif live == "live":
                print("Video is live")
            elif captionLanguage != "en" and captionLanguage != "unknown":
                print("Wrong Language: " + captionLanguage + ", Video Id: " + str(videoId))
        
        elif int(subs) < subreq:
            print("Video did not read sub requirement, " + str(subs) + "/" + str(subreq) + ", Video Id: " + str(videoId) + ", Date: " + str(videoDate))
            

    if i < frequency: #once the search is done print out a checkpoint, and wait the period*60
        print("\nScan " + str(i+1) + " Run, " + str(period) + " minutes until the next one\nTime - ", datetime.now().hour, ":", datetime.now().minute)
        hours = int(period / 60)
        minutes = period % 60 
        print("Next Scan Time - " +  str(datetime.now().hour + hours) + ":" + str(datetime.now().minute + minutes))
        print("Total Video Results = " + str(count) + "\n")
        time.sleep(period*60)
