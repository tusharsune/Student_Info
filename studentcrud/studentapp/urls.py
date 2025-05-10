from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # You may want to update this if it should be different
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:id>/', views.edit_student, name='edit_student'),
    path('delete/<int:id>/', views.delete_student, name='delete_student'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('student/<int:student_id>/add_performance/', views.add_performance, name='add_performance'),
    path('student/<int:student_id>/mark_attendance/<str:date>/', views.mark_attendance, name='mark_attendance'),
    path('student/<int:student_id>/generate_pdf_report/', views.generate_pdf_report, name='generate_pdf_report'),

]
