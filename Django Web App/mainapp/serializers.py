from rest_framework import serializers
from mainapp.models import *
from django.db import models
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(format='%d %b %Y %I:%M %p', read_only=True)
    user_fullname = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_on']

    def get_user_fullname(self, obj):
        return obj.user.get_full_name()

class PostSerializer(serializers.ModelSerializer):
    created_on = serializers.DateTimeField(format='%d %b %Y %I:%M %p', read_only=True)
    tag = serializers.SerializerMethodField()
    user_fullname = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    upvoted_by = serializers.SerializerMethodField()
    downvoted_by = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['created_on', 'p_real', 'p_fake', 'binary_mask', 'votes']

    def get_tag(self, obj):
        return [x.strip() for x in obj.tag.split(',')]

    def get_user_fullname(self, obj):
        return obj.user.get_full_name()

    def get_upvoted_by(self, obj):
        return [x.user.id for x in obj.upvoted_by.all()]

    def get_downvoted_by(self, obj):
        return [x.user.id for x in obj.downvoted_by.all()]

class UserVoteDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserVoteDetails
        fields = '__all__'