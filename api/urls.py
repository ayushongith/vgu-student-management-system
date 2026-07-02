from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    StudentViewSet, TeacherViewSet, DepartmentViewSet,
    CourseViewSet, SubjectViewSet, AttendanceViewSet,
    ExamViewSet, MarksViewSet, TimetableViewSet,
    AssignmentViewSet, NoticeViewSet, FeePaymentViewSet
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

router = DefaultRouter()
router.register('students', StudentViewSet)
router.register('teachers', TeacherViewSet)
router.register('departments', DepartmentViewSet)
router.register('courses', CourseViewSet)
router.register('subjects', SubjectViewSet)
router.register('attendance', AttendanceViewSet)
router.register('exams', ExamViewSet)
router.register('marks', MarksViewSet)
router.register('timetable', TimetableViewSet)
router.register('assignments', AssignmentViewSet)
router.register('notices', NoticeViewSet)
router.register('fees', FeePaymentViewSet)

schema_view = get_schema_view(
    openapi.Info(title='Student Management System API', default_version='v1'),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api_docs'),
]
