from django.core import serializers
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import UserSerializer, PostSerializer
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User, Post
import jwt, datetime


class Register(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class Login(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']

        user = User.objects.filter(username = username).first()

        if user is None:
            raise AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')

        payload = {
            'id': user.user_id(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()

        # response.set_cookie(key="jwt", value=token, httponly=True)

        response.data = {
            'jwt': token
        }

        return Response(token)

def get_user_from_request(request):
    user = get_current_user(request)
    serializer = UserSerializer(user)

    return serializer.data

def get_current_user(request):
    data = request.headers['Authorization']

    if not data:
        raise AuthenticationFailed('Unauthenticated')

    token = str.replace(str(data), 'Bearer ', '')

    if not token:
        raise AuthenticationFailed('Unauthenticated')

    try:
        payload = jwt.decode(token, 'secret', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Unauthenticated')

    user = User.objects.filter(id=payload['id']).first()

    return user

class UserView(APIView):
    def get(self, request):
        data = get_user_from_request(request)
        user = get_current_user(request)
        posts = Post.objects.filter(user = user.id)
        serializer = PostSerializer(posts, many=True)
        data['posts'] = serializer.data
        return Response(data)


class PostView(APIView):
    def post(self, request):
        post_serializer = PostSerializer(data=request.data)
        post_serializer.is_valid(raise_exception=True)
        post = Post(title = post_serializer.data.get('title'), description = post_serializer.data.get('description'), user = get_current_user(request))
        post.save()
        return Response(post_serializer.data)


class LikeView(APIView):
    def post(self, request, id):
        post = Post.objects.get(pk = id)
        if not post:
            raise Exception('Post Not Found')
        post.likes += 1
        post.save()
        return Response(PostSerializer(post).data)


class PopularView(APIView):
    def get(self, request):
        users = {}
        posts = Post.objects.all()
        for post in posts:
            if post.user is None:
                continue
            if post.user.username not in users.keys():
                users[post.user.username] = post.likes
            else:
                users[post.user.username] += post.likes

        leaderboard = []
        for user in users.keys():
            leaderboard.append({"username": user, "likes": users[user]})
        leaderboard.sort(reverse=True, key=lambda u: u['likes'])
        return Response(leaderboard)