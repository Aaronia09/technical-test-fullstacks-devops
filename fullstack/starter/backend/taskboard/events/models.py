from django.db import models
from django.conf import settings

class Event(models.Model):
    task = models.ForeignKey("tasks.Task", on_delete=models.CASCADE, related_name="events")
    who = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    what = models.CharField(max_length=120)  # e.g. "status_changed"
    previous_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
