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
    print(request.user)
    posts = requests.get('http://localhost:8000/api/posts/').json()
    return render(request, 'headers.html', context={'posts':posts})

def signin(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user == None:
            messages.add_message(request, messages.ERROR, 'Invalid Credentials!')
            print('Invalid Credentials!')
            return render(request, 'signin.html')
        login(request, user)
        print('Logged in', request.user.username)
        return redirect('/')
    return render(request, 'signin.html')

def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(username=request.POST['username'], email=request.POST['email'], password=request.POST['password'])
        user.first_name = request.POST['firstname']
        user.last_name = request.POST['lastname']
        user.save()
        print('Account created for',user.username)
        return redirect('/signin/')
    return render(request, 'register.html')

def signout(request):
    logout(request)
    return redirect('/signin/')

def analyze(request):
    if request.method == 'POST':
        post = Post.objects.create(image=request.FILES['image_file'], tag=request.POST['tags'], user=request.user)
        res = requests.post('http://localhost:8000/api/analyze/', {"post_id": post.id})
        print(res)
        return render(request, 'submitted.html')
    return render(request, 'analysis.html')

def history(request):
    posts = requests.get('http://localhost:8000/api/posts/').json()
    filtered_posts=[]
    for post in posts:
        if post['user']==request.user.id:
            filtered_posts.append(post)
    return render(request, 'history.html', context={'posts':filtered_posts})

def accountinfo(request):
    return render(request, 'account.html')

def search(request):
    if 'keyword' in request.GET and request.GET['keyword'].strip() != '':
        res = Post.objects.filter(tag__icontains=request.GET['keyword'])
        posts = [PostSerializer(x).data for x in res]
        if len(posts) == 0:
            return render(request, 'search.html', context={'notfound':True})
        return render(request, 'search.html', context={'posts':posts})
    return render(request, 'search.html')