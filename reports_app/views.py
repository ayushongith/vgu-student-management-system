from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required
from django.db.models import Count, Avg, Sum
from students.models import Student
from teachers.models import Teacher
from attendance.models import Attendance
from exams.models import Marks, Exam
from fees.models import FeePayment
from datetime import date, timedelta
import json


@admin_required
def reports_dashboard(request):
    import json
    # 1. Attendance Present vs Absent
    attendance_stats = Attendance.objects.values('status').annotate(count=Count('id'))
    attendance_data = {'present': 0, 'absent': 0}
    for stat in attendance_stats:
        if stat['status'] in attendance_data:
            attendance_data[stat['status']] = stat['count']

    # 2. Course Enrollment distribution
    course_stats = Student.objects.values('course__code').annotate(count=Count('id'))
    course_labels = []
    course_counts = []
    for stat in course_stats:
        if stat['course__code']:
            course_labels.append(stat['course__code'])
            course_counts.append(stat['count'])

    # 3. Fee Payments counts
    fee_stats = FeePayment.objects.values('status').annotate(count=Count('id'))
    fee_data = {'paid': 0, 'partial': 0, 'pending': 0}
    for stat in fee_stats:
        if stat['status'] in fee_data:
            fee_data[stat['status']] = stat['count']

    # 4. Grades split
    grade_stats = Marks.objects.values('grade').annotate(count=Count('id')).order_by('grade')
    grade_labels = []
    grade_counts = []
    for stat in grade_stats:
        if stat['grade']:
            grade_labels.append(stat['grade'])
            grade_counts.append(stat['count'])

    return render(request, 'reports_app/reports_dashboard.html', {
        'attendance_json': json.dumps(attendance_data),
        'course_labels_json': json.dumps(course_labels),
        'course_counts_json': json.dumps(course_counts),
        'fee_json': json.dumps(fee_data),
        'grade_labels_json': json.dumps(grade_labels),
        'grade_counts_json': json.dumps(grade_counts),
    })


@admin_required
def attendance_report(request):
    from django.db.models import Q
    start_date = request.GET.get('from', (date.today() - timedelta(days=30)).isoformat())
    end_date = request.GET.get('to', date.today().isoformat())

    report = Attendance.objects.filter(date__gte=start_date, date__lte=end_date) \
        .values('status').annotate(count=Count('id'))

    daily = Attendance.objects.filter(date__gte=start_date, date__lte=end_date) \
        .values('date', 'status').annotate(count=Count('id')).order_by('date')

    return render(request, 'reports_app/attendance_report.html', {
        'report': report, 'daily': list(daily),
        'start_date': start_date, 'end_date': end_date
    })


@admin_required
def exam_report(request):
    exam_id = request.GET.get('exam')
    exams = Exam.objects.all()
    marks_data = []
    if exam_id:
        marks_qs = Marks.objects.filter(exam_id=exam_id).select_related('student__user')
        for m in marks_qs:
            marks_data.append({
                'student': m.student.user.get_full_name(),
                'roll': m.student.roll_number,
                'theory': m.theory_marks,
                'practical': m.practical_marks,
                'total': m.total_marks,
                'grade': m.grade,
                'pct': m.percentage,
            })
        avg = Marks.objects.filter(exam_id=exam_id).aggregate(
            avg_total=Avg('total_marks'), avg_theory=Avg('theory_marks'), avg_practical=Avg('practical_marks')
        )
    else:
        avg = {}

    return render(request, 'reports_app/exam_report.html', {
        'exams': exams, 'marks_data': marks_data, 'avg': avg, 'selected_exam': exam_id
    })


@admin_required
def fee_report(request):
    total_collected = FeePayment.objects.filter(status='paid').aggregate(total=Sum('amount_paid'))
    pending = FeePayment.objects.filter(status='pending').count()
    paid = FeePayment.objects.filter(status='paid').count()
    return render(request, 'reports_app/fee_report.html', {
        'total_collected': total_collected['total'] or 0,
        'pending': pending, 'paid': paid
    })


