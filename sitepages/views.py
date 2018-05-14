from django.shortcuts import render
from datetime import date, datetime, time, timedelta
from django.utils import timezone


today = date.today()
dt_today = timezone.make_aware(datetime.combine(today, time.min))
memdates = {
'Started dating': [2001,1,1,0,0,0],
'Got married': [2004,6,19,0,0,0],
'Mat quit smoking': [2013,9,27,21,0,0],#'2013-09-27 21:00:00',
'Zakynthos holiday': [2017,10,9,0,0,0],
'Christmas': [2016,12,25,0,0,0]
}

''',
'Mat Birthday':[1972,3,21,0,0,0],
'Stella Birthday':[1978,1,18,1,0,0],
'Josh Birthday':[2002,2,8,20,30,0],
'Chloe Birthday':[2000,7,7,13,0,0]
'''
# Create your views here.
def home(request):
    dates = {}
    for title,date in memdates.items():
        if title == 'Christmas':
            date[0] = int(dt_today.strftime('%Y'))
        ddate = timezone.make_aware(datetime(date[0],date[1],date[2],date[3],date[4],date[5]))  
        dates[title] = ddate
    return render(request,'sitepages/home.html',{'dates':dates})
def homepage(request):
    return render(request,'sitepages/homepage.html')