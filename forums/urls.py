from django.urls import path
from . import views


urlpatterns = [
    path('', views.forum_list, name='forum_list'),
    path('subject/<int:subject_id>/', views.subject_threads, name='subject_threads'),
    path('subject/<int:subject_id>/create/', views.create_thread, name='create_thread'),
    path('thread/<int:thread_id>/', views.thread_detail, name='thread_detail'),
]
