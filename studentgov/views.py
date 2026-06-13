from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group, Permission
from django.contrib import messages
from django.db.models import Q, Sum

# Try-Except Fallbacks to safe-bind context apps across the system
try:
    from finance.models import Transaction
except ImportError:
    Transaction = None

try:
    from inventory.models import Item
except ImportError:
    Item = None

try:
    from attendance.models import StudentProfile
except ImportError:
    StudentProfile = None


# ==========================================
# 🔐 SYSTEM CENTRAL SECURITY CONTROLLERS
# ==========================================

def is_admin_user(user):
    """🛡️ System Guardrail: Checks for root administrator status"""
    return user.is_superuser or user.username.lower() == 'admin'


# ==========================================
# 🏛️ CORE LAYOUT METRIC ENGINE
# ==========================================

def get_base_context(extra_title="SSLG Primary Hub"):
    """📈 Accumulates real-time system tracking statistics safely across core modules"""
    if Transaction:
        total_income = Transaction.objects.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expense = Transaction.objects.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        live_balance = f"{(total_income - total_expense):,.2f}"
    else:
        live_balance = "0.00"

    if Item:
        db_low_stock = Item.objects.filter(quantity__lte=5).values('name', 'quantity')
        low_stock_list = list(db_low_stock)
    else:
        low_stock_list = []

    return {
        'title': extra_title,
        'balance': live_balance,
        'low_stock_items': low_stock_list,
        'absences': 4,
        'upcoming_events': [
            {'title': 'General Student Assembly', 'date': 'June 18, 2026'},
            {'title': 'Campus Clean-up Drive', 'date': 'June 25, 2026'}
        ]
    }


# ==========================================
# 🏛️ GENERAL NAVIGATION CORE VIEWS
# ==========================================

@login_required
def dashboard(request):
    """📊 Render the system-wide Master Status Workspace dashboard"""
    return render(request, 'dashboard.html', get_base_context('SSLG Main Dashboard'))


# =======================================================
# ⚙️ IDENTITY & ROLE MATRIX OPERATIONS (ADMIN STATION)
# =======================================================

@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def manage_roles(request):
    """🛠️ Matrix Dashboard: Renders configuration management layout and handles Group Compilations"""
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        selected_permission_ids = request.POST.getlist('permissions')
        
        valid_perm_ids = [pid for pid in selected_permission_ids if pid and pid.isdigit()]
        
        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            if valid_perm_ids:
                perms = Permission.objects.filter(id__in=valid_perm_ids)
                group.permissions.set(perms)
            else:
                group.permissions.clear()
                
            if created:
                messages.success(request, f"Authorization Group '{group_name}' compiled successfully!")
            else:
                messages.success(request, f"Configuration definitions updated for group context '{group_name}'.")
        return redirect('manage_roles')

    users = User.objects.all().prefetch_related('groups')
    groups = Group.objects.all().prefetch_related('permissions')
    
    # Track cross-application tracking permission nodes explicitly
    sslg_permissions = Permission.objects.filter(
        content_type__app_label__in=['finance', 'inventory', 'attendance', 'events']
    ).select_related('content_type').order_by('content_type__app_label', 'codename')

    context = {
        'users': users,
        'groups': groups,
        'sslg_permissions': sslg_permissions,
    }
    return render(request, 'admin/manage_roles.html', context)


@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def create_user(request):
    """👤 Form interface to generate structural account objects and safe profiles"""
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

        # Safely setup biometric tracking map shell if model profile app module is mounted
        if StudentProfile:
            StudentProfile.objects.get_or_create(user=new_user, defaults={'middle_initial': mi if mi else None})
        
        messages.success(request, f"User account tracking initialized for {username} successfully!")
    return redirect('manage_roles')


@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def delete_user(request, user_id):
    """🗑️ Drops an operational user node completely from the environment"""
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        if target_user.username.lower() == 'admin' or target_user.is_superuser:
            messages.error(request, "System Guardrail: Cannot eliminate Root Administrator instances.")
        else:
            username = target_user.username
            target_user.delete()
            messages.success(request, f"User instance profile '{username}' dropped from grid.")
    return redirect('manage_roles')


@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def change_user_password(request, user_id):
    """🔑 Overwrites target access validation security keys admin-side"""
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
def assign_user_role(request):
    """🤝 Clears and assigns a user profile to a designated system security role group"""
    if request.method == 'POST':
        
        # 🕵️‍♂️ TEMPORARY INCOMING FORM SCANNER
        print("\n=== 📥 ROLE ASSIGNMENT INCOMING POST DATA ===")
        print(f"Raw Form payload:   {dict(request.POST)}")
        print(f"Extracted user_id:  {request.POST.get('user_id')}")
        print(f"Extracted group_id: {request.POST.get('group_id')}")
        print("=============================================\n")
        
        user_id = request.POST.get('user_id')
        group_id = request.POST.get('group_id')
        
        user = get_object_or_404(User, id=user_id)
        user.groups.clear()
        
        if group_id:
            group = get_object_or_404(Group, id=group_id)
            user.groups.add(group)
            messages.success(request, f"Assigned role [{group.name}] to {user.username}.")
        else:
            messages.success(request, f"Revoked group tracking layers from {user.username}.")
            
    return redirect('manage_roles')


@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def edit_group(request, group_id):
    """✏️ Adjusts configuration parameters and overrides active permission models for a group"""
    group = get_object_or_404(Group, id=group_id)
    
    if request.method == 'POST':
        new_name = request.POST.get('group_name', '').strip()
        selected_permission_ids = request.POST.getlist('permissions')
        
        valid_perm_ids = [pid for pid in selected_permission_ids if pid and str(pid).isdigit()]
        
        if new_name and new_name != group.name:
            if Group.objects.filter(name__iexact=new_name).exclude(id=group.id).exists():
                messages.error(request, f"Naming conflict: A group named '{new_name}' already exists.")
                return redirect('manage_roles')
            group.name = new_name
            group.save()

        if valid_perm_ids:
            perms = Permission.objects.filter(id__in=valid_perm_ids)
            group.permissions.set(perms)
        else:
            group.permissions.clear()

        messages.success(request, f"Successfully updated settings for role group '{group.name}'!")
        
    return redirect('manage_roles')


@login_required
@user_passes_test(is_admin_user, login_url='dashboard')
def delete_group(request, group_id):
    """❌ Drops an authorization role mapping from the global identity framework"""
    if request.method == 'POST':
        group = get_object_or_404(Group, id=group_id)
        group_name = group.name
        group.delete()
        messages.success(request, f"Successfully destroyed security role group: '{group_name}'.")
    else:
        messages.error(request, "Invalid security request format standard.")
    return redirect('manage_roles')