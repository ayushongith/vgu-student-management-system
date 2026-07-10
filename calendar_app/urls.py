from django.urls import path
from . import views


urlpatterns = [
    path('', views.calendar_view, name='academic_calendar'),
    path('events/', views.get_calendar_events, name='get_calendar_events'),
    path('events/create/', views.create_event, name='create_calendar_event'),
]
