from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views, logout
from django.conf import settings
from django.conf.urls.static import static

# Import your core hub views and your real attendance views
from attendance import views as attendance_views
from finance import views as finance_views
from inventory import views as inventory_views
from events import views as events_views 
from studentgov import views as main_views

# 🔑 Custom logout view to fix the Django 5+ strict POST login trap
def custom_logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [
    # 🔐 Authentication Routes
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('logout/', custom_logout_view, name='logout'),
    
    # 🏛️ Core Dashboard Hub Routes
    path('', lambda request: redirect('dashboard')),
    path('dashboard/', main_views.dashboard, name='dashboard'),
    
    # 📸 Real Attendance App Routing Matrix
    path('attendance/hub/', attendance_views.attendance_hub, name='attendance_hub'),
    path('attendance/scan/', attendance_views.scan_attendance, name='scan'),
    path('attendance/logs/', attendance_views.attendance_logs, name='attendance_logs'),
    path('attendance/profiles/', attendance_views.student_profiles_manage, name='student_profiles'),
    path('attendance/verify/', attendance_views.verify_face, name='verify_face'),
    # 🖨️ Documentation Print Routes (Attendance)
    path('attendance/print/profiles/', attendance_views.print_student_profiles, name='print_student_profiles'),
    path('attendance/print/records/', attendance_views.print_attendance_records, name='print_attendance_records'),
    
    # 🔄 Production App Mappings (Finance)
    path('finance/transactions/', finance_views.finance_ledger, name='finance_ledger'),
    # 🖨️ Documentation Print Routes (Finance)
    path('finance/print/', finance_views.print_finance_ledger, name='print_finance_ledger'),
    
    # 🔄 Production App Mappings (Inventory)
    path('inventory/items/', inventory_views.inventory_management, name='inventory_management'),
    # 🖨️ Documentation Print Routes (Inventory)
    path('inventory/print/list/', inventory_views.print_inventory, name='print_inventory'),
    
    # 🎪 Real Events App Routes
    path('events/calendar/', events_views.events_dashboard, name='events_calendar'), 
    path('events/dashboard/', events_views.events_dashboard, name='events_dashboard'), 
    path('events/create/', events_views.create_event, name='create_event'),
    path('events/update-expense/<int:event_id>/', events_views.update_expense, name='update_expense'),
    path('events/delete/<int:event_id>/', events_views.delete_event, name='delete_event'),
    # 🖨️ Documentation Print Routes (Events)
    path('events/print/summary/', events_views.print_events_summary, name='print_events_summary'),
    
    # 🛠️ Administrative Frameworks Control Station
    path('admin-control/roles/', main_views.manage_roles, name='manage_roles'),
    path('admin-control/user/create/', main_views.create_user, name='create_user'),
    path('admin-control/user/delete/<int:user_id>/', main_views.delete_user, name='delete_user'),
    path('admin-control/user/password/<int:user_id>/', main_views.change_user_password, name='change_user_password'),
    path('admin-control/group/edit/<int:group_id>/', main_views.edit_group, name='edit_group'),
    path('admin-control/group/delete/<int:group_id>/', main_views.delete_group, name='delete_group'),
    path('admin-control/group/assign/', main_views.assign_user_role, name='assign_user_role'),
    
    path('secret-backend/', admin.site.urls),
]

# 📸 LOCAL ASSET ROUTING MATRIX ACCELERATOR
# This tells Django to explicitly look in your local hard drive folders for media uploads when running locally
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)