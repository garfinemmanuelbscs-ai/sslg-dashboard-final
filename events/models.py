from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    venue = models.CharField(max_length=100)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    actual_expense = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    participants = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.date})"

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
