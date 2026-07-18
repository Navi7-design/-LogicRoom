from django.urls import path
from . import views
from django.conf import settings


urlpatterns = [
    path('', views.index, name='index'),
    path("posts/create/", views.create_post, name="create_post"),
    path('posts/', views.posts_page, name='posts'),
    path('posts/detail/<int:post_id>/', views.post_detail, name='post_detail'),
    path("comment/<int:comment_id>/vote/<str:value>/", views.vote_comment, name="vote_comment"),    
    path('comment/delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path("comment/<int:pk>/edit/",views.edit_comment,name="edit_comment"),
    path("post/<int:post_id>/rate/<int:value>/", views.rate_post, name="rate_post"),
    path('posts/category/<slug:slug>/', views.posts_page, name='posts_by_category'),
    path("profile/<str:username>/", views.profile_view, name="profile"),
    path('logout/', views.logout_view, name='logout'),
    path("post/delete/<int:post_id>/", views.delete_post, name="delete_post"),
    path('post/<int:pk>/edit/', views.edit_post, name='edit_post'),
    path("like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path("save/<int:post_id>/", views.toggle_save, name="toggle_save"),
    path("check-user/", views.check_user_exists, name="check_user"),
    path("follow/<str:username>/", views.follow_user, name="follow_user"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/open/<int:notification_id>/", views.open_notification, name="open_notification"),
    path("notifications/delete/<int:notification_id>/", views.delete_notification, name="delete_notification"), 
    path("save-social-link/",views.save_social_link,name="save_social_link"),
    path("support/", views.support_page, name="support"),
    path("<str:username>/connections/",views.followers_page,name="followers_page",),
]

