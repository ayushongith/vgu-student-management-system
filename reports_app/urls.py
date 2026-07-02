from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('exam/', views.exam_report, name='exam_report'),
    path('fee/', views.fee_report, name='fee_report'),
]
