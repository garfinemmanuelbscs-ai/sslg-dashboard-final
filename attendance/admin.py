from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import AttendanceRecord, StudentProfile
from deepface import DeepFace
import json
import io
from PIL import Image
import numpy as np

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'has_encoding')
    readonly_fields = ('face_encoding',)

    def has_encoding(self, obj):
        return bool(obj.face_encoding)
    has_encoding.boolean = True

    def save_model(self, request, obj, form, change):
        # 1️⃣ Save the model baseline first so files are committed to Cloudinary
        super().save_model(request, obj, form, change)
        
        # 2️⃣ Auto-Assign Basic SSLG Staff Permissions to the User
        try:
            staff_group, created = Group.objects.get_or_create(name='SSLG Operations Staff')
            if created:
                # Give this group basic rights to view logs if needed
                content_type = ContentType.objects.get_for_model(AttendanceRecord)
                permission = Permission.objects.get(codename='view_attendancerecord', content_type=content_type)
                staff_group.permissions.add(permission)
            
            obj.user.groups.add(staff_group)
            if not obj.user.is_staff:
                obj.user.is_staff = True  # Allows them access to terminal entry points
                obj.user.save()
        except Exception as perm_err:
            print(f"⚠️ Permissions Group Auto-Assignment skipped: {perm_err}")

        # 3️⃣ Cloud-safe DeepFace math calculation
        if obj.photo and not obj.face_encoding:
            try:
                # 📸 Read photo file stream safely directly from cloud memory bucket
                photo_file = obj.photo.open()
                image_bytes = photo_file.read()
                
                # Convert bytes into an image array that DeepFace can ingest without local paths
                image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
                img_array = np.array(image)
                
                # Process vectors via Facenet engine directly from memory array
                results = DeepFace.represent(img_path=img_array, model_name="Facenet", enforce_detection=True)
                
                if results:
                    embedding = results[0]["embedding"]
                    obj.face_encoding = json.dumps(embedding)
                    # Atomically update profile table row
                    StudentProfile.objects.filter(pk=obj.pk).update(face_encoding=obj.face_encoding)
                    print(f"✅ DEEPFACE SUCCESS: Encoded cloud profile file for {obj.user}")
                else:
                    print("❌ DEEPFACE FAILED: No face detected in photo framework.")
            except Exception as e:
                print(f"🔥 DeepFace Cloud Admin Ingestion Error: {e}")
            finally:
                obj.photo.close()

@admin.register(AttendanceRecord)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'remarks')
    list_filter = ('status', 'date')
    search_fields = ('student__username', 'remarks')