@login_required
def academic_predictor(request, student_id=None):
    user = request.user
    students_list = None
    selected_student = None

    if user.role in ['admin', 'teacher']:
        students_list = Student.objects.all().select_related('user', 'course')
        if student_id:
            selected_student = get_object_or_404(Student, pk=student_id)
        elif request.GET.get('student'):
            selected_student = get_object_or_404(Student, pk=request.GET.get('student'))
        else:
            selected_student = students_list.first()
    elif user.role == 'student':
        selected_student = get_object_or_404(Student, user=user)
        if student_id and student_id != selected_student.pk:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to view other students' predictions.")

    if not selected_student:
        return render(request, 'reports_app/student_predictor.html', {
            'error_message': 'No student records found to perform analytics.'
        })

    # Attendance Projections
    attendance_qs = Attendance.objects.filter(student=selected_student)
    total_held = attendance_qs.count()
    present_count = attendance_qs.filter(status='present').count()
    current_pct = round((present_count / total_held * 100), 1) if total_held > 0 else 100.0

    total_semester_classes = 80
    remaining = max(0, total_semester_classes - total_held)
    max_possible_pct = round(((present_count + remaining) / total_semester_classes * 100), 1)
    min_classes_needed_for_75 = max(0, int(0.75 * total_semester_classes) - present_count)

    if current_pct >= 75:
        risk_level = 'safe'
        risk_text = 'Safe'
        risk_class = 'success'
    elif max_possible_pct >= 75:
        risk_level = 'warning'
        risk_text = 'At Risk'
        risk_class = 'warning'
    else:
        risk_level = 'danger'
        risk_text = 'Critical'
        risk_class = 'danger'

    # Academic & CGPA calculations
    marks_qs = Marks.objects.filter(student=selected_student).select_related('exam__subject')
    avg_pct = 0.0
    projected_cgpa = 0.0
    theory_pct = 0.0
    practical_pct = 0.0
    recommendation = "No exam marks available yet. Predictions will update once scores are recorded."

    if marks_qs.exists():
        avg_pct = sum(m.percentage for m in marks_qs) / marks_qs.count()
        projected_cgpa = min(10.0, round((avg_pct / 10.0), 2))

        theory_pct_sum = sum(m.theory_marks for m in marks_qs)
        theory_max_sum = sum(m.exam.max_theory_marks for m in marks_qs)
        practical_pct_sum = sum(m.practical_marks for m in marks_qs)
        practical_max_sum = sum(m.exam.max_practical_marks for m in marks_qs)

        theory_pct = round((theory_pct_sum / theory_max_sum * 100), 1) if theory_max_sum > 0 else 0.0
        practical_pct = round((practical_pct_sum / practical_max_sum * 100), 1) if practical_max_sum > 0 else 0.0

        if theory_pct < 60 and theory_pct < practical_pct:
            recommendation = "Your theory exam scores are significantly trailing your practical results. Focus on textbook readings, theory lectures, and structured notes. Try writing previous years' test papers to practice formatting answers."
        elif practical_pct < 60 and practical_pct < theory_pct:
            recommendation = "Your lab/practical submissions are holding back your academic performance. Ensure you attend all practical sessions, practice lab exercises, and ask for faculty help with lab assignments."
        elif avg_pct < 60:
            recommendation = "Your overall performance requires general improvement. Establish a dedicated study timetable, attend tutoring sessions, and regularly review course syllabus items."
        else:
            recommendation = "Excellent work! Your academic progress is balanced. Continue maintaining your current effort across both lecture rooms and lab sessions."

    return render(request, 'reports_app/student_predictor.html', {
        'students_list': students_list,
        'selected_student': selected_student,
        'attendance': {
            'total_held': total_held,
            'present': present_count,
            'current_pct': current_pct,
            'max_possible': max_possible_pct,
            'min_needed': min_classes_needed_for_75,
            'risk_level': risk_level,
            'risk_text': risk_text,
            'risk_class': risk_class,
        },
        'academics': {
            'avg_pct': round(avg_pct, 1),
            'projected_cgpa': projected_cgpa,
            'theory_pct': theory_pct,
            'practical_pct': practical_pct,
            'recommendation': recommendation,
        }
    })


