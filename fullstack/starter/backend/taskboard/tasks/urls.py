from django.urls import path
from .views import (
    TaskListCreateAPIView,
    TaskRetrieveUpdateAPIView,
    TaskDependenciesAPIView,
    ForceCloseTaskAPIView,
    EventListAPIView
)

urlpatterns = [
    # Liste toutes les tâches et création
    path("tasks/", TaskListCreateAPIView.as_view(), name="tasks-list-create"),

    # Détail, update ou delete une tâche spécifique
    path("tasks/<int:pk>/", TaskRetrieveUpdateAPIView.as_view(), name="tasks-detail"),

    # Récupérer les dépendances d'une tâche
    path("tasks/<int:pk>/dependencies/", TaskDependenciesAPIView.as_view(), name="tasks-dependencies"),

    # Forcer la clôture d'une tâche (Manager only)
    path("tasks/<int:pk>/force-close/", ForceCloseTaskAPIView.as_view(), name="tasks-force-close"),

    # Journal des événements, filtrable par task_id
    path("events/", EventListAPIView.as_view(), name="events-list"),
]
