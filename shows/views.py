from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.shortcuts import render, get_object_or_404, redirect
from django.core.files.storage import FileSystemStorage
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.decorators import permission_required, login_required
from django.http import JsonResponse
from django.db.models import Q
from .models import Episode, Series, Media
from django.db.models import Count
from .forms import SeriesForm, MediaForm
from datetime import date, datetime, time, timedelta
from time import mktime
from pytvdbapi import api
import feedparser
import re
import urllib.request
import os

'''
TODO:
---
Styling - try for flex to share space with columns
permissions
hover show display details in popup (including last seen episode and last inserted episode)
button to hide all shows not your own/universal
display relative weekday headers instead of the day name?
page to display all shows in case they aren't on any page (this happens if they were ticked today and thus not in this week's list but also not on a break).
Page for all shows and order by status (active/on break/inactive).
'''

cache.clear()
dt_1000 = timezone.make_aware(datetime(1000,1,1,0,0,0))

#@permission_required('shows.series.can_edit')
@login_required
@never_cache
def home(request):
    today = date.today()
    dt_today = timezone.make_aware(datetime.combine(today, time.min))
    dt_yesterday = timezone.make_aware(datetime.combine(today - timedelta(days=1), time.min))
    dt_tomorrow = timezone.make_aware(datetime.combine(today + timedelta(days=1), time.min))
    dt1 = timezone.make_aware(datetime.combine(today + timedelta(days=6), time.max))
    dt2 = timezone.make_aware(datetime.combine(today - timedelta(days=14), time.min))
    err=''
    # UPDATE EPISODES #
    try:
        tvdb()
    except:
        err = 'TVDB not available to update shows.'

    # CREATE DICTIONARIES #
    weekdays = [dt_yesterday + timedelta(days=x+1) for x in range((dt1-dt_yesterday).days)]
    thisweek = Episode.objects.filter(due__range=(dt_yesterday, dt1)).filter(downloaded__lte=dt_1000).exclude(season=0).order_by('-due','title')
    errors = Episode.objects.filter(due__lt=dt_yesterday).filter(due__gt=dt2).filter(downloaded__lte=dt_1000).exclude(season=0).order_by('-due','title')
    dltoday = Episode.objects.filter(downloaded__range=(dt_today,dt_tomorrow))
    dltodaytext = ''

    if dltoday:
        dltodaytext = '<b>Downloaded Today</b><br>'
    for dlt in dltoday:
        dltodaytext += str(dlt.title_pretty()) + '&nbsp;' + str(dlt.episode_detail()) + '<br>'

    # GET LINKS FROM SHOWSRSS #
    for epi in errors:
        rsslink(epi)
    for epi1 in thisweek:
        rsslink(epi1)

    return render(request,'shows/home.html',{
        'weekdays': weekdays,
        'thisweek': thisweek,
        'dltoday': dltodaytext,
        'errors': errors,
        'err': err
        })

@login_required
def series(request,seotitle):
    today = date.today()
    dt_today = timezone.make_aware(datetime.combine(today, time.min))
    show = Series.objects.get(seotitle=seotitle)

    seasonDict = {}
    for epi in show.sid.all():
        if epi.season > 0:
            if epi.downloaded is not None and epi.downloaded <= dt_1000:
                rsslink(epi)
            if epi.season not in seasonDict:
                seasonDict[epi.season] = {}
            seasonDict[epi.season][epi.episode] = {
            'episod':epi.id,
            'due':epi.due_pretty,
            'downloaded':epi.downloaded_pretty,
            'desc':epi.desc,
            'tvdb':epi.tvdblink,
            'tvdbs':epi.tvdbslink,
            'link':epi.link
            }
            if epi.due > dt_today:
                seasonDict[epi.season][epi.episode]['future'] = ' faded'
            else:
                seasonDict[epi.season][epi.episode]['future'] = ''
    return render(request,'shows/show_detail.html',{'show':show,'seasons':seasonDict})

