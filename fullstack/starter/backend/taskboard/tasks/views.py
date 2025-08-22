from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task
from .serializers import TaskSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().prefetch_related("depends_on")
    serializer_class = TaskSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ("status", "assigned_to")

    @action(detail=True, methods=["get"])
    def dependencies(self, request, pk=None):
        task = self.get_object()
        serializer = TaskSerializer(task.depends_on.all(), many=True, context={"request": request})
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="force-close")
    def force_close(self, request, pk=None):
        # Manager-only check
        if not request.user.is_manager():
            return Response({"detail": "Manager only"}, status=403)
        task = self.get_object()
        task.status = Task.STATUS_DONE
        setattr(task, "_modified_by", request.user)
        task.save()
        return Response(TaskSerializer(task, context={"request": request}).data)
