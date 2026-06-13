from django.db import models
from django.contrib.auth.models import User

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 🔍 Added to support tracking middle initials safely
    middle_initial = models.CharField(max_length=2, blank=True, null=True)
    face_encoding = models.TextField(null=True, blank=True) 
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True) # Allowed blank initially

    def __str__(self):
        return f"{self.user.username} Profile"

    class Meta:
        default_permissions = ('add', 'view')  # 🔒 Blocks Django from recreating change/delete
        # 🖨️ Explicit custom print permission registration
        permissions = [
            ("print_studentprofile", "Can print student profile rosters"),
        ]


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

    class Meta:
        default_permissions = ('add', 'view')  # 🔒 Blocks Django from recreating change/delete
        # 🖨️ Explicit custom print permission registration
        permissions = [
            ("print_attendancerecord", "Can print historical attendance records"),
        ]