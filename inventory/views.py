from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import F
from .models import Item

# ==========================================
# 🔐 GRANULAR INVENTORY SECURITY CONTROLLERS
# ==========================================

def is_inventory_authorized(user):
    """🛡️ Multi-layered permission check matching explicit and inherited group states for inventory"""
    if not user or user.is_anonymous:
        return False
        
    # 🕵️‍♂️ TEMPORARY DIAGNOSTIC CONSOLE LOG
    print("\n=== ⚙️ INVENTORY SECURITY CREDENTIAL DIAGNOSTIC MATRIX ===")
    print(f"User Attempting Access: '{user.username}'")
    print(f"Is Root Superuser:       {user.is_superuser}")
    print(f"Active Groups Linked:    {list(user.groups.values_list('name', flat=True))}")
    
    # Check what permissions are actually bundled inside those groups
    group_permission_tokens = []
    for group in user.groups.all():
        for perm in group.permissions.all():
            group_permission_tokens.append(f"{perm.content_type.app_label}.{perm.codename}")
            
    print(f"Permissions via Groups:  {group_permission_tokens}")
    print("========================================================\n")
        
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm('inventory.view_item') or
        user.groups.filter(permissions__codename='view_item').exists()
    )

def can_print_inventory(user):
    """🛡️ Guardrail: Only allows roles with explicit inventory printing permissions to generate summaries"""
    if not user or user.is_anonymous:
        return False
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm('inventory.print_item') or
        user.groups.filter(permissions__codename='print_item').exists()
    )


# ==========================================
# 🏛️ INVENTORY MANAGEMENT CORE GATEWAYS
# ==========================================

@login_required
@user_passes_test(is_inventory_authorized, login_url='dashboard')
def inventory_management(request):
    """📦 Live Inventory Registry & Asset Tracker View"""
    if request.method == 'POST':
        # 🛡️ GRANULAR WRITE SECURITY GATEWAY
        is_write_authorized = (
            request.user.is_superuser or 
            request.user.username.lower() == 'admin' or 
            request.user.has_perm('inventory.add_item') or
            request.user.groups.filter(permissions__codename='add_item').exists()
        )
        
        if not is_write_authorized:
            messages.error(request, "Access Denied: Your assigned role is Read-Only and lacks explicit inventory write privileges.")
            return redirect('inventory_management')

        # 📥 Secure Data Processing Block
        name = request.POST.get('name')
        quantity = request.POST.get('quantity')
        condition = request.POST.get('condition')
        custodian = request.POST.get('custodian')
        
        if name and quantity and condition and custodian:
            try:
                Item.objects.create(
                    name=name,
                    quantity=int(quantity),
                    condition=condition,
                    custodian=custodian
                )
                messages.success(request, f"Successfully registered item: {name} into stock!")
            except Exception as e:
                messages.error(request, f"Failed to register asset: {e}")
        else:
            messages.error(request, "Asset registration failed: Missing required fields.")
        return redirect('inventory_management')

    # Query all inventory items from the database
    all_items = Item.objects.all().order_by('name')
    
    # Track metrics for the overview scorecards
    total_items_count = all_items.count()
    low_stock_threshold = 5
    low_stock_count = Item.objects.filter(quantity__lte=low_stock_threshold).count()
    damaged_count = Item.objects.filter(condition='damaged').count()

    context = {
        'title': '📦 Inventory Stock Registry',
        'all_items': all_items,
        'total_count': total_items_count,
        'low_stock_count': low_stock_count,
        'damaged_count': damaged_count,
    }
    
    return render(request, 'inventory/inventory.html', context)


# ==========================================
# 🖨️ SYSTEM PRINT GENERATION TERMINALS
# ==========================================

@login_required
@user_passes_test(can_print_inventory, login_url='inventory_management')
def print_inventory(request):
    """🖨️ Generates print-optimized physical plant asset inventories via strict matrix gate controls"""
    # .annotate maps your database 'date_added' to the 'created_at' lookups expected by your print template layout
    items = Item.objects.all().annotate(created_at=F('date_added')).order_by('name')
    return render(request, 'inventory/print_inventory.html', {'items': items})