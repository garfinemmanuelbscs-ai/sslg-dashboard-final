from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    source = models.CharField(max_length=100)  # e.g. "Fundraising", "Supplies"
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')]
    )
    date = models.DateField(auto_now_add=True)
    officer = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.source} - {self.type} - {self.amount}"

    class Meta:
        app_label = 'finance'              # <-- forces Django to show Finance
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        default_permissions = ('add', 'view')  # 🛑 Permanently locks out change & delete permissions
        # 🖨️ Explicit custom print permission registration
        permissions = [
            ("print_transaction", "Can print financial ledger registry indices"),
        ]