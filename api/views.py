from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .serializers import (
    StudentSerializer, TeacherSerializer, DepartmentSerializer,
    CourseSerializer, SubjectSerializer, AttendanceSerializer,
    ExamSerializer, MarksSerializer, TimetableSerializer,
    AssignmentSerializer, NoticeSerializer, FeePaymentSerializer
)
from students.models import Student
from teachers.models import Teacher
from departments.models import Department
from courses.models import Course
from subjects.models import Subject
from attendance.models import Attendance
from exams.models import Exam, Marks
from timetable.models import Timetable
from assignments.models import Assignment
from notices.models import Notice
from fees.models import FeePayment


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user.is_superuser or request.user.role == 'admin'


class IsAdminOrTeacherWrite(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_superuser or request.user.role in ['admin', 'teacher'])
        )


class IsAdminWriteOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user.is_superuser or request.user.role == 'admin'


def _teacher_for_request(request):
    return Teacher.objects.filter(user=request.user).first()


def _require_teacher_subject(request, subject):
    if request.user.is_superuser or request.user.role == 'admin':
        return
    teacher = _teacher_for_request(request)
    if not teacher or subject.teacher_id != teacher.id:
        raise PermissionDenied('You can only manage records for assigned subjects.')


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('user', 'department', 'course').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['department', 'course', 'semester', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'admission_number', 'roll_number']


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'department').all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['department', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name', 'code']


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('department').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['department', 'semester']
    search_fields = ['name', 'code']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('course', 'teacher').all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['course', 'teacher']
    search_fields = ['name', 'code']


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student__user', 'subject').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAdminOrTeacherWrite]
    filterset_fields = ['student', 'subject', 'date', 'status']
    search_fields = ['student__user__first_name']

    def perform_create(self, serializer):
        _require_teacher_subject(self.request, serializer.validated_data['subject'])
        serializer.save()

    def perform_update(self, serializer):
        subject = serializer.validated_data.get('subject', serializer.instance.subject)
        _require_teacher_subject(self.request, subject)
        serializer.save()


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('subject').all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminWriteOnly]
    filterset_fields = ['subject', 'exam_type', 'semester']


class MarksViewSet(viewsets.ModelViewSet):
    queryset = Marks.objects.select_related('student__user', 'exam').all()
    serializer_class = MarksSerializer
    permission_classes = [IsAdminOrTeacherWrite]
    filterset_fields = ['student', 'exam']
    search_fields = ['student__user__first_name']

    def perform_create(self, serializer):
        _require_teacher_subject(self.request, serializer.validated_data['exam'].subject)
        serializer.save()

    def perform_update(self, serializer):
        exam = serializer.validated_data.get('exam', serializer.instance.exam)
        _require_teacher_subject(self.request, exam.subject)
        serializer.save()


class TimetableViewSet(viewsets.ModelViewSet):
    queryset = Timetable.objects.select_related('course', 'subject', 'teacher').all()
    serializer_class = TimetableSerializer
    permission_classes = [IsAdminWriteOnly]
    filterset_fields = ['course', 'day', 'semester']


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('subject', 'teacher').all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrTeacherWrite]
    filterset_fields = ['subject', 'teacher']

    def perform_create(self, serializer):
        subject = serializer.validated_data['subject']
        _require_teacher_subject(self.request, subject)
        if self.request.user.role == 'teacher':
            serializer.save(teacher=_teacher_for_request(self.request))
        else:
            serializer.save()

    def perform_update(self, serializer):
        subject = serializer.validated_data.get('subject', serializer.instance.subject)
        _require_teacher_subject(self.request, subject)
        serializer.save()


class NoticeViewSet(viewsets.ModelViewSet):
    queryset = Notice.objects.filter(is_active=True)
    serializer_class = NoticeSerializer
    permission_classes = [IsAdminOrReadOnly]


class FeePaymentViewSet(viewsets.ModelViewSet):
    queryset = FeePayment.objects.select_related('student__user', 'category').all()
    serializer_class = FeePaymentSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['student', 'status']
