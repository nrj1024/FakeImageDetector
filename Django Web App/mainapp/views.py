from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status, viewsets, filters
from mainapp.models import *
from mainapp.serializers import *
from mainapp.NeuralNets import initClassifier, initSegmenter
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

def convert_to_ela_image(path, quality,intensity=None):
    filename = path
    resaved_filename = settings.BASE_DIR.as_posix()+settings.MEDIA_URL+'tempresaved.jpg'
    
    im = Image.open(filename).convert('RGB')
    im.save(resaved_filename, 'JPEG', quality = quality)
    resaved_im = Image.open(resaved_filename)
    
    ela_im = ImageChops.difference(im, resaved_im)
    
    extrema = ela_im.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    if intensity==None:
        ela_im = ImageEnhance.Brightness(ela_im).enhance(scale)
    else:
        ela_im = ImageEnhance.Brightness(ela_im).enhance(intensity)
    return  ela_im

def classify(file_path):
    classifier=initClassifier()
    #classifier.load_weights('/static/classifier_weights.h5') #Will find files in STATIC_ROOT
    classifier.load_weights(settings.BASE_DIR.as_posix()+'/AI_models/classifier_weights.h5')
    testimg=convert_to_ela_image(file_path, 90).resize((256,256))
    test=np.array(testimg)/255
    test=test.reshape(-1,256,256,3)
    result=classifier.predict(test)
    realp = round(result[0][0],3)
    fakep = round(result[0][1],3)
    return (realp, fakep)

def segment(file_path):
    segmenter=initSegmenter()
    segmenter.load_weights(settings.BASE_DIR.as_posix()+'/AI_models/segmenter_weights.h5')
    testimg=convert_to_ela_image(file_path,90).resize((256,256))
    testimg=testimg.getchannel('B')
    test=np.array(testimg)/np.max(testimg)
    test=test.reshape(-1,256,256,1)
    mask=segmenter.predict(test)
    mask=mask.reshape(256,256)
    mask=(mask*255).astype('uint8')
    im = Image.fromarray(mask)
    original_size = Image.open(file_path).size
    im = im.resize(original_size)
    file_name = file_path.split('/')[-1][:-4]
    sub_path = 'binary_masks/'+file_name+'_segmentation.jpg'
    segmntn_path = settings.BASE_DIR.as_posix()+settings.MEDIA_URL+sub_path
    im.save(segmntn_path)
    return sub_path

class Analyze(APIView):
    def post(self, request):
        postid = request.data['post_id']
        cur_post = Post.objects.get(pk=postid)
        image_path = settings.BASE_DIR.as_posix()+settings.MEDIA_URL+str(cur_post.image)
        cur_post.p_real, cur_post.p_fake = classify(image_path)
        cur_post.binary_mask = segment(image_path)
        cur_post.save()
        return Response(PostSerializer(cur_post).data)

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_on', 'votes']

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.AllowAny]

class UserVoteDetailsViewSet(viewsets.ModelViewSet):
    queryset = UserVoteDetails.objects.all()
    serializer_class = UserVoteDetailsSerializer
    permission_classes = [permissions.AllowAny]

class Login(APIView):
    def post(self, request):
        user = authenticate(username=request.data['username'], password=request.data['password'])
        cur_token = Token.objects.filter(user=user).first()
        if cur_token != None:
            cur_token.delete()
        token = Token.objects.create(user=user)
        return Response({'token':token.key})

class Logout(APIView):
    def post(self,request):
        cur_token = Token.objects.get(key=request.data['token'])
        cur_token.delete()
        return Response({'status':'Successfully Logged out'})

class Register(APIView):
    def post(self, request):
        new_user = User.objects.create_user(username=request.data['username'], email=request.data['email'],
                                            password=request.data['password'])
        #new_user.is_active = True      #True by default | maybe supply false and make it true after email verification
        new_user.first_name = request.data['first_name']
        new_user.last_name = request.data['last_name']
        new_user.save()
        UserVoteDetails.objects.create(user=new_user)
        return Response({'status': 'Successfully registered new user'})

class TopTags(APIView):
    def get(self, request):
        posts = Post.objects.all()
        tags = ''
        for post in posts:
            tags = tags+post.tag+','
        atags = [x.strip() for x in tags.split(',')][:-1]
        s_tags = sorted(atags, key = atags.count, reverse=True)
        top_tags = list(dict.fromkeys(s_tags))
        return Response(top_tags[:15])

class SaveUpvotes(APIView):
    def post(self, request):
        relation = UserVoteDetails.objects.get(user = request.data['user_id'])
        post = Post.objects.get(id = request.data['post_id'])
        relation.upvoted_posts.add(post)
        post.votes = request.data['updated_votes']
        post.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        relation = UserVoteDetails.objects.get(user__id = request.data['user_id'])
        post = Post.objects.get(id = request.data['post_id'])
        relation.upvoted_posts.remove(post)
        post.votes = request.data['updated_votes']
        post.save()
        return Response(status=status.HTTP_200_OK)

class SaveDownvotes(APIView):
    def post(self, request):
        relation = UserVoteDetails.objects.get(user__id = request.data['user_id'])
        post = Post.objects.get(id = request.data['post_id'])
        relation.downvoted_posts.add(post)
        post.votes = request.data['updated_votes']
        post.save()
        return Response(status=status.HTTP_200_OK)

    def delete(self, request):
        relation = UserVoteDetails.objects.get(user__id = request.data['user_id'])
        post = Post.objects.get(id = request.data['post_id'])
        relation.downvoted_posts.remove(post)
        post.votes = request.data['updated_votes']
        post.save()
        return Response(status=status.HTTP_200_OK)
