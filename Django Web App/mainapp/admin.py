from django.contrib import admin
from mainapp.models import *

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserVoteDetails)