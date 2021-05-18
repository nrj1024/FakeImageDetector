from django.urls import path, include
from rest_framework import routers
from mainapp.views import *

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/', Analyze.as_view()),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('toptags/', TopTags.as_view())
]