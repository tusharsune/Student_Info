from django.db import models

from django.contrib.auth.models import User

class Student(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 👈 Add this line
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    enrollment_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Performance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="performances")
    marks = models.IntegerField()  # Changed to IntegerField if marks are integers
    grade = models.CharField(max_length=2)
    feedback = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.student.name} - {self.grade} - {self.marks}'

class Attendance(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('Present', 'Present'), ('Absent', 'Absent')])

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.status}"
