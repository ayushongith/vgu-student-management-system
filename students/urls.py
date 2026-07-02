from django.urls import path
from . import views

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('<int:pk>/', views.student_detail, name='student_detail'),
    path('<int:pk>/edit/', views.student_update, name='student_update'),
    path('<int:pk>/delete/', views.student_delete, name='student_delete'),
    path('my/attendance/', views.my_attendance, name='my_attendance'),
    path('my/marks/', views.my_marks, name='my_marks'),
    path('my/timetable/', views.my_timetable, name='my_timetable'),
    path('my/assignments/', views.my_assignments, name='my_assignments'),
    path('export/csv/', views.export_students_csv, name='export_students_csv'),
]
