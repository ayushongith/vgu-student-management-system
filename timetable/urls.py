from django.urls import path
from . import views

urlpatterns = [
    path('', views.timetable_list, name='timetable_list'),
    path('create/', views.timetable_create, name='timetable_create'),
    path('<int:pk>/edit/', views.timetable_update, name='timetable_update'),
    path('<int:pk>/delete/', views.timetable_delete, name='timetable_delete'),
]
