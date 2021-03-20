from django.db import models
from django.utils import timezone
from datetime import timedelta, datetime, date

dt_1000 = timezone.make_aware(datetime(1000,1,1,0,0,0))

# Create your models here.
class Series(models.Model):
    title = models.CharField(max_length=200)
    seotitle = models.CharField(max_length=200,unique=True)
    period = models.CharField(max_length=200,null=True,blank=True)
    firstaired = models.DateTimeField()
    lastdue = models.DateTimeField()
    lastepi = models.CharField(max_length=10)
    overview = models.TextField(null=True,blank=True)
    rssfeedid = models.IntegerField(unique=True)
    audCHOICES = (('', 'All',), ('Mat', 'Mat',), ('Stella', 'Stella',))
    audience = models.CharField(max_length=200,null=True,blank=True,choices=audCHOICES,default='')
    imdb = models.CharField(max_length=200,null=True,blank=True)
    banner = models.ImageField(upload_to='shows/bart/',null=True,blank=True)
    thumb = models.ImageField(upload_to='shows/tart/',null=True,blank=True)
    lastlookup = models.DateTimeField()
    tvdbid = models.IntegerField()

    def __str__(self):
        return self.title.replace("\\'","\'")

    def clean_title(self):
        c=self.title
        replace = [" ","\\'",":","."]
        for i in replace:
            c=c.replace(i,'')
        return c

    def audience_letter(self):
        return self.audience[0]

    def tvdblink(self):
        return "http://www.thetvdb.com/?tab=series&id={0}&lid=7".format(self.tvdbid)

    def imdblink(self):
        return "http://www.imdb.com/title/{0}/".format(self.imdb)

    def rsslink(self):
        return "http://showrss.info/browse/{0}".format(self.rssfeedid)

    def banner_img(self):
        return "/shows/img/bart/{0}.jpg".format(self.tvdbid)

    def readmorelink(self):
        if len(self.overview.split()) > 80:
            return "<a id='readmore'>Read More</a>"
        else:
            return ""

    def title_pretty(self):
        return self.title.replace("\\'","\'")

    def firstaired_pretty(self):
        return self.firstaired.strftime('%M')

    def audience_icon_letter(self):
        if self.audience:
            return "<span class='" + self.audience.lower() + "'>" + self.audience[0] + "</span> "
        else:
            return ""

    def audience_icon(self):
        if self.audience:
            return "<i class='fa fa-user-circle " + self.audience.lower() + "' aria-hidden='true'></i> "
        else:
            return ""
        
    class Meta:
        db_table = 'shows_series'

class Episode(models.Model):
    series = models.ForeignKey(Series, related_name='sid', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=200)
    season = models.IntegerField()
    episode = models.IntegerField()
    serid = models.IntegerField()
    seaid = models.IntegerField()
    epiid = models.IntegerField()
    rssid = models.IntegerField(null=True,blank=True)
    rssdate = models.DateTimeField(null=True,blank=True)
    desc = models.TextField()
    date_added = models.DateTimeField()
    due = models.DateTimeField()
    link = models.TextField()
    downloaded = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return  '{0} S:{1} E{2} Due {3}'.format(self.title.replace("\\'","\'"),self.season,self.episode,self.due)

    def title_pretty(self):
        return self.title.replace("\\'","\'")

    def tvdblink(self):
        return "http://www.thetvdb.com/?tab=episode&seriesid={0}&seasonid={1}&id={2}&lid=7".format(self.serid,self.seaid,self.epiid)

    def tvdbslink(self):
        return "http://www.thetvdb.com/?tab=season&seriesid={0}&seasonid={1}&lid=7".format(self.serid,self.seaid)

    def imdblink(self):
        return "http://www.imdb.com/title/{0}/episodes?season={1}".format(self.rsskey.imdb,self.season)

    def due_plus(self):
        return self.due + timedelta(days=1)

    def thumb(self):
        return "/shows/img/fart/{0}.jpg".format(self.serid)

    def banner(self):
        return "/shows/img/bart/{0}.jpg".format(self.serid)

    def due_pretty(self):
        dayadded = self.due + timedelta(days=1)
        if timezone.now().year == dayadded.year:
            return dayadded.strftime('%A %b %e')
        else:
            return dayadded.strftime('%b %e %Y')

    def date_added_pretty(self):
        return self.date_added.strftime('%b %e %Y')

    def downloaded_pretty(self):
        if self.downloaded is not None and self.downloaded > dt_1000:
            return self.downloaded.strftime('%b %e %Y')
        else:
            return 'No'

    def rssdate_pretty(self):
        return self.rssdate.strftime('%b %e %Y')

    def episode_detail(self):
        if self.season == 0:
            return 'Special'
        else:
            return 'S:{0} E:{1}'.format(self.season,self.episode)

    class Meta:
        ordering = ('-season','-episode')
        db_table = 'shows_episodes'


class Media(models.Model):
    title = models.CharField(max_length=200)
    seotitle = models.CharField(max_length=200,unique=True)
    overview = models.TextField(null=True,blank=True)
    turl = models.URLField()
    datestr = models.DateTimeField()
    episode = models.IntegerField(default=0)
    certCHOICES = (
        ("U","U"),
        ("PG","PG"),
        ("12","12"),
        ("12A","12A"),
        ("PG-13","PG-13"),
        ("15","15"),
        ("18","18")
    )
    cert = models.CharField(max_length=200,choices=certCHOICES,default='18')
    typCHOICES = (('movie', 'Movie',), ('tv', 'TV',), ('book', 'Book',))
    typ = models.CharField(max_length=100,choices=typCHOICES,default='movie')
    gotCHOICES = ((0,'No'),(1,'Yes'))
    got = models.IntegerField(default=0,choices=gotCHOICES)
    banner = models.ImageField(upload_to='shows/mart/',null=True,blank=True)

    def __str__(self):
        return self.title

    def datestr_pretty(self):
        return self.datestr.strftime('%b %e %Y')

    def poster(self):
        return "/shows/img/mart/{0}.jpg".format(self.id)

    def certimg(self):
        return "shows/img/pegi/{0}.png".format(self.cert.lower())

    class Meta:
        db_table = 'shows_movies'