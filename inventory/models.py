from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(
        max_length=20,
        choices=[('good', 'Good'), ('damaged', 'Damaged'), ('lost', 'Lost')]
    )
    custodian = models.CharField(max_length=100)  # who is responsible
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    class Meta:
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
