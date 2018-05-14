from django.utils import timezone
from datetime import date, datetime, time, timedelta
from time import mktime
from pytvdbapi import api
import feedparser
import MySQLdb
connection=MySQLdb.connect(
    host='localhost',user='aristia',passwd='Petransikey18',db='aristia')
cursor=connection.cursor()

dt0 = timezone.make_aware(datetime.combine(today - timedelta(days=2), time.min))
dt1 = timezone.make_aware(datetime.combine(today - timedelta(days=30), time.min))
dt3 = timezone.make_aware(datetime.combine(today - timedelta(days=500), time.min))

module_dir = os.path.dirname(__file__)  # get current directory

db = api.TVDB("D620620B2C727377", banners=True)

#series = Series.objects.filter(lastlookup__lt=dt0)
sql="SELECT id,title FROM shows_series WHERE lastlookup < '%s'" ,(dt0)
cursor.execute(sql)
series=cursor.fetchall()


for show in series:
    result = db.search(show.title,"en")
    tvdbshow = result[0]
    for tvdbseason in tvdbshow:
        for tvdbepi in tvdbseason:

            #Episode.objects.filter(due__lte=dt3).delete()# delete old episodes
            try:
                AiredDT = timezone.make_aware(datetime.combine(tvdbepi.FirstAired, time.min))
            except:
                AiredDT = None
            if AiredDT is not None and AiredDT > dt1:
                try:
                    sql="SELECT * FROM shows_episodes WHERE `season`= '%s', `episode`='%s', serid='%s'" ,(tvdbepi.SeasonNumber,tvdbepi.EpisodeNumber,tvdbshow.id)
                    cursor.execute(sql)
                    dupe = cursor.fetchall()
                except:
                    dupe = None
                if dupe is None:                    
                    sql="INSERT INTO shows_episodes (`title`,`season`,`episode`,`date_added`,`due`,`desc`,`serid`,`epiid`,`seaid`,`downloaded`,`series_id`) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',)" , (tvdbshow.SeriesName, tvdbepi.SeasonNumber, tvdbepi.EpisodeNumber, dt_today, AiredDT, tvdbepi.Overview, tvdbshow.id, tvdbepi.id, tvdbepi.seasonid, dt_1000, show.id)
                    cursor.execute(sql)

                elif dupe.due != AiredDT:                    
                    sql="UPDATE shows_episodes SET `date_added`='%s', `due`='%s', `desc`='%s',`serid`='%s',`epiid`='%s', `seaid`='%s' WHERE `id` = '%s'",(dt_today, AiredDT, tvdbepi.Overview, tvdbshow.id, tvdbepi.id, tvdbepi.seasonid, dt_1000, dupe.id)
                    cursor.execute(sql)

    
    sql="UPDATE shows_series SET `lastlookup`=,`tvdbid`=,`overview`=,`firstaired`=,`imdb`=  WHERE `id` = %s" , (dt_today,tvdbshow.id,tvdbshow.Overview,timezone.make_aware(datetime.combine(tvdbshow.FirstAired, time.min)),tvdbshow.IMDB_ID,show.id)
    cursor.execute(sql)
    connection.close()