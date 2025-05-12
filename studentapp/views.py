from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Student, Performance, Attendance
from django.core.paginator import Paginator
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.contrib import messages
from reportlab.pdfgen import canvas
from datetime import datetime, date
from decimal import Decimal
from textwrap import wrap
from io import BytesIO
import json

from django.contrib.auth import get_user_model

def index(request):
    return render(request, 'index.html')

@login_required
def home(request):
    query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', 'name')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    students = Student.objects.filter(user=request.user)

    if query:
        students = students.filter(name__icontains=query) | students.filter(email__icontains=query)

    if start_date and end_date:
        students = students.filter(enrollment_date__gte=start_date, enrollment_date__lte=end_date)

    if sort_by == 'name':
        students = students.order_by('name')
    elif sort_by == 'email':
        students = students.order_by('email')
    elif sort_by == 'phone':
        students = students.order_by('phone')

    paginator = Paginator(students, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home.html', {
        'page_obj': page_obj, 'query': query, 'sort_by': sort_by, 'start_date': start_date, 'end_date': end_date
    })

def about(request):
    context = {
        'project_name': '👨‍🎓 Student_Info',
        'mission': "To simplify student management for schools and institutions through an easy-to-use web application.",
        'why_built': "This project was created to help educational institutions manage data digitally and efficiently.",
        'how_it_helps': "By automating tasks like attendance, progress tracking, and record updates, it reduces paperwork and human error.",
        'future_plans': [
            "Only verified teachers can log in. Verification is done based on their official offer and joining letters to ensure authenticity.",
            'Add automated report card generation',
            'Enable real-time chat between parents and teachers',
            'Mobile app integration',
            'Multi-language support'
            'Generate classroom timetables',
            'Allow parents to view student updates',
        ],
        'features': [
            'Secure login and access control',
            'Manage student records easily',
            'Track academic progress',
            'Mark and view attendance',
        ],
        'tech_stack': ['Python', 'Django', 'Matplotlib', 'SQLite', 'HTML', 'CSS'],
        'developer_name': 'Tushar D. Sune',
        'developer_role': 'Python/Django Developer'
    }
    return render(request, 'about.html', context)


@login_required
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id, user=request.user)  
    performances = student.performances.order_by('id')
    attendances = student.attendances.order_by('date')

    labels = []
    marks = []

    for p in performances:
        subject = getattr(p, 'subject', None)
        if subject:
            labels.append(f"{subject} ({p.grade})")
        else:
            labels.append(f"Entry {p.id}")
        
        marks.append(float(p.marks) if isinstance(p.marks, Decimal) else p.marks)

    attendance_status = {attendance.date: attendance.status for attendance in attendances}

    today = date.today().isoformat()

    context = {
        'student': student,
        'labels': json.dumps(labels),
        'marks': json.dumps(marks),
        'attendance_status': attendance_status,
        'today': today,
    }

    return render(request, 'student_detail.html', context)


@login_required
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if Student.objects.filter(email=email).exists():
            messages.error(request, "A student with this email already exists.")
            return render(request, 'add_student.html', {
                'name': name, 'email': email, 'phone': phone, 'address': address
            })

        Student.objects.create(
            user=request.user,
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        messages.success(request, "Student added successfully.")
        
        return redirect('home') 
    return render(request, 'add_student.html')


@login_required
def edit_student(request, id):
    student = get_object_or_404(Student, pk=id)
    if request.method == 'POST':
        student.name = request.POST['name']
        student.email = request.POST['email']
        student.phone = request.POST['phone']
        student.address = request.POST['address']
        student.save()
        return redirect('home')
    return render(request, 'edit_student.html', {'student': student})


@login_required
def delete_student(request, id):
    student = get_object_or_404(Student, pk=id)
    student.delete()
    return redirect('home')


@login_required
def add_performance(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    
   
    from .forms import PerformanceForm

    if request.method == "POST":
        form = PerformanceForm(request.POST)
        if form.is_valid():
            performance = form.save(commit=False)
            performance.student = student
            performance.save()
            return redirect('student_detail', student_id=student.id)
    else:
        form = PerformanceForm()

    return render(request, 'add_performance.html', {'form': form, 'student': student})


@login_required
def mark_attendance(request, student_id, date):
    student = get_object_or_404(Student, id=student_id)
    date = datetime.strptime(date, '%Y-%m-%d').date()

    if date > datetime.now().date():
        return HttpResponse("Cannot mark attendance for a future date.", status=400)

    attendance, created = Attendance.objects.get_or_create(student=student, date=date)
    
    from .forms import AttendanceForm

    if request.method == "POST":
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            return redirect('student_detail', student_id=student.id)
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'mark_attendance.html', {'form': form, 'student': student, 'date': date})

def create_admin_user():
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'tdssdt765@gmail.com', 'tusharsune..2411')


@login_required
def generate_pdf_report(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    performances = student.performances.all()
    attendances = student.attendances.all()

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter  

    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, height - 40, f"Student Report: {student.name}")

    p.setFont("Helvetica", 10)
    p.drawString(100, height - 60, "Performance History:")

    y_position = height - 80 

    for performance in performances:
        performance_text = f"{performance.marks} - {performance.grade} - {performance.feedback}"
        
        wrapped_text = wrap(performance_text, width=60) 
        
        for line in wrapped_text:
            p.drawString(100, y_position, line)
            y_position -= 12  

        y_position -= 10 

    p.drawString(100, y_position, "Attendance History:")
    y_position -= 20

    for attendance in attendances:
        attendance_text = f"{attendance.date} - {attendance.status}"
        
        wrapped_text = wrap(attendance_text, width=60)
        
        for line in wrapped_text:
            p.drawString(100, y_position, line)
            y_position -= 12 

        y_position -= 10  
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{student.name}_report.pdf"'
    return response
