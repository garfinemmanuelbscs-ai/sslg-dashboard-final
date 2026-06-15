from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import F
from .models import Item, InventoryLog

def is_inventory_authorized(user):
    if not user or user.is_anonymous:
        return False
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm('inventory.view_item') or
        user.groups.filter(permissions__codename='view_item').exists()
    )

def can_print_inventory(user):
    if not user or user.is_anonymous:
        return False
    return (
        user.is_superuser or 
        user.username.lower() == 'admin' or 
        user.has_perm('inventory.print_item') or
        user.groups.filter(permissions__codename='print_item').exists()
    )

@login_required
@user_passes_test(is_inventory_authorized, login_url='dashboard')
def inventory_management(request):
    """📦 Core Inventory Matrix Controller with Automated Dynamic Stock Balance Updating"""
    if request.method == 'POST':
        is_write_authorized = (
            request.user.is_superuser or 
            request.user.username.lower() == 'admin' or 
            request.user.has_perm('inventory.add_item') or
            request.user.groups.filter(permissions__codename='add_item').exists()
        )
        
        if not is_write_authorized:
            messages.error(request, "Access Denied: You lack explicit privileges to alter inventory stock levels.")
            return redirect('inventory_management')

        name = request.POST.get('name', '').strip()
        quantity_str = request.POST.get('quantity')
        action_type = request.POST.get('action_type') # 'add', 'borrow', 'lost'
        remarks = request.POST.get('remarks', '').strip()
        custodian = request.POST.get('custodian', '').strip() or request.user.username

        if name and quantity_str and action_type:
            try:
                qty = int(quantity_str)
                if qty <= 0:
                    messages.error(request, "Invalid Quantity: Input value must be greater than zero.")
                    return redirect('inventory_management')

                # 🗂️ Check if item already exists or instantiate a fresh master definition
                item, created = Item.objects.get_or_create(
                    name__iexact=name, 
                    defaults={'name': name, 'quantity': 0, 'custodian': custodian}
                )

                # 📊 Execute Stock Accounting Calculations
                if action_type == 'add':
                    item.quantity += qty
                    item.condition = 'good'
                elif action_type in ['borrow', 'lost']:
                    if item.quantity < qty:
                        messages.error(request, f"Transaction Rejected: Insufficient stock. Only ({item.quantity}) items available for '{item.name}'.")
                        return redirect('inventory_management')
                    
                    item.quantity -= qty
                    if action_type == 'lost':
                        item.condition = 'lost'

                if custodian:
                    item.custodian = custodian
                item.save()

                # 📝 Create the permanent chronological transaction audit log entry
                InventoryLog.objects.create(
                    item=item,
                    action_type=action_type,
                    quantity=qty,
                    officer=request.user,
                    remarks=remarks if remarks else f"Stock updated via inventory console."
                )

                messages.success(request, f"Successfully recorded transaction line item for {item.name}!")
            except Exception as e:
                messages.error(request, f"System transaction tracking failure: {e}")
        else:
            messages.error(request, "Failed to execute transaction: Missing required fields.")
        return redirect('inventory_management')

    # Query items and full historic timeline transaction sheets
    all_items = Item.objects.all().order_by('name')
    transaction_logs = InventoryLog.objects.all().order_by('-timestamp')
    
    total_items_count = all_items.count()
    low_stock_count = Item.objects.filter(quantity__lte=5).count()
    damaged_or_lost_count = Item.objects.filter(condition__in=['damaged', 'lost']).count()

    context = {
        'title': '📦 Inventory Stock Registry',
        'all_items': all_items,
        'transaction_logs': transaction_logs,
        'total_count': total_items_count,
        'low_stock_count': low_stock_count,
        'damaged_count': damaged_or_lost_count,
    }
    return render(request, 'inventory/inventory.html', context)

@login_required
def delete_item(request, item_id):
    """🗑️ Completely drops a master item tracking entry along with its structural logging fields"""
    is_write_authorized = (
        request.user.is_superuser or 
        request.user.username.lower() == 'admin' or 
        request.user.has_perm('inventory.delete_item') or
        request.user.groups.filter(permissions__codename='delete_item').exists()
    )
    if not is_write_authorized:
        messages.error(request, "Access Denied: Your account role limits do not permit item record pruning.")
        return redirect('inventory_management')

    item = get_object_or_404(Item, id=item_id)
    name = item.name
    item.delete()
    messages.success(request, f"Permanently removed {name} from organizational stock records.")
    return redirect('inventory_management')

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