@login_required
def manage(request,seotitle):
    if seotitle:
        show = get_object_or_404(Series,seotitle=seotitle)
    else:
        show = Series()

    if request.method == 'POST':
        form = SeriesForm(request.POST,instance=show,label_suffix='')
        if seotitle is not None and 'deleteshow' in request.POST:
            try:
                module_dir = os.path.dirname(__file__)  # get current directory
                os.remove(os.path.join(module_dir, os.path.normpath('static/shows/img/bart/{0}.jpg').format(show.tvdbid)))
                os.remove(os.path.join(module_dir, os.path.normpath('static/shows/img/fart/{0}.jpg').format(show.tvdbid)))
            except:
                error = 'could not delete file'
            Episode.objects.filter(series=show).delete()
            show.delete()
            return redirect('shows:home')
        if form.is_valid():
            #self.cleaned_data - not needed in modelforms
            obj = form.save(commit=False)
            obj.lastlookup = dt_1000
            obj.save()

            if(seotitle is None):
                tvdb(obj.id)
            seotitle = obj.seotitle
            if 'save' in request.POST:
                return redirect('shows:series', seotitle=seotitle)
    else:
        form = SeriesForm(instance=show,label_suffix='')
    if(seotitle):# Here we are editing
        data = {
        'head':"Editing " + seotitle,
        'urlstuff': seotitle
        }
    else:# Here we are adding
        data = {
        'head':"Add New Show",
        'urlstuff': ''
        }

    return render(request,'shows/manage.html',{'data':data,'form':form})

@never_cache
def onbreak(request):
    #series where no episodes this week
    today = date.today()
    dt_today = timezone.make_aware(datetime.combine(today, time.min))
    dt_yesterday = timezone.make_aware(datetime.combine(today - timedelta(days=1), time.min))
    dt1 = timezone.make_aware(datetime.combine(today + timedelta(days=6), time.max))
    thisweek = Episode.objects.filter(due__range=(dt_yesterday, dt1)).exclude(series_id=None).exclude(season=0).order_by('-due','title').select_related('series').values_list('series_id',flat=True)

    # series with no episodes this week
    onbreakq = Episode.objects.exclude(series_id__in=thisweek).exclude(due__lt=dt_today).exclude(season=0).order_by('due','title').select_related('series')
    onbreak = {}
    for ob in onbreakq:
        if ob.series.seotitle not in onbreak:
            onbreak[ob.series.seotitle] = {
            'title':ob.series.title_pretty,
            'overview':ob.series.overview,
            'audience':ob.series.audience,
            'banner':ob.series.banner_img,
            'rsslink':ob.series.rsslink,
            'imdblink':ob.series.imdblink,
            'tvdblink':ob.series.tvdblink,
            'due':ob.due_pretty,
            'detail':ob.episode_detail
            }

    upcomingepi = Episode.objects.filter(due__gte=dt_today).exclude(series_id=None).values_list('series_id',flat=True)
    print(upcomingepi)

    inactive = Series.objects.exclude(pk__in=upcomingepi).extra(select={'firstair': 'MONTH(firstaired)'},order_by=['firstair'])
    return render(request,'shows/onbreak.html',{'onbreak':onbreak,'inactive':inactive})


def managemovie(request,seotitle=''):
    if seotitle:
        media = get_object_or_404(Media, seotitle=seotitle)
    elif seotitle is None:
        media = Media()

    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES,instance=media,label_suffix='')

        # DELETE THE ENTRY
        if seotitle is not None and 'deletemovie' in request.POST and media.banner is not None:
            try:
                os.remove(settings.BASE_DIR + os.path.normpath(media.banner.url))
            except:
                error = 'could not delete file'
            media.delete()
            return redirect('shows:movies')

        # SAVE THE ENTRY
        datestring = datetime.strptime(request.POST['datestr'], '%d/%m/%Y')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.datestr = timezone.make_aware(datetime.combine(datestring, time.min))
            obj.save()
        seotitle = media.seotitle
        if 'save' in request.POST:
            return redirect('shows:movies')
    else:
        form = MediaForm(instance=media,label_suffix='')
    return render(request,'shows/managemovie.html',{'data':media,'form':form})

def movies(request):
    today = date.today()
    dt_today = timezone.make_aware(datetime.combine(today, time.min))
    movies = Media.objects.order_by('got','datestr')
    released = {}
    upcoming = {}
    for movie in movies:
        data = {
        'title':movie.title,
        'seotitle':movie.seotitle,
        'date':movie.datestr_pretty,
        'typ':movie.typ,
        'overview':movie.overview,
        'turl':movie.turl,
        'got':movie.got,
        'banner':movie.banner,
        'id':movie.id
        }
        if movie.got == 1:
            data['fade'] = ' faded'
        else:
            data['fade'] = ''
        if movie.cert is not None and movie.cert != '':
            data['certimg']=movie.certimg
        if movie.datestr > dt_today:
            if movie.typ.lower() not in upcoming:
                upcoming[movie.typ.lower()] = []
            upcoming[movie.typ.lower()].append(data)
        else:
            if movie.typ.lower() not in released:
                released[movie.typ.lower()] = []
            released[movie.typ.lower()].append(data)

    return render(request,'shows/movies.html',{'released':released,'upcoming':upcoming})
'''
UTILIY METHODS
'''

