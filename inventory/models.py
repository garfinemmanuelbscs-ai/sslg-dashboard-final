from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('lost', 'Lost')]
    )
    custodian = models.CharField(max_length=100)  # who is responsible
    date_added = models.DateTimeField(auto_now_add=True) # Upgraded to DateTimeField to log exact print precision times

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        default_permissions = ('add', 'view')  # 🛑 Permanently locks out change & delete permissions
        # 🖨️ Explicit custom print permission registration
        permissions = [
            ("print_item", "Can print asset management summary registries"),
        ]