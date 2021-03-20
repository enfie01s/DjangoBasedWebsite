from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
#from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, datetime, time, timedelta
from .models import Post
from .forms import PostForm
from django.conf import settings
import os

def home(request):
    posts = Post.objects.order_by('-pub_date')
    return render(request,'blog/home.html',{'posts':posts})

def blog_post(request,year,month,day,seotitle):
    pdate = date(int(year),int(month),int(day))
    daystart = timezone.make_aware(datetime.combine(pdate, time.min))
    dayend = timezone.make_aware(datetime.combine(pdate, time.max))
    post = get_object_or_404(Post, seotitle=seotitle,pub_date__range=(daystart,dayend))
    return render(request,'blog/blog_post.html',{'post':post})

@login_required
def manage(request,pk=''):
    if pk is not None and len(pk) > 0:
        post = get_object_or_404(Post,pk=pk) 
    else:
        post = Post()

    if request.method == 'POST':
        error = ''
        form = PostForm(request.POST,request.FILES,instance=post,label_suffix='')

        # DELETE THE POST       
        if 'deleterow' in request.POST:
            if form.image is not None:
                try:
                    os.remove(settings.BASE_DIR + os.path.normpath(post.image.url))
                except:
                    error = 'could not delete file'
            post.delete()
            return redirect('blog:home')

        # ADD/EDIT THE POST
        datestring = datetime.strptime(request.POST['pub_date'], '%d/%m/%Y')
        if form.is_valid():
            obj = form.save(commit=False)
            obj.pub_date = timezone.make_aware(datetime.combine(datestring, time.min))
            #obj.author = request.user
            obj.save()
            if 'save' in request.POST:
                return redirect('blog:home')
        else:
            error = 'Please fill in all fields.'
        return render(request,'blog/create.html',{'error':error,'form':form,'pk':pk})
    else:
        form = PostForm(instance=post,label_suffix='')
        return render(request,'blog/create.html',{'form':form,'pk':pk})