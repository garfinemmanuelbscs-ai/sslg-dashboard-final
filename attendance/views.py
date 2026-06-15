from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q
from .models import StudentProfile, AttendanceRecord
from deepface import DeepFace
from scipy.spatial import distance
import json
import io
import base64
from PIL import Image
import numpy as np

# ==========================================
# 🔐 GRANULAR ACCESS CONTROLLERS
# ==========================================

def is_admin_user(user):
    """Checks for root administrator status"""
    return user.is_superuser or user.username.lower() == 'admin'

def has_attendance_perm(user, perm_codename):
    """Evaluates explicit, superuser, or inherited role permissions"""
    if not user or user.is_anonymous:
        return False
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm(f'attendance.{perm_codename}') or
        user.groups.filter(permissions__codename=perm_codename).exists()
    )

def can_view_hub(user):
    return (
        is_admin_user(user) or 
        has_attendance_perm(user, 'view_attendancerecord') or 
        has_attendance_perm(user, 'view_studentprofile') or
        has_attendance_perm(user, 'add_attendancerecord')
    )

def can_view_logs(user):
    return has_attendance_perm(user, 'view_attendancerecord')

def can_run_scanner(user):
    return has_attendance_perm(user, 'add_attendancerecord')

def can_view_profiles(user):
    return user.is_authenticated

def can_print_profiles(user):
    return is_admin_user(user) or has_attendance_perm(user, 'print_studentprofile')

def can_print_records(user):
    return is_admin_user(user) or has_attendance_perm(user, 'print_attendancerecord')


# ==========================================
# 🏛️ ATTENDANCE & BIOMETRIC GATEWAYS
# ==========================================

@login_required
@user_passes_test(can_view_hub, login_url='dashboard')
def attendance_hub(request):
    """🏛️ Central hub menu exposing contextually verified modules"""
    return render(request, 'attendance/hub.html')


@login_required
@user_passes_test(can_view_logs, login_url='attendance_hub')
def attendance_logs(request):
    """📋 View historical attendance logging tracks"""
    records = AttendanceRecord.objects.all().order_by('-date')
    return render(request, 'attendance/logs.html', {'records': records})


@login_required
@user_passes_test(can_view_profiles, login_url='attendance_hub')
def student_profiles_manage(request):
    """👤 Manage and register face profiles with dynamic self-service scoping"""
    is_staff_or_admin = has_attendance_perm(request.user, 'view_studentprofile') or is_admin_user(request.user)
    is_modifier = has_attendance_perm(request.user, 'add_studentprofile') or is_admin_user(request.user)

    if request.method == 'POST':
        user_id = request.POST.get('user')
        photo = request.FILES.get('photo')
        
        if not user_id or not photo:
            messages.error(request, "Please select a user and upload a valid photo.")
            return redirect('student_profiles')
            
        if not is_modifier and str(user_id) != str(request.user.id):
            messages.error(request, "Access Denied: You are only authorized to compile your own face profile.")
            return redirect('student_profiles')
            
        try:
            target_user = User.objects.get(id=user_id)
            profile, created = StudentProfile.objects.get_or_create(user=target_user)
            profile.photo = photo
            profile.save()
            
            # 📸 Safe in-memory DeepFace Face Encoding calculations
            photo_file = profile.photo.open()
            image_bytes = photo_file.read()
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            img_array = np.array(image)
            
            results = DeepFace.represent(
                img_path=img_array, 
                model_name="VGG-Face", 
                detector_backend="opencv", 
                enforce_detection=False
            )
            
            if results and len(results) > 0:
                embedding = results[0]["embedding"]
                profile.face_encoding = json.dumps(embedding)
                profile.save()
                messages.success(request, f"Successfully created face profile vector for {target_user.username}!")
            else:
                messages.error(request, "Face detection failed! Ensure lighting conditions reveal facial details cleanly.")
                if created:
                    profile.delete()
                
        except Exception as e:
            messages.error(request, f"Error processing face registry: {e}")
            
        return redirect('student_profiles')

    if is_staff_or_admin:
        profiles = StudentProfile.objects.all().select_related('user')
        all_users = User.objects.filter(
            Q(studentprofile__isnull=True) | 
            Q(studentprofile__face_encoding__isnull=True) | 
            Q(studentprofile__face_encoding='')
        ).distinct()
    else:
        profiles = StudentProfile.objects.filter(user=request.user).select_related('user')
        all_users = User.objects.filter(id=request.user.id).filter(
            Q(studentprofile__isnull=True) | 
            Q(studentprofile__face_encoding__isnull=True) | 
            Q(studentprofile__face_encoding='')
        ).distinct()

    return render(request, 'attendance/profiles.html', {
        'profiles': profiles,
        'all_users': all_users,
        'is_staff_or_admin': is_staff_or_admin
    })


@login_required
@user_passes_test(can_run_scanner, login_url='attendance_hub')
def scan_attendance(request):
    """📷 Face Scanner Core Terminal view wrapper"""
    return render(request, 'attendance/scan.html')