@login_required
def download_transcript(request, student_id=None):
    import io
    from datetime import date
    from django.http import FileResponse, Http404
    from django.shortcuts import get_object_or_404
    from django.core.exceptions import PermissionDenied
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    
    from students.models import Student
    from exams.models import Marks

    user = request.user
    selected_student = None

    if user.role in ['admin', 'teacher']:
        if student_id:
            selected_student = get_object_or_404(Student, pk=student_id)
        else:
            first_student = Student.objects.first()
            if first_student:
                selected_student = first_student
    elif user.role == 'student':
        selected_student = get_object_or_404(Student, user=user)
        if student_id and student_id != selected_student.pk:
            raise PermissionDenied("You do not have permission to view other students' transcripts.")

    if not selected_student:
        raise Http404("Student record not found.")

    marks_qs = Marks.objects.filter(student=selected_student).select_related('exam__subject')
    
    avg_pct = 0.0
    projected_cgpa = 0.0
    if marks_qs.exists():
        avg_pct = sum(m.percentage for m in marks_qs) / marks_qs.count()
        projected_cgpa = min(10.0, round((avg_pct / 10.0), 2))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#007bff'),
        alignment=1
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.gray,
        alignment=1,
        spaceAfter=15
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#333333'),
        alignment=1,
        spaceAfter=15
    )
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12
    )
    val_style = ParagraphStyle(
        'ValStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )
    
    story.append(Paragraph("VIVEKANAND GLOBAL UNIVERSITY", title_style))
    story.append(Paragraph("OFFICE OF THE CONTROLLER OF EXAMINATIONS & STUDENT RECORDS", subtitle_style))
    story.append(Paragraph("<b>OFFICIAL ACADEMIC TRANSCRIPT</b>", section_title))
    
    student_meta = [
        [
            Paragraph("<b>Name:</b>", label_style), Paragraph(selected_student.user.get_full_name() or selected_student.user.username, val_style),
            Paragraph("<b>Department:</b>", label_style), Paragraph(selected_student.department.name, val_style)
        ],
        [
            Paragraph("<b>Roll Number:</b>", label_style), Paragraph(selected_student.roll_number, val_style),
            Paragraph("<b>Course:</b>", label_style), Paragraph(selected_student.course.name, val_style)
        ],
        [
            Paragraph("<b>Admission ID:</b>", label_style), Paragraph(selected_student.admission_number, val_style),
            Paragraph("<b>Date Generated:</b>", label_style), Paragraph(date.today().strftime('%d %B %Y'), val_style)
        ]
    ]
    
    meta_table = Table(student_meta, colWidths=[90, 160, 90, 160])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 20))
    
    grades_data = [
        [
            Paragraph("<b>Exam Name</b>", val_style),
            Paragraph("<b>Subject</b>", val_style),
            Paragraph("<b>Theory</b>", val_style),
            Paragraph("<b>Practical</b>", val_style),
            Paragraph("<b>Total</b>", val_style),
            Paragraph("<b>Grade</b>", val_style)
        ]
    ]
    
    for m in marks_qs:
        max_total = m.exam.max_theory_marks + m.exam.max_practical_marks
        grades_data.append([
            Paragraph(m.exam.name, val_style),
            Paragraph(m.exam.subject.name, val_style),
            Paragraph(str(m.theory_marks), val_style),
            Paragraph(str(m.practical_marks), val_style),
            Paragraph(f"{m.total_marks} / {max_total}", val_style),
            Paragraph(f"<b>{m.grade}</b>", val_style)
        ])
        
    if marks_qs.exists():
        grades_data.append([
            Paragraph(f"<b>Cumulative Average: {round(avg_pct, 1)}%</b>", val_style),
            Paragraph("", val_style),
            Paragraph("", val_style),
            Paragraph("", val_style),
            Paragraph(f"<b>Projected CGPA: {projected_cgpa} / 10.0</b>", val_style),
            Paragraph("", val_style)
        ])
    else:
        grades_data.append([Paragraph("No academic scores registered yet.", val_style), "", "", "", "", ""])
        
    grades_table = Table(grades_data, colWidths=[120, 120, 50, 60, 80, 70])
    
    t_style = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#007bff')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
    ]
    
    if marks_qs.exists():
        t_style.append(('SPAN', (0, -1), (3, -1)))
        t_style.append(('SPAN', (4, -1), (5, -1)))
        t_style.append(('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f8f9fa')))
        
    grades_table.setStyle(TableStyle(t_style))
    story.append(grades_table)
    story.append(Spacer(1, 40))
    
    sig_data = [
        [Paragraph("Prepared By: __________________", val_style), Paragraph("Controller of Examinations: __________________", val_style)]
    ]
    sig_table = Table(sig_data, colWidths=[250, 250])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    
    response = FileResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="transcript_{selected_student.roll_number}.pdf"'
    return response


