from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings # 1. Import settings
from django.conf.urls.static import static # 2. Import static helper
from . import views
from attendance import views as att_views

urlpatterns = [
    # Admin and Dashboard
    path('admin/', admin.site.urls),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Facial Recognition Attendance Paths
    path('attendance/scan/', att_views.scan_attendance, name='scan'),
    path('attendance/verify/', att_views.verify_face, name='verify'),

    # Redirect empty URL to dashboard
    path('', lambda request: redirect('dashboard')),
]

# 3. Add this block to handle the Media files 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)