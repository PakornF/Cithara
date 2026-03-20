from django.urls import path
from . import views

urlpatterns = [
    # Users
    path('users/', views.user_list, name='user-list'),
    path('users/<int:pk>/', views.user_detail, name='user-detail'),

    # Songs
    path('songs/', views.song_list, name='song-list'),
    path('songs/<int:pk>/', views.song_detail, name='song-detail'),

    # Generation Requests
    path('requests/', views.request_list, name='request-list'),
    path('requests/<int:pk>/', views.request_detail, name='request-detail'),

    # Share Links
    path('share/<str:token>/', views.shared_song, name='shared-song'),

    # Feedback
    path('feedback/', views.feedback_list, name='feedback-list'),
]
