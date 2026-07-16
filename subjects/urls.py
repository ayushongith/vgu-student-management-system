from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('create/', views.subject_create, name='subject_create'),
    path('<int:pk>/edit/', views.subject_update, name='subject_update'),
    path('<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    path('electives/', views.electives_list, name='electives_list'),
    path('electives/enroll/<int:subject_id>/', views.enroll_elective, name='enroll_elective'),
    path('electives/withdraw/<int:subject_id>/', views.withdraw_elective, name='withdraw_elective'),
]