def rsslink(epis):
    epi = Episode.objects.get(pk=epis.pk)
    sea=str(epi.season).zfill(2)
    ep=str(epi.episode).zfill(2)
    thislink = epi.link
    today = date.today()
    thisdate = timezone.make_aware(datetime.combine(today, time.min))
    xml = feedparser.parse("http://showrss.info/show/{0}.rss".format(epi.series.rssfeedid))
    if xml:
        for item in xml.entries:
            if item.link:
                hd1080 = 0
                se = re.search( r'S([\d]{2})E([\d]{2})', item.tv_raw_title, re.I)
                if se and int(se.group(1)) > 0 and int(se.group(1)) == int(sea) and int(se.group(2)) == int(ep):
                    hd = re.search( r'(720p)', item.tv_raw_title, re.I)
                    hd1 = re.search( r'(1080p)', item.tv_raw_title, re.I)
                    if thislink == '':
                        thislink = item.link
                    elif hd1:# allow a second pass to collect 1080p link if possible
                        thislink = item.link
                        hd1080 = 1
                    elif hd1080 == 0 and hd:# allow a third pass to collect 720p link if needed
                        thislink = item.link
                    thisdate = timezone.make_aware(datetime.fromtimestamp(mktime(item.published_parsed)))
                    epi.rssdate = thisdate
                    epi.link = thislink
                    if epi.downloaded is None:
                        epi.downloaded = dt_1000
                    epi.save()

def tvdb(showid=''):
    today = date.today()
    dt_today = timezone.make_aware(datetime.combine(today, time.min))
    dt0 = timezone.make_aware(datetime.combine(today - timedelta(days=2), time.min))
    dt1 = timezone.make_aware(datetime.combine(today - timedelta(days=30), time.min))
    dt3 = timezone.make_aware(datetime.combine(today - timedelta(days=500), time.min))

    module_dir = os.path.dirname(__file__)  # get current directory

    db = api.TVDB("D620620B2C727377", banners=True)
    if showid:
        series = { Series.objects.get(pk=showid) }
    else:
        series = Series.objects.filter(lastlookup__lt=dt0)

    for show in series:
        result = db.search(show.title,"en")
        tvdbshow = result[0]
        #['FirstAired', 'IMDB_ID', 'Network', 'Overview', 'SeriesName', 'actor_objects', 'api', 'banner', 'banner_objects', 'id', 'lang', 'language', 'seriesid', 'zap2it_id']
        lastDue = timezone.make_aware(datetime.combine(tvdbshow.FirstAired, time.min))
        lastEpi = '1x1'
        for tvdbseason in tvdbshow:#['season_number', 'show']
            for tvdbepi in tvdbseason:
                #['Combined_episodenumber', 'Combined_season', 'DVD_chapter', 'DVD_discid', 'DVD_episodenumber', 'DVD_season', 'Director', 'EpImgFlag', 'EpisodeName', 'EpisodeNumber', 'FirstAired', 'GuestStars', 'IMDB_ID', 'Language', 'Overview', 'ProductionCode', 'Rating', 'RatingCount', 'SeasonNumber', 'Writer', 'absolute_number', 'filename', 'id', 'is_movie', 'lastupdated', 'season', 'seasonid', 'seriesid', 'thumb_added', 'thumb_height', 'thumb_width']

                Episode.objects.filter(due__lte=dt3).delete()# delete old episodes
                try:
                    AiredDT = timezone.make_aware(datetime.combine(tvdbepi.FirstAired, time.min))
                except:
                    AiredDT = None
                if AiredDT is not None and AiredDT > dt1:
                    try:
                        dupe = Episode.objects.get(season=tvdbepi.SeasonNumber,episode=tvdbepi.EpisodeNumber,serid=tvdbshow.id)
                    except:
                        dupe = None
                    if dupe is None:
                        print("Adding {0} S{1}E{2}, date {3}".format(tvdbshow.SeriesName,tvdbepi.SeasonNumber,tvdbepi.EpisodeNumber,tvdbepi.FirstAired))
                        new = Episode()
                        new.title = tvdbshow.SeriesName
                        new.season = tvdbepi.SeasonNumber
                        new.episode = tvdbepi.EpisodeNumber
                        new.date_added = dt_today
                        new.due = AiredDT
                        new.desc = tvdbepi.Overview
                        new.serid = tvdbshow.id
                        new.epiid = tvdbepi.id
                        new.seaid = tvdbepi.seasonid
                        new.series_id = show.id
                        new.rssdate = dt_1000
                        new.downloaded = dt_1000
                        new.save()
                    elif dupe.due != AiredDT:
                        print("Updating {0} S{1}E{2}, date {3}".format(tvdbshow.SeriesName,tvdbepi.SeasonNumber,tvdbepi.EpisodeNumber,tvdbepi.FirstAired))
                        dupe.date_added = dt_today
                        dupe.due = AiredDT
                        dupe.desc = tvdbepi.Overview
                        dupe.serid = tvdbshow.id
                        dupe.epiid = tvdbepi.id
                        dupe.seaid = tvdbepi.seasonid
                        dupe.series_id = show.id
                        if dupe.rssdate is None:
                            dupe.rssdate = dt_1000
                        if dupe.downloaded is None:
                            dupe.downloaded = dt_1000
                        dupe.save()
                if AiredDT is not None:
                    lastDue = AiredDT
                    lastEpi = str(tvdbepi.SeasonNumber) + 'x' + str(tvdbepi.EpisodeNumber)

        show.lastlookup=dt_today
        show.tvdbid=tvdbshow.id
        show.overview=tvdbshow.Overview
        #show.period=tvdbshow.FirstAired.strftime('%b')
        show.firstaired=timezone.make_aware(datetime.combine(tvdbshow.FirstAired, time.min))
        show.lastdue = timezone.make_aware(datetime.combine(lastDue, time.min))
        show.lastepi = lastEpi
        show.imdb=tvdbshow.IMDB_ID
        show.save()

        # fanart - these require collectstatic. TODO: change to use media folder!
        file_path = os.path.join(module_dir, os.path.normpath('static/shows/img/fart/{0}.jpg').format(tvdbshow.id))
        if os.path.isfile(file_path) == False:
            try:
                filemessage = 'Getting Fan Art File: ' + file_path
                urllib.request.urlretrieve("http://www.thetvdb.com/banners/fanart/original/{0}-1.jpg".format(tvdbshow.id), file_path)
            except:
                filemessage = None
            if filemessage is not None:
                print(filemessage)
        # banner
        file_path = os.path.join(module_dir, os.path.normpath('static/shows/img/bart/{0}.jpg').format(tvdbshow.id))
        if os.path.isfile(file_path) == False:
            try:
                filemessage = 'Getting Banner File: ' + file_path
                urllib.request.urlretrieve("http://www.thetvdb.com/banners/{0}".format(tvdbshow.banner), file_path)
            except:
                filemessage = None
            if filemessage is not None:
                print(filemessage)

