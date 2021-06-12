from django.urls import path
from .views import Register, Login, UserView, PostView, LikeView, PopularView

urlpatterns = [
    path('register', Register.as_view()),
    path('login', Login.as_view()),
    path('user', UserView.as_view()),
    path('post', PostView.as_view()),
    path('post/<int:id>/like', LikeView.as_view()),
    path('users/popular', PopularView.as_view()),
]