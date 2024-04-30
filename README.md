# YouTube Data Harvesting and Warehousing using SQL, python, and Streamlit

## Problem Statement:

The problem statement is to create a Streamlit application that allows users to access and analyze data from multiple YouTube channels. The application should have the following features:</br>

1. Ability to input a YouTube channel ID and retrieve all the relevant data (Channel name, subscribers, total video count, playlist ID, video ID, likes, dislikes, comments of each video) using Google API.</br>
2. Ability to collect data for up to 10 different YouTube channels and store them in the data lake by clicking a button.</br>
3. Option to store the data in a MYSQL or PostgreSQL.</br>
4. Ability to search and retrieve data from the SQL database using different search options, including joining tables to get channel details.

## 1. Tools Install
* Visual code.
* Jupyter notebook.
* Python
* MySQL.
* Youtube API key.

## 2. Requirement Libraries to Install
* pip install google-api-python-client, mysql-connector-python, pandas, numpy, plotly-express, streamlit, streamlit_option_menu, ipynb, isodate

##  3. Import Libraries

#### Youtube API libraries

* import googleapiclient.discovery
* from googleapiclient.discovery import build
* File handling libraries
#### SQL libraries

* import mysql.connector
#### pandas, numpy

* import pandas as pd
* import numpy as np
#### Dashboard libraries

* import streamlit as st
* import plotly.express as px

##  4. Run application

1. Create database "youtube_db" in mysql
2. Run "python db_init.py" to setup the required schema
3. Run "streamlit run streamlit_youtube.py", then application will run on the 8501 port

## 5. Screenshots

<img width="1509" alt="Screenshot 2024-04-30 at 6 53 16 PM" src="https://github.com/raji-gadagoju/Youtube_Data_Harvesting/assets/52797530/64c9f5be-f479-41fc-98f4-42b203a42021">
<img width="1509" alt="Screenshot 2024-04-30 at 6 54 41 PM" src="https://github.com/raji-gadagoju/Youtube_Data_Harvesting/assets/52797530/5a80534a-e640-48e5-9e78-d1872a2bac95">
<img width="1509" alt="Screenshot 2024-04-30 at 6 55 47 PM" src="https://github.com/raji-gadagoju/Youtube_Data_Harvesting/assets/52797530/82354d28-915f-4617-a929-09601743f5fe">
<img width="1509" alt="Screenshot 2024-04-30 at 6 56 05 PM" src="https://github.com/raji-gadagoju/Youtube_Data_Harvesting/assets/52797530/b37e9b06-1118-4c94-a99b-04a0158328bc">

## 6. References

Streamlit Doc:
 https://docs.streamlit.io/library/api-reference
 
Youtube API Reference:
 https://developers.google.com/youtube/v3/getting-started






