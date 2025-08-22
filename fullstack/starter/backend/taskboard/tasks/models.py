from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

class Task(models.Model):
    STATUS_TODO = "TODO"
    STATUS_INPROG = "IN_PROGRESS"
    STATUS_DONE = "DONE"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_CHOICES = [
        (STATUS_TODO, "TODO"),
        (STATUS_INPROG, "IN_PROGRESS"),
        (STATUS_DONE, "DONE"),
        (STATUS_CANCELLED, "CANCELLED"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    depends_on = models.ManyToManyField("self", symmetrical=False, blank=True, related_name="dependents")
    base_priority = models.IntegerField(default=0)
    due_date = models.DateTimeField(null=True, blank=True)
    estimated_hours = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TODO)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def unresolved_dependencies(self):
        return self.depends_on.exclude(status=self.STATUS_DONE)

    @property
    def urgency_score(self):
        score = 0
        # due date closeness
        if self.due_date:
            delta = (self.due_date - timezone.now()).total_seconds()
            days = delta / 86400
            if days < 1: score += 5
            elif days < 3: score += 3
            elif days < 7: score += 1
        # unresolved deps
        score += 2 * self.unresolved_dependencies().count()
        # estimated hours
        if self.estimated_hours:
            if self.estimated_hours > 8: score += 2
            elif self.estimated_hours > 4: score += 1
        return score

    @property
    def priority(self):
        return self.base_priority + self.urgency_score

    def save(self, *args, **kwargs):
        # detect status change for event logging -> implemented elsewhere or override here
        super().save(*args, **kwargs)
