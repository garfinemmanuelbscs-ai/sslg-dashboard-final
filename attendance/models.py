from django.db import models
from django.contrib.auth.models import User
import json

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # This stores the "face math"
    face_encoding = models.TextField(null=True, blank=True) 
    photo = models.ImageField(upload_to='profiles/')

    def __str__(self):
        return self.user.username

class AttendanceRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=[('present', 'Present'), ('absent', 'Absent'), ('late', 'Late')]
    )
    remarks = models.TextField(blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"