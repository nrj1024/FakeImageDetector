from django.urls import path, include
from UI.views import *

urlpatterns = [
    path('', home),
    path('signin/', signin),
    path('register/', register),
    path('signout/', signout),
    path('analyze/', analyze),
    path('history/', history),
    path('account/', accountinfo),
    path('search/', search),
    path('post/<int:post_id>', post)
]