@login_required
def dl(request):
    if request.method == 'POST' and request.is_ajax():
        epi = request.POST.get('epi')
        episode = Episode.objects.get(pk=epi)
        episode.downloaded = timezone.now()
        #if episode.rssdate is None:
        #    episode.rssdate = dt_1000
        episode.save()
        data = {'downloaded': ', <b>Downloaded:</b> ' + episode.downloaded_pretty(),'id': epi}
        return JsonResponse(data)

@login_required
def dlm(request):
    if request.method == 'POST' and request.is_ajax():
        movid = request.POST.get('id')
        mov = Media.objects.get(pk=movid)
        mov.got = 1
        mov.save()
        data = {'id': movid}
        return JsonResponse(data)

'''
            if 'deletefile' in request.POST or 'banner' in request.FILES and media.banner is not None:
                try:
                    os.remove(settings.BASE_DIR + os.path.normpath(media.banner.url))
                    obj.banner = None
                except:
                    error = 'could not delete file'

            if 'banner' in request.FILES:
                obj.banner = request.FILES['banner']
            '''
'''
    {
    'title': 'Shadowhunters 2x14 The Fair Folk',

    'title_detail': {'type': 'text/plain', 'language': None, 'base': 'http://showrss.info/show/438.rss', 'value': 'Shadowhunters 2x14 The Fair Folk'},

    'link': 'magnet:?xt=urn:btih:AFB6BE15925904C4FDE36702E9638D4CA0EF460B&dn=Shadowhunters+S02E14+WEBRip+x264+RARBG&tr=udp%3A%2F%2Ftracker.coppersurfer.tk%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.leechers-paradise.org%3A6969%2Fannounce&tr=udp%3A%2F%2Ftracker.opentrackr.org%3A1337%2Fannounce&tr=http%3A%2F%2Ftracker.trackerfix.com%3A80%2Fannounce',

    'published': 'Tue, 27 Jun 2017 18:10:05 +0000',

    'published_parsed': time.struct_time(tm_year=2017, tm_mon=6, tm_mday=27, tm_hour=18, tm_min=10, tm_sec=5, tm_wday=1, tm_yday=178, tm_isdst=0),

    'tv_show_id': '438',

    'tv_show_name': 'Shadowhunters',

    'tv_episode_id': '38932',

    'tv_raw_title': 'Shadowhunters S02E14 WEBRip x264 RARBG',
    }


'''