@csrf_exempt
@login_required
def verify_face(request):
    """🔬 Robust AJAX live face validation processing engine"""
    if not has_attendance_perm(request.user, 'add_attendancerecord'):
        return JsonResponse({'status': 'denied', 'message': 'Lacks biometric verification authority.'}, status=403)
        
    if request.method == 'POST':
        try:
            try:
                data = json.loads(request.body)
            except Exception as json_err:
                print(f"❌ JSON Parse Error: {json_err}")
                data = request.POST if request.POST else {}

            image_data = data.get('image') or request.POST.get('image')
            
            if not image_data:
                print("❌ Verification Error: Capture data payload string missing.")
                return JsonResponse({'status': 'failed', 'message': 'Missing frame capture element.'}, status=400)
                
            if "," in image_data:
                image_data = image_data.split(',')[1]
                
            try:
                img_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                live_array = np.array(image)
            except Exception as img_err:
                print(f"❌ Image Decoding Error: {img_err}")
                return JsonResponse({'status': 'failed', 'message': 'Invalid image format sent from webcam.'}, status=400)
            
            try:
                live_results = DeepFace.represent(
                    img_path=live_array, 
                    model_name="VGG-Face", 
                    detector_backend="opencv", 
                    enforce_detection=False
                )
            except Exception as df_err:
                print(f"❌ DeepFace Representation Exception: {df_err}")
                return JsonResponse({'status': 'failed', 'message': 'Facial model engine error.'}, status=500)
            
            if not live_results or len(live_results) == 0:
                return JsonResponse({'status': 'failed', 'message': 'No face detected in live feed stream.'})
                
            live_embedding = live_results[0]["embedding"]
            valid_profiles = StudentProfile.objects.exclude(face_encoding__isnull=True).exclude(face_encoding='')
            
            # 🛑 1. RESET MATCH VARIABLES FOR THE CURRENT LIVE WEB-FRAME 
            best_match_user = None
            lowest_distance = 999.0  # High number so the first real check drops it
            
            # 🛡️ STRICT SECURITY THRESHOLD FOR VGG-FACE + COSINE DISTANCE
            # 0.40 is too loose. 0.25 means they must look 75% identical biometric-wise.
            SECURITY_THRESHOLD = 0.25 
            
            print(f"\n🚀 --- NEW BIOMETRIC SCANNER FRAME ---")
            print(f"Total Database Profiles to Compare: {len(valid_profiles)}")

            for profile in valid_profiles:
                try:
                    # Parse out the registered student's face vectors
                    stored_embedding = json.loads(profile.face_encoding)
                    
                    # Compute spatial cosine distance
                    cos_dist = distance.cosine(live_embedding, stored_embedding)
                    
                    # 🔬 Real-time console analytics
                    print(f"   👤 Testing [{profile.user.username}] -> Dist: {cos_dist:.4f} (Target: < {SECURITY_THRESHOLD})")
                    
                    # Core matching logic conditional trap
                    if cos_dist < SECURITY_THRESHOLD:
                        if cos_dist < lowest_distance:
                            lowest_distance = cos_dist
                            best_match_user = profile.user
                            print(f"      🔥 New Lead Match: {best_match_user.username} @ {lowest_distance:.4f}")
                
                except Exception as profile_err:
                    print(f"   ⚠️ Skipping Profile ID {profile.id} Error: {profile_err}")
                    continue

            # 🛑 2. FINAL VERIFICATION GATEKEEPER CHECK
            if best_match_user is not None:
                print(f"✅ [SUCCESS] Face verified as operational user: {best_match_user.username} (Distance: {lowest_distance:.4f})")
                
                # Create the live attendance check-in instance log in your database
                AttendanceRecord.objects.create(
                    student=best_match_user, 
                    status='present',
                    remarks=f"Biometric matching verified via VGG-Face engine. (Dist: {lowest_distance:.4f})"
                )
                
                return JsonResponse({
                    'status': 'success', 
                    'result': 'Access Granted',
                    'message': 'Access Granted',
                    'user': best_match_user.username
                })
            else:
                print("❌ [REJECTED] Biometric signature did not match any registered officer.")
                return JsonResponse({'status': 'Access Denied', 'reason': 'No secure profile match found.'})

        except Exception as global_err:
            print(f"❌ Critical Error in verify_face view processing: {global_err}")
            return JsonResponse({'status': 'failed', 'message': f'Internal backend error: {global_err}'}, status=500)

    return JsonResponse({'status': 'failed', 'message': 'Invalid view processing method request type.'}, status=405)


