# tasks/models.py
from django.db import models
from django.utils import timezone
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Task(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_IN_PROGRESS = "IN_PROGRESS"
    STATUS_DONE = "DONE"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_IN_PROGRESS, "In Progress"),
        (STATUS_DONE, "Done"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    base_priority = models.IntegerField(default=0)
    due_date = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.FloatField(blank=True, null=True)
    assigned_to = models.ManyToManyField(User, blank=True, related_name="tasks")
    dependencies = models.ManyToManyField("self", blank=True, symmetrical=False, related_name="dependents")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def urgency_score(self):
        score = 0
        if self.due_date:
            delta_days = (self.due_date - timezone.now()).days
            score += max(0, 10 - delta_days)  # plus proche = plus urgent
        score += self.unresolved_dependencies().count() * 5
        if self.estimated_hours:
            score += int(self.estimated_hours)
        return score

    @property
    def priority(self):
        return self.base_priority + self.urgency_score

    def unresolved_dependencies(self):
        """Retourne les dépendances non terminées"""
        return self.dependencies.filter(~models.Q(status=self.STATUS_DONE))

    def __str__(self):
        return self.title
