from django.db import models
from django.contrib.auth.models import User


class PlanningTask(models.Model):
    STATUS_CHOICES = [
        ('pending',    'Pending'),
        ('in_progress', 'In Progress'),
        ('completed',  'Completed'),
        ('overdue',    'Overdue'),
    ]

    client      = models.CharField(max_length=200)
    obligation  = models.CharField(max_length=300)
    responsible = models.CharField(max_length=200)
    due_date    = models.DateField()
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes       = models.TextField(blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tasks')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Planning Task'
        verbose_name_plural = 'Planning Tasks'

    def __str__(self):
        return f"{self.client} — {self.obligation}"
