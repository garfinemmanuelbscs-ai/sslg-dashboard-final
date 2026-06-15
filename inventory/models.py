from django.db import models
from django.contrib.auth.models import User

class Item(models.Model):
    # unique=True guarantees we don't get duplicate rows for the same item name
    name = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    condition = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('lost', 'Lost')],
        default='good'
    )
    custodian = models.CharField(max_length=100, blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity} in stock)"

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        # 🔓 Removed default_permissions lock to allow standard deletion operations
        permissions = [
            ("print_item", "Can print asset management summary registries"),
        ]

class InventoryLog(models.Model):
    ACTION_CHOICES = [
        ('add', 'Add Stock (+)'),
        ('borrow', 'Borrow Item (-)'),
        ('lost', 'Report Lost (-)'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='logs')
    action_type = models.CharField(max_length=15, choices=ACTION_CHOICES)
    quantity = models.PositiveIntegerField()
    officer = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Inventory Transaction Log"
        verbose_name_plural = "Inventory Transaction Logs"

    def __str__(self):
        return f"{self.action_type.upper()} - {self.item.name} ({self.quantity}) by {self.officer.username}"