from django.shortcuts import render
from django.http import JsonResponse
from .models import StudentProfile, AttendanceRecord
from django.utils import timezone
from deepface import DeepFace
import json
import numpy as np
from scipy.spatial.distance import cosine

# --- THIS WAS THE MISSING PIECE ---
def scan_attendance(request):
    """Renders the webcam scanning page."""
    return render(request, 'attendance/scan.html')
# ----------------------------------

def verify_face(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            image_data = data.get('image')

            # 1. Get embedding for the webcam face
            scan_results = DeepFace.represent(img_path=image_data, model_name="Facenet", enforce_detection=False)
            if not scan_results:
                return JsonResponse({'status': 'failed', 'message': 'No face detected.'})
            
            scan_embedding = scan_results[0]["embedding"]

            # 2. Get registered profiles
            profiles = StudentProfile.objects.exclude(face_encoding="")
            
            for profile in profiles:
                try:
                    saved_embedding = json.loads(profile.face_encoding)
                    
                    # 3. Compare using standard Cosine Similarity
                    dist = cosine(saved_embedding, scan_embedding)
                    
                    # 0.4 threshold for Facenet (Lower = Stricter)
                    if dist <= 0.3:
                        AttendanceRecord.objects.get_or_create(
                            student=profile.user,
                            date=timezone.now().date(),
                            defaults={'status': 'present', 'remarks': "DeepFace Verified"}
                        )
                        return JsonResponse({'status': 'success', 'name': profile.user.username})
                        
                except Exception as e:
                    print(f"Skipping profile {profile.user}: {e}")
                    continue

            return JsonResponse({'status': 'failed', 'message': 'Face not recognized'})
            
        except Exception as e:
            print(f"❌ SCAN ERROR: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'failed'})