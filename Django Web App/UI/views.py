from django.shortcuts import render, redirect
import requests
from mainapp.models import *
from mainapp.serializers import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from time import sleep
from django.template.response import TemplateResponse
from django.contrib import messages

def home(request):
    if not request.user.is_authenticated:
        return redirect('/signin/')
    if 'sort' in request.GET:
        posts = requests.get('http://localhost:8000/api/posts?ordering='+request.GET['sort']).json()
    else:
        posts = requests.get('http://localhost:8000/api/posts?ordering=votes').json()
    return render(request, 'headers.html', context={'posts':posts})

def signin(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user == None:
            messages.add_message(request, messages.ERROR, 'Invalid Credentials!')
            return render(request, 'signin.html')
        login(request, user)
        return redirect('/')
    return render(request, 'signin.html')

def register(request):
    if request.method == 'POST':
        existing_usernames = [ x.username for x in User.objects.all()]
        if request.POST['username'] in existing_usernames:
            messages.add_message(request, messages.ERROR, 'This username is taken!')
            return render(request, 'register.html')
        user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'])
        user.first_name = request.POST['firstname']
        user.last_name = request.POST['lastname']
        user.save()
        UserVoteDetails.objects.create(user=user)
        return render(request, 'registered.html')
    return render(request, 'register.html')

def signout(request):
    logout(request)
    return redirect('/signin/')

def analyze(request):
    if not request.user.is_authenticated:
        return redirect('/signin/')
    if request.method == 'POST':
        post = Post.objects.create(image=request.FILES['image_file'], tag=request.POST['tags'], user=request.user)
        res = requests.post('http://localhost:8000/api/analyze/', {"post_id": post.id})
        return render(request, 'submitted.html')
    return render(request, 'analysis.html')

def history(request):
    if not request.user.is_authenticated:
        return redirect('/signin/')
    posts = requests.get('http://localhost:8000/api/posts/').json()
    filtered_posts=[]
    for post in posts:
        if post['user']==request.user.id:
            filtered_posts.append(post)
    return render(request, 'history.html', context={'posts':filtered_posts})

def accountinfo(request):
    if not request.user.is_authenticated:
        return redirect('/signin/')
    return render(request, 'account.html')

def search(request):
    if not request.user.is_authenticated:
        return redirect('/signin/')
    if 'keyword' in request.GET and request.GET['keyword'].strip() != '':
        res = Post.objects.filter(tag__icontains=request.GET['keyword'])
        posts = [PostSerializer(x).data for x in res]
        if len(posts) == 0:
            return render(request, 'search.html', context={'notfound':True})
        return render(request, 'search.html', context={'posts':posts})
    return render(request, 'search.html')

def post(request, post_id):
    post = Post.objects.get(id = post_id)
    post = PostSerializer(post).data
    return render(request, 'post.html', context={'post':post})