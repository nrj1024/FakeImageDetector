from django.urls import path, include
from rest_framework import routers
from mainapp.views import *

router = routers.DefaultRouter()
router.register(r'posts', PostViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'uservotedetails', UserVoteDetailsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('analyze/', Analyze.as_view()),
    path('login/', Login.as_view()),
    path('logout/', Logout.as_view()),
    path('register/', Register.as_view()),
    path('toptags/', TopTags.as_view()),
    path('saveupvotes/', SaveUpvotes.as_view()),
    path('savedownvotes/', SaveDownvotes.as_view())
]