import os
import django
import random
from datetime import date, timedelta, time
from django.contrib.auth import get_user_model
from departments.models import Department
from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from subjects.models import Subject
from exams.models import Exam, Marks
from fees.models import FeeCategory, FeePayment
from attendance.models import Attendance
from timetable.models import Timetable
from assignments.models import Assignment, Submission
from notices.models import Notice

User = get_user_model()

def seed():
    print("Clearing old dummy data (except admin)...")
    User.objects.filter(is_superuser=False).delete()
    Department.objects.all().delete()
    FeeCategory.objects.all().delete()
    Notice.objects.all().delete()

    print("Creating Departments...")
    dept_cs = Department.objects.create(name='Computer Science', code='CS', description='CS Department')
    dept_me = Department.objects.create(name='Mechanical Engineering', code='ME', description='ME Department')

    print("Creating Courses...")
    course_btech_cs = Course.objects.create(name='B.Tech Computer Science', code='BTCS', department=dept_cs, semester=8, credits=4)
    course_mtech_cs = Course.objects.create(name='M.Tech Computer Science', code='MTCS', department=dept_cs, semester=4, credits=4)
    course_btech_me = Course.objects.create(name='B.Tech Mechanical', code='BTME', department=dept_me, semester=8, credits=4)

    print("Creating Teachers...")
    t1_user = User.objects.create_user(username='teacher_alice', password='password123', first_name='Alice', last_name='Smith', email='alice@example.com', role='teacher')
    t2_user = User.objects.create_user(username='teacher_bob', password='password123', first_name='Bob', last_name='Jones', email='bob@example.com', role='teacher')
    
    t1 = Teacher.objects.create(user=t1_user, employee_id='EMP001', department=dept_cs, qualification='PhD', phone='1234567890')
    t2 = Teacher.objects.create(user=t2_user, employee_id='EMP002', department=dept_me, qualification='M.Tech', phone='0987654321')

    print("Creating Subjects...")
    sub_ds = Subject.objects.create(name='Data Structures', code='CS201', course=course_btech_cs, teacher=t1, credits=4)
    sub_algo = Subject.objects.create(name='Algorithms', code='CS202', course=course_btech_cs, teacher=t1, credits=4)
    sub_thermo = Subject.objects.create(name='Thermodynamics', code='ME201', course=course_btech_me, teacher=t2, credits=4)

    print("Creating Students...")
    students = []
    for i in range(1, 11):
        s_user = User.objects.create_user(username=f'student_{i}', password='password123', first_name=f'Student', last_name=f'{i}', email=f'student{i}@example.com', role='student')
        student = Student.objects.create(
            user=s_user, admission_number=f'ADM100{i}', roll_number=f'R100{i}',
            gender=random.choice(['male', 'female']),
            date_of_birth=date(2002, 5, 10) + timedelta(days=i*10),
            phone=f'987654321{i}',
            parent_name=f'Parent of Student {i}',
            parent_contact=f'912345678{i}',
            address=f'House #{i}, University Residential block, Campus ground',
            batch='2023-2027',
            department=dept_cs if i <= 5 else dept_me,
            course=course_btech_cs if i <= 5 else course_btech_me,
            semester=2, admission_date=date(2023, 8, 1)
        )
        students.append(student)

    print("Creating Attendance...")
    today = date.today()
    for student in students:
        subject = sub_ds if student.course == course_btech_cs else sub_thermo
        teacher = t1 if student.course == course_btech_cs else t2
        for d in range(5):
            Attendance.objects.create(
                student=student, subject=subject, date=today - timedelta(days=d),
                status=random.choice(['present', 'present', 'present', 'absent']),
                marked_by=teacher
            )

    print("Creating Exams and Marks...")
    exam1 = Exam.objects.create(name='Mid Term - Data Structures', subject=sub_ds, exam_type='mid_sem', exam_date=today - timedelta(days=10), semester=2)
    exam2 = Exam.objects.create(name='Mid Term - Thermodynamics', subject=sub_thermo, exam_type='mid_sem', exam_date=today - timedelta(days=10), semester=2)
    
    for student in students:
        exam = exam1 if student.course == course_btech_cs else exam2
        Marks.objects.create(
            student=student, exam=exam,
            theory_marks=random.randint(20, 50),
            practical_marks=random.randint(10, 25),
        )

    print("Creating Fees...")
    fee_cat = FeeCategory.objects.create(name='Tuition Fee Semester 2', amount=50000, semester=2)
    for i, student in enumerate(students):
        FeePayment.objects.create(
            student=student, category=fee_cat, amount_paid=random.choice([0, 25000, 50000]),
            due_date=today + timedelta(days=30),
            status=random.choice(['pending', 'partial', 'paid']),
            receipt_number=f"RCPT-{random.randint(1000, 9999)}-{i}"
        )

    print("Creating Timetable...")
    Timetable.objects.create(department=dept_cs, course=course_btech_cs, semester=2, day='monday', start_time=time(10, 0), end_time=time(11, 0), subject=sub_ds, teacher=t1, room='101')
    Timetable.objects.create(department=dept_me, course=course_btech_me, semester=2, day='monday', start_time=time(11, 0), end_time=time(12, 0), subject=sub_thermo, teacher=t2, room='201')

    print("Creating Assignments...")
    assign1 = Assignment.objects.create(title='DS Assignment 1', description='Implement a BST', subject=sub_ds, teacher=t1, due_date=today + timedelta(days=5), max_marks=10)
    for student in students[:5]:
        if random.choice([True, False]):
            Submission.objects.create(assignment=assign1, student=student, submitted_at=today, marks_obtained=random.randint(5, 10))

    print("Creating Notices...")
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = t1_user
    Notice.objects.create(title='Welcome to Semester 2', content='Classes begin next week.', posted_by=admin_user, priority='high', is_active=True)

    print("Dummy data seeded successfully!")

if __name__ == '__main__':
    seed()
