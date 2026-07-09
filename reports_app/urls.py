from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='reports_dashboard'),
    path('attendance/', views.attendance_report, name='attendance_report'),
    path('exam/', views.exam_report, name='exam_report'),
    path('fee/', views.fee_report, name='fee_report'),
    path('predictor/', views.academic_predictor, name='academic_predictor'),
    path('predictor/<int:student_id>/', views.academic_predictor, name='academic_predictor_detail'),
    path('transcript/', views.download_transcript, name='download_student_transcript'),
    path('transcript/<int:student_id>/', views.download_transcript, name='download_transcript'),
]
