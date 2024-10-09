# -*- coding: utf-8 -*-

import os

import math
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

#This scope allows access to your Youtube account. Scary.
scopes = ["https://www.googleapis.com/auth/youtube"]

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"

    #SECRETS FILE
    client_secrets_file = "YOUR_SECRETS_FILE.json"

    # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_local_server()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


    #TODO: Add input for ID, possibly strip from a given URL?
    #myPlaylistId="PLbg4rpCA3X3o4k0uIToFZKlvZY_VquWK6"
    myPlaylistId=input("\nInput Playlist ID: \n")


    #The lists of exisiting Video IDs and duplicate Playlist IDs
    #Video IDs are the IDs for the actual video (e.g. youtube.com/watch?v=YourIdHere)
    #Playlist IDs are unique to each video "entry" in a playlist.
    videoIdList=[]
    dupePlaylistIdList=[]

    #Initial Request
    request = youtube.playlistItems().list(
        part="contentDetails",
        maxResults=50,
        playlistId=myPlaylistId,
    )
    response = request.execute()


    #Get the nextPageToken for the next request.
    myPageToken = response["nextPageToken"]


    #Get the amount of videos in the list so we can find out how many future requests we need to send in order to search the entire playlist.
    playlistVideoCount = response["pageInfo"]["totalResults"]
    pageCount = math.ceil(playlistVideoCount/50) #We search in batches of max 50 results.
    print("\n", pageCount, " pages of videos found. \n")


    i = 0
    vidcount = 0
    while i < pageCount:
        for key in response["items"]:
            playlist_id = key["id"]
            video_id = key["contentDetails"]["videoId"];

            if video_id in videoIdList:
                dupePlaylistIdList.append(playlist_id)
                print("Dupe detected! Playlist ID: ", playlist_id, "|| Video ID: ", video_id)
            else:
                videoIdList.append(video_id)
        
        if i != pageCount -1:
            if "nextPageToken" in response:
                 myPageToken = response["nextPageToken"]
            else:
                print("No more pages")
                break

            request = youtube.playlistItems().list(
                part="contentDetails",
                maxResults=50,
                playlistId=myPlaylistId,
                pageToken=myPageToken,
            )
            
            response = request.execute()

        i+=1
        vidcount+=50
        print("~", vidcount, " Videos Searched")

    dupesLeft = len(dupePlaylistIdList)
    for dupVid in dupePlaylistIdList:
        request = youtube.playlistItems().delete(   
            id=dupVid
        )
        request.execute()
        print("Executing Delete Request for ID: ", dupVid)
        print(dupesLeft, "dupes left.")
        dupesLeft-=1

    print("\nDupes deleted. Have a nice day!")

if __name__ == "__main__":
    main()