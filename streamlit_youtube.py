import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px

import mysql.connector as sql
import os
import pandas as pd
import googleapiclient.discovery
from datetime import datetime
import isodate

# CONSTANTS
api_service_name = "youtube"
api_version = "v3"
api_key = "AIzaSyDtacQ22yD88vRiLdK03nEooZJAouEr3NU"

youtube_channel_part = "snippet,contentDetails,statistics,status"
youtube_videos_part = "contentDetails"
youtube_video_details_part = "snippet,contentDetails,statistics"
youtube_comment_part = "snippet"

#youtube api initiation
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

def get_channel_details(channel_id):
    request = youtube.channels().list(
        part = youtube_channel_part,
        id = channel_id
    )
    response = request.execute()

    channel_data = response['items'][0]
    
    data = dict(
        channel_id = channel_data['id'],
        channel_name = channel_data['snippet']['title'],
        channel_description = channel_data['snippet']['description'],
        channel_publishedat = channel_data['snippet']['publishedAt'],
        channel_playlistid = channel_data['contentDetails']['relatedPlaylists']['uploads'],
        channel_subscribers = channel_data['statistics']['subscriberCount'],
        channel_views = channel_data['statistics']['viewCount'],
        channel_videocount = channel_data['statistics']['videoCount'],
        channel_status = channel_data['status']['privacyStatus'],
        channel_type = channel_data['kind']
    )
    return data

# FUNCTION TO GET VIDEO IDS
def get_channel_videos(channel_id):
    video_ids = []
    # get Uploads playlist id
    res = youtube.channels().list(id=channel_id, 
                                  part=youtube_videos_part).execute()
    playlist_id = res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    next_page_token = None
    
    while True:
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids

