from django.contrib import admin
from .models import AttendanceRecord, StudentProfile
from deepface import DeepFace
import json
import os

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_encoding')
    readonly_fields = ('face_encoding',)

    def has_encoding(self, obj):
        return bool(obj.face_encoding)
    has_encoding.boolean = True

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        
        if obj.photo:
            try:
                # Get the absolute path to the uploaded photo
                img_path = obj.photo.path
                
                # DeepFace.represent generates the math (embedding) for the face
                # We use 'Facenet' as it is fast and accurate
                results = DeepFace.represent(img_path=img_path, model_name="Facenet", enforce_detection=True)
                
                if results:
                    # Extract the list of numbers and save as JSON
                    embedding = results[0]["embedding"]
                    obj.face_encoding = json.dumps(embedding)
                    # Force update the field in the database
                    StudentProfile.objects.filter(pk=obj.pk).update(face_encoding=obj.face_encoding)
                    print(f"✅ DEEPFACE SUCCESS: Encoded {obj.user}")
                else:
                    print("❌ DEEPFACE FAILED: No face detected in photo.")
            except Exception as e:
                print(f"🔥 DeepFace Admin Error: {e}")

@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'remarks')