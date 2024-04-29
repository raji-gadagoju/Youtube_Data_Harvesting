import mysql.connector as mysql
import os
import pandas as pd

client = mysql.connect(
    host ="localhost",
    user="root",
    password="12345678",
    database="youtube_db"
)

cursor = client.cursor()

#create channels table
channels_table="""create table if not exists channels(
    id int auto_increment primary key,
    channel_id varchar(255) unique,
    channel_name varchar(255),
    channel_type varchar(255),
    channel_views int,
    channel_description text,
    channel_status varchar(255),
    channel_subscribers int
)"""
cursor.execute(channels_table)

#create playlist table
playlist_table="""create table if not exists playlists(
    id int auto_increment primary key,
    playlist_id varchar(255) unique,
    channel_id varchar(255) ,
    playlist_name varchar(255),
    FOREIGN KEY (channel_id) REFERENCES channels(channel_id)
)"""
cursor.execute(playlist_table)

#create video table
video_table="""create table if not exists videos(
    id int auto_increment primary key,
    video_id varchar(255) unique,
    playlist_id varchar(255),
    video_name varchar(255),
    video_description text,
    published_date datetime,
    view_count int,
    like_count int,
    dislike_count int,
    favorite_count int,
    comment_count int,
    duration int,
    thumbnail varchar(255),
    caption_status varchar(255),
    FOREIGN KEY (playlist_id) REFERENCES playlists(playlist_id)
)"""
cursor.execute(video_table)

#create comment table
comment_table="""create table if not exists comments(
    id int auto_increment primary key,
    comment_id varchar(255) unique,
    video_id varchar(255),
    comment_text text,
    comment_author varchar(255),
    comment_published_date datetime,
    FOREIGN KEY (video_id) REFERENCES videos(video_id)
)"""
cursor.execute(comment_table)

client.commit()