# FUNCTION TO GET PLAYLISTS from channel
def get_channel_playlists(channel_id):
    playlists = []

    next_page_token = None
    
    while True:
        print("get_channel_playlists")
        res = youtube.playlists().list(channelId=channel_id, 
                                           part='id,snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        for item in res['items']:
            playlist = dict(
                playlist_id = item['id'],
                channel_id = item['snippet']['channelId'],
                playlist_name = item['snippet']['title']
            )
            playlists.append(playlist)

        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break

    return playlists


# FUNCTION TO GET VIDEO IDS from playlist
def get_playlist_videos(playlist_id):
    video_ids = []

    next_page_token = None
    
    while True:
        print("get_playlist_videos")
        res = youtube.playlistItems().list(playlistId=playlist_id, 
                                           part='snippet', 
                                           maxResults=50,
                                           pageToken=next_page_token).execute()
        
        for i in range(len(res['items'])):
            video_ids.append(res['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token = res.get('nextPageToken')
        
        if next_page_token is None:
            break
    return video_ids

def get_video_details(video_ids, playlist_id):

    videos = []

    next_page_token = None
    
    for i in range(0, len(video_ids), 50):
        res = youtube.videos().list(id = ','.join(video_ids[i:i+50]),
                                        part = youtube_video_details_part,
                                        maxResults=50
                                        ).execute()
        
        for i in range(len(res['items'])):
            video = dict(
                video_id = res['items'][i]['id'],
                playlist_id = playlist_id,
                video_name = res['items'][i]['snippet']['title'],
                video_description = res['items'][i]['snippet']['description'],
                published_date = datetime.strptime(res['items'][i]['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ"),
                view_count = res['items'][i]['statistics']['viewCount'],
                like_count = res['items'][i]['statistics'].get('likeCount', 0),
                dislike_count = res['items'][i]['statistics'].get('dislikeCount', 0),
                favorite_count = res['items'][i]['statistics']['favoriteCount'],
                comment_count = res['items'][i]['statistics']['commentCount'],
                duration = .parse_duration(res['items'][i]['contentDetails']['duration']).total_seconds(),
                thumbnail = res['items'][i]['snippet']['thumbnails']['high']['url'],
                caption_status = res['items'][i]['contentDetails']['caption'],
            )
            videos.append(video)

    return videos

def get_video_comments(video_id):

    comments = []

    next_page_token = None
    # while True:
    res = youtube.commentThreads().list(videoId = video_id,
                                        part = youtube_comment_part,
                                        maxResults=50,
                                        pageToken=next_page_token).execute()
    
    for item in res['items']:
        comment = dict(
            comment_id = item['id'],
            video_id = item['snippet']['videoId'],
            comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay'],
            comment_author = item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
            comment_published_date = datetime.strptime(item['snippet']['topLevelComment']['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")

        )
        comments.append(comment)

    # next_page_token = res.get('nextPageToken')
        
    # if next_page_token is None:
    #     break
    return comments

# SETTING PAGE CONFIGURATIONS
icon = ""
st.set_page_config(page_title= "Youtube Data Harvesting and Warehousing",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded",
                   menu_items={})
st.title("Youtube Data Harvesting and Warehousing")

# CREATING OPTION MENU
with st.sidebar:
    selected = option_menu(None, ["Home","Collect and Migrate to MySQL","Analytics"], 
                           icons=["house-door-fill","tools","card-text"],
                           default_index=0,
                           orientation="vertical",
                           styles={"nav-link": {"font-size": "14px", "text-align": "centre", "margin": "0px", 
                                                "--hover-color": "#FF0000", },
                                   "icon": {"font-size": "14px"},
                                   "container" : {"max-width": "6000px"},
                                   "nav-link-selected": {"background-color": "#FF0000"}})

# CONNECTING WITH MYSQL DATABASE
mydb = sql.connect(host="localhost",
                   user="root",
                   password="12345678",
                   database= "youtube_db"
                  )
mycursor = mydb.cursor(buffered=True)

# FUNCTION TO GET CHANNEL NAMES FROM MYSQL
def channel_names():
    mycursor.execute("""SELECT channel_name
                            FROM channels""")
    return [item[0] for item in mycursor.fetchall()]

#HOME
if selected == "Home":
    st.write("#### Select a channel to check the video details")
        
    ch_names = channel_names()
    option = st.selectbox("Select channel",options= ch_names, index=None)

    mycursor.execute("""SELECT c.channel_id as `Channel Id`,c.channel_name as `Channel Name`,c.channel_views as `Channel Views`,count(v.video_id) as `Video Count`, c.channel_subscribers as Subscribers
                     FROM youtube_db.channels as c,youtube_db.videos as v,youtube_db.playlists as p 
                     where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and c.channel_name='%s' group by c.channel_id"""%option)
    
    if option:
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)



# EXTRACT and TRANSFORM PAGE
if selected == "Collect and Migrate to MySQL":

    channel_id = st.text_input("Youtube Channel 

    if channel_id and st.button("Extract Data"):
        ch_details = get_channel_details(channel_id[0])
        st.write(f'#### Extracted data from :green["{ch_details["channel_name"]}"] channel')
        st.table(ch_details)

    if st.button("Migrate to MySQL"):
        ch_details = get_channel_details(channel_id[0])
        playlists = get_channel_playlists(channel_id[0])

        if len(playlists) == 0:
            playlists.append(
                dict(
                    playlist_id = ch_details['channel_id'],
                    channel_id = ch_details['channel_id'],
                    playlist_name = ch_details['channel_name']
                )
            )

        v_ids = get_channel_videos(channel_id[0])

        st.write(f'#### Videos :green["{len(v_ids)}"] in channel')
        vid_details = []
        for p in playlists:
            each_video = get_video_details(v_ids, p['playlist_id'])
            vid_details.extend(each_video)


        def comments():
            com_d = []
            for i in v_ids:
                try: 
                    com_d+= get_video_comments(i)
                except:
                    print("Video commments issue")
            return com_d
        
        comm_details = comments()
        st.write(f'#### VideoComments :green["{len(comm_details)}"] in channel')

        # Remove duplicate video_ids from dataframe videosdf
        

        def insert_into_channels():
                query = """INSERT INTO channels (channel_id,channel_name,
                channel_type,channel_views,channel_description,channel_status,channel_subscribers) VALUES(%s,%s,%s,%s,%s,%s,%s)"""
                try:
                    mycursor.execute(query,(ch_details['channel_id'],
                                                ch_details['channel_name'],
                                                ch_details['channel_type'],
                                                ch_details['channel_views'],
                                                ch_details['channel_description'],
                                                ch_details['channel_status'],
                                                ch_details['channel_subscribers']))
                    mydb.commit()
                except:
                    print("Error in channel insertion")
                
        def insert_into_videos():
            query1 = """INSERT INTO videos (video_id, playlist_id, video_name, video_description,
            published_date, view_count, like_count,dislike_count, favorite_count, comment_count,
            duration, thumbnail, caption_status) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

            for i in vid_details:
                t=tuple(i.values())
                try:
                    mycursor.execute(query1,t)
                    mydb.commit()
                except:
                    print("Error in video insertion")

        def insert_into_playlists():
            query2 = """INSERT INTO playlists (playlist_id, channel_id, playlist_name) VALUES(%s,%s,%s)"""

            for i in playlists:
                t=tuple(i.values())
                try:
                    mycursor.execute(query2,t)
                    mydb.commit()
                except:
                    print("Error in playlist insertion")
            
        def insert_into_comments():
            query2 = """INSERT INTO comments (comment_id, video_id, comment_text,
            comment_author, comment_published_date) VALUES(%s,%s,%s,%s,%s)"""

            for i in comm_details:
                t=tuple(i.values())
                try:
                    mycursor.execute(query2,t)
                    mydb.commit()
                except:
                    print("Error in video insertion")

        try:
            insert_into_channels()
            insert_into_playlists()
            insert_into_videos()
            insert_into_comments()
            st.success("Transformation to MySQL Successful!!!")
        except Exception as error:
            st.error("Channel details already transformed!!")
            print(error)


        st.success("Migrate to MySQL successful !!")

if selected == "Analytics":
    st.write("## :orange[Select any question to get Insights]")
    questions = st.selectbox('Questions',
    ['Click the question that you would like to query',
    '1. What are the names of all the videos and their corresponding channels?',
    '2. Which channels have the most number of videos, and how many videos do they have?',
    '3. What are the top 10 most viewed videos and their respective channels?',
    '4. How many comments were made on each video, and what are their corresponding video names?',
    '5. Which videos have the highest number of likes, and what are their corresponding channel names?',
    '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?',
    '7. What is the total number of views for each channel, and what are their corresponding channel names?',
    '8. What are the names of all the channels that have published videos in the year 2022?',
    '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?',
    '10. Which videos have the highest number of comments, and what are their corresponding channel names?'])
    
    if questions == '1. What are the names of all the videos and their corresponding channels?':
        mycursor.execute("""SELECT v.video_name as Video_Name, c.channel_name as Channel_Name FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id order by c.channel_name ASC;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        
    elif questions == '2. Which channels have the most number of videos, and how many videos do they have?':
        mycursor.execute("""SELECT c.channel_name 
        AS Channel_Name, count(v.video_name) AS Total_Videos
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id group by c.channel_name order by c.channel_name ASC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Number of videos in each channel :]")
        #st.bar_chart(df,x= mycursor.column_names[0],y= mycursor.column_names[1])
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '3. What are the top 10 most viewed videos and their respective channels?':
        mycursor.execute("""SELECT DISTINCT (v.video_name) AS `Video Title`, v.view_count AS Views, c.channel_name AS `Channel Name`
	FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
    WHERE v.playlist_id=p.playlist_id and p.channel_id=c.channel_id
                            ORDER BY v.view_count DESC
                            LIMIT 10""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Top 10 most viewed videos :]")
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[0],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '4. How many comments were made on each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT v.video_id, v.video_name 
        AS Video_Name, count(cm.comment_id) AS Total_Comments
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p, youtube_db.comments as cm 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and cm.video_id=v.video_id group by v.video_id order by v.video_name ASC""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
          
    elif questions == '5. Which videos have the highest number of likes, and what are their corresponding channel names?':
        mycursor.execute("""SELECT DISTINCT (v.video_name) AS `Video Title`, v.like_count AS Likes, c.channel_name AS `Channel Name`
	FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
    WHERE v.playlist_id=p.playlist_id and p.channel_id=c.channel_id
                            ORDER BY v.like_count DESC
                            LIMIT 10;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Highest number of likes :]")
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[0],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?':
        mycursor.execute("""SELECT DISTINCT (v.video_name) AS Video_Name, v.like_count AS Likes, v.dislike_count AS dislikes 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            ORDER BY v.video_name ASC;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
         
    elif questions == '7. What is the total number of views for each channel, and what are their corresponding channel names?':
        mycursor.execute("""select channel_name as Channel_Name, channel_views as Views
	from youtube_db.channels order by channel_views DESC;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Channels vs Views :]")
        fig = px.bar(df,
                     x=mycursor.column_names[0],
                     y=mycursor.column_names[1],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '8. What are the names of all the channels that have published videos in the year 2022?':
        mycursor.execute("""SELECT c.channel_name AS `Channel Name`
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            WHERE published_date LIKE '2022%' and v.playlist_id=p.playlist_id and v.playlist_id=p.playlist_id and p.channel_id=c.channel_id 
                            GROUP BY channel_name
                            ORDER BY channel_name""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        
    elif questions == '9. What is the average duration of all videos in each channel, and what are their corresponding channel names?':
        mycursor.execute("""SELECT c.channel_name 
        AS `Channel Name`, avg(v.duration) AS `Avg Duration`
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id 
                            group by c.channel_name order by c.channel_name ASC;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names
                          )
        st.write(df)
        st.write("### :green[Average video duration for channels :]")
        
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[0],
                     orientation='h',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)
        
    elif questions == '10. Which videos have the highest number of comments, and what are their corresponding channel names?':
        mycursor.execute("""SELECT c.channel_name AS Channel_Name, v.video_name 
        AS Video_Name, count(cm.comment_id) AS Comment_Count 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p,youtube_db.comments as cm 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and cm.video_id=v.video_id group by v.video_id order by v.Comment_Count DESC
                            LIMIT 10;""")
        df = pd.DataFrame(mycursor.fetchall(),columns=mycursor.column_names)
        st.write(df)
        st.write("### :green[Videos with most comments :]")
        fig = px.bar(df,
                     x=mycursor.column_names[1],
                     y=mycursor.column_names[2],
                     orientation='v',
                     color=mycursor.column_names[0]
                    )
        st.plotly_chart(fig,use_container_width=True)        
