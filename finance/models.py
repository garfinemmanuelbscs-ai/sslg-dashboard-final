from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    source = models.CharField(max_length=100)  # e.g. "Fundraising", "Supplies"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )
    # 🕒 FIX: Changed from DateField to DateTimeField to capture exact time!
    date = models.DateTimeField(auto_now_add=True)
    officer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.source} - {self.type} - {self.amount}"

    class Meta:
        app_label = 'finance'
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        # 🔓 FIX: Removed the restrictive default_permissions so delete works!
        permissions = [
            ("print_transaction", "Can print financial ledger registry indices"),
        ]