# ==========================================
# ⚙️ MATRIX ROLE & IDENTITY ADMINISTRATION
# ==========================================

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def manage_roles(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        permission_ids = request.POST.getlist('permissions')
        
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            if '-1' in permission_ids:
                permission_ids.remove('-1')
            group.permissions.set(Permission.objects.filter(id__in=permission_ids))
            messages.success(request, f"Authorization Group '{group_name}' compiled successfully!")
        return redirect('manage_roles')

    users = User.objects.all().select_related('studentprofile').prefetch_related('groups')
    groups = Group.objects.all().prefetch_related('permissions')
    sslg_permissions = Permission.objects.all().select_related('content_type')
    
    return render(request, 'admin/manage_roles.html', {
        'users': users,
        'groups': groups,
        'sslg_permissions': sslg_permissions
    })

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def create_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        mi = request.POST.get('mi', '').strip()
        pword = request.POST.get('password')
        repword = request.POST.get('re_password')

        if pword != repword:
            messages.error(request, "Password validation failed: Match verification error.")
            return redirect('manage_roles')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username declaration conflict: Account already exists.")
            return redirect('manage_roles')

        new_user = User.objects.create_user(username=username, password=pword)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        StudentProfile.objects.get_or_create(user=new_user, defaults={'middle_initial': mi if mi else None})
        messages.success(request, f"User account tracking initialized for {username} successfully!")
    return redirect('manage_roles')

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def delete_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if target_user.username == 'admin' or target_user.is_superuser:
            messages.error(request, "System Guardrail: Cannot eliminate Root Administrator instance.")
        else:
            username = target_user.username
            target_user.delete()
            messages.success(request, f"User instance profile '{username}' dropped from grid.")
    return redirect('manage_roles')

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def change_user_password(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        pword = request.POST.get('password')
        repword = request.POST.get('re_password')

        if pword != repword:
            messages.error(request, "Access key modification failed: Match verification error.")
            return redirect('manage_roles')

        target_user.set_password(pword)
        target_user.save()
        messages.success(request, f"Security verification matrices updated for {target_user.username}.")
    return redirect('manage_roles')

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def edit_group(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        new_name = request.POST.get('group_name')
        permission_ids = request.POST.getlist('permissions')

        if new_name:
            group.name = new_name
            group.save()
            
        if '-1' in permission_ids:
            permission_ids.remove('-1')
            
        group.permissions.set(Permission.objects.filter(id__in=permission_ids))
        messages.success(request, f"Configuration definitions updated for group context '{group.name}'.")
    return redirect('manage_roles')

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def delete_group(request, group_id):
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        group_name = group.name
        group.delete()
        messages.success(request, f"Structural clearance container '{group_name}' deleted.")
    return redirect('manage_roles')

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def assign_user_role(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        
        target_user = get_object_or_404(User, id=user_id)
        target_user.groups.clear()
        
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            target_user.groups.add(group)
            messages.success(request, f"User clearance adjusted successfully for context: {group.name}.")
        else:
            messages.success(request, f"Clearance levels reset for account: {target_user.username}.")
    return redirect('manage_roles')


# ==========================================
# 🖨️ SYSTEM PRINT GENERATION TERMINALS
# ==========================================

@login_required
@user_passes_test(can_print_profiles, login_url='attendance_hub')
def print_student_profiles(request):
    profiles = StudentProfile.objects.all().select_related('user')
    return render(request, 'attendance/print_profiles.html', {
        'profiles': profiles,
        'is_staff_or_admin': True
    })

@login_required
@user_passes_test(can_print_records, login_url='attendance_hub')
def print_attendance_records(request):
    records = AttendanceRecord.objects.all().order_by('-date')
    return render(request, 'attendance/print_records.html', {'records': records})

@login_required
def delete_profile_photo(request, profile_id):
    """🗑️ Clears out face vectors and profile photo associations safely without Windows file locks"""
    is_modifier = has_attendance_perm(request.user, 'add_studentprofile') or is_admin_user(request.user)
    profile = get_object_or_404(StudentProfile, id=profile_id)
    
    # 🛡️ Guardrail: Regular users can only clear their own account photo
    if not is_modifier and profile.user != request.user:
        messages.error(request, "Access Denied: Unauthorized to modify this matrix profile.")
        return redirect('student_profiles')
        
    if request.method == 'POST':
        try:
            # 💡 WINDOWS FIX: Instead of running photo.delete() which triggers WinError 32,
            # we break the database relationship connection and clear the text vector hashes.
            profile.photo = None
            profile.face_encoding = None
            profile.save()
            
            messages.success(request, f"Face vector signatures cleared for {profile.user.username}.")
        except Exception as e:
            messages.error(request, f"Error processing deletion: {e}")
            
    return redirect('student_profiles')


@login_required
def delete_attendance_log(request, log_id):
    """🗑️ Deletes a specific biometric logging compliance entry"""
    # Restrict delete functions strictly to administrative managers
    if not (has_attendance_perm(request.user, 'view_attendancerecord') or is_admin_user(request.user)):
        return HttpResponseForbidden("Access Denied: Lacks log elimination authority.")
        
    if request.method == 'POST':
        log_entry = get_object_or_404(AttendanceRecord, id=log_id)
        user_target = log_entry.student.username
        log_entry.delete()
        messages.success(request, f"Attendance log transaction record dropped for {user_target}.")
        
    return redirect('attendance_logs')