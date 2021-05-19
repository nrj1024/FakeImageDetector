from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    image = models.ImageField(upload_to='uploaded_images/')
    tag = models.CharField(max_length=40) #Charfield to make it flexible and searchable
    created_on = models.DateTimeField(auto_now=True)
    p_real = models.FloatField(null=True)
    p_fake = models.FloatField(null=True)
    binary_mask = models.ImageField(upload_to='binary_masks/', null=True)
    votes = models.IntegerField(default=0)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.CharField(max_length=500)
    created_on = models.DateTimeField(auto_now=True)

class UserVoteDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vote_details')
    upvoted_posts = models.ManyToManyField(Post, related_name='upvoted_by')
    downvoted_posts = models.ManyToManyField(Post, related_name='downvoted_by')
