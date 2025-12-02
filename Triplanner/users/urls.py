# users/urls.py

from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register_user, name="register-user"),
    path('login/', login_user, name="login-user"),
    path('<int:user_id>/counts/', user_follow_counts, name='user-follow-counts'),
    path('send_follow_request/', send_follow_request, name='send_follow_request'),
    path('list_all_follow_requests/', list_all_follow_requests, name='list_all_follow_requests'),
    path('manage_follow_request/', manage_follow_request, name='manage_follow_request'),
    path("unfollow/", unfollow_user),
    path("search_users/",search_users,name='search_users'),
    path("notification_read/",notification_read,name='search_users'),
    path("get_all_notify/",get_all_notify,name="get_all_notify")

]
