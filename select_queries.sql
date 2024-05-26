SELECT v.video_name as Video_Name, c.channel_name as Channel_Name FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id order by c.channel_name ASC;

SELECT c.channel_name 
        AS Channel_Name, count(v.video_name) AS Total_Videos
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id 
                            group by c.channel_name order by c.channel_name ASC;
                            
SELECT c.channel_name AS Channel_Name, v.video_name AS Video_Title, v.view_count AS Views 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            ORDER BY v.view_count DESC
                            LIMIT 10;
						
                        
SELECT v.video_id, v.video_name 
        AS Video_Name, count(cm.comment_id) AS Total_Comments
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p, youtube_db.comments as cm 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and cm.video_id=v.video_id group by v.video_id order by v.video_name ASC;


SELECT c.channel_name AS Channel_Name, v.video_name 
        AS Video_Name, v.like_count AS Likes 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            ORDER BY v.like_count DESC
                            LIMIT 10;

SELECT v.video_name AS Video_Name, v.like_count AS Likes, v.dislike_count AS dislikes 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            ORDER BY v.video_name ASC;
                            
select channel_name as Channel_Name, channel_views as Views
	from youtube_db.channels order by channel_views DESC;
    
SELECT c.channel_name AS Channel_Name
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p
                            WHERE published_date LIKE '2022%' and v.playlist_id=p.playlist_id and v.playlist_id=p.playlist_id and p.channel_id=c.channel_id 
                            GROUP BY channel_name
                            ORDER BY channel_name;


SELECT c.channel_name 
        AS Channel_Name, avg(v.duration) AS Avg_Duration
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id 
                            group by c.channel_name order by c.channel_name ASC;

SELECT c.channel_name AS Channel_Name, v.video_name 
        AS Video_Name, count(cm.comment_id) AS Comment_Count 
                            FROM youtube_db.videos as v,youtube_db.channels as c,youtube_db.playlists as p,youtube_db.comments as cm 
                            where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and cm.video_id=v.video_id group by v.video_id order by v.Comment_Count DESC
                            LIMIT 10;
                            
SELECT c.channel_id as `Channel Id`,c.channel_name as `Channel Name`,c.channel_views as `Channel Views`,count(v.video_id) as `Video Count`, c.channel_subscribers as Subscribers
                     FROM youtube_db.channels as c,youtube_db.videos as v,youtube_db.playlists as p 
                     where v.playlist_id=p.playlist_id and p.channel_id=c.channel_id and c.channel_name='%s' group by c.channel_id