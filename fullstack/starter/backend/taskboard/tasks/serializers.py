from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    # Champ calculé : priorité dynamique
    priority = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = "__all__"

    def get_priority(self, obj):
        """
        Retourne la priorité calculée de la tâche
        (base_priority + urgency_score).
        """
        return obj.priority

    def validate(self, data):
        """
        Vérifie les règles métiers avant création ou mise à jour.
        - Si status -> DONE
        - Si utilisateur non manager et force=False
        - Vérifie que toutes les dépendances sont DONE
        """
        status = data.get("status", getattr(self.instance, "status", None))
        user = self.context["request"].user
        force = self.context["request"].data.get("force", False)

        if status == Task.STATUS_DONE and not (user.is_manager() or force):
            task = self.instance
            if task and task.unresolved_dependencies().exists():
                raise serializers.ValidationError(
                    "Impossible de marquer DONE : certaines dépendances ne sont pas terminées."
                )
        return data

    def attach_modified_by(self, instance):
        """
        Méthode utilitaire pour signal/log : qui a modifié/créé la tâche
        """
        setattr(instance, "_modified_by", self.context["request"].user)

    def create(self, validated_data):
        task = super().create(validated_data)
        self.attach_modified_by(task)
        return task

    def update(self, instance, validated_data):
        self.attach_modified_by(instance)
        return super().update(instance, validated_data)

    def save(self, *args, **kwargs):
        # sécurise attach_modified_by pour les créations
        if self.instance:
            self.attach_modified_by(self.instance)
        return super().save(*args, **kwargs)
