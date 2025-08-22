from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from taskboard.taskboard import settings
from .models import Task
from events.models import Event
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(pre_save, sender=Task)
def log_status_and_assignment_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    prev = Task.objects.get(pk=instance.pk)
    changes = []
    if prev.status != instance.status:
        Event.objects.create(task=instance, who=getattr(instance, "_modified_by", None),
                             what="status_changed", previous_value=prev.status)
        changes.append(("status", prev.status))
    if prev.assigned_to_id != instance.assigned_to_id:
        Event.objects.create(task=instance, who=getattr(instance, "_modified_by", None),
                             what="assignment_changed", previous_value=str(prev.assigned_to_id))
        changes.append(("assigned_to", prev.assigned_to_id))

    # broadcast via channels
    if changes:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "tasks", {"type": "task_update", "data": {"task_id": instance.pk, "changes": changes}}
        )

@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def reassign_tasks_on_user_delete(sender, instance, **kwargs):
    manager = instance.manager
    qs = Task.objects.filter(assigned_to=instance)
    for t in qs:
        t.assigned_to = manager if manager else None
        t.save()
        Event.objects.create(task=t, who=None, what="reassigned_on_user_delete", previous_value=str(instance.pk))
