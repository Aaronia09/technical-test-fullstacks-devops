
from taskboard.core.models import User
from taskboard.tasks import models


class Event(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="events")
    who = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    what = models.CharField(max_length=255)
    previous_value = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Task, Event

@receiver(post_save, sender=Task)
def log_task_change(sender, instance, created, **kwargs):
    user = getattr(instance, "_modified_by", None)
    what = "Created" if created else "Updated"
    previous_status = None
    if not created:
        previous_status = instance.__class__.objects.get(pk=instance.pk).status

    event = Event.objects.create(
        task=instance,
        who=user,
        what=what,
        previous_value=previous_status
    )

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "tasks",
        {
            "type": "task_update",
            "data": {
                "task_id": instance.id,
                "title": instance.title,
                "status": instance.status,
                "priority": instance.priority,
                "event": {
                    "what": what,
                    "who": user.username if user else None,
                    "previous_value": previous_status,
                    "created_at": str(event.created_at),
                },
            },
        }
    )
