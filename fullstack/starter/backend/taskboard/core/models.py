from django.db import models
from django.contrib.auth.models import AbstractUser

class Team(models.Model):
    name = models.CharField(max_length=120)
    # lead can be null initially
    lead = models.ForeignKey("User", null=True, blank=True, on_delete=models.SET_NULL, related_name="leading_teams")

    def __str__(self):
        return self.name

class User(AbstractUser):
    ROLE_USER = "User"
    ROLE_LEAD = "Lead"
    ROLE_MANAGER = "Manager"
    ROLE_CHOICES = [
        (ROLE_USER, "User"),
        (ROLE_LEAD, "Lead"),
        (ROLE_MANAGER, "Manager"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    manager = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="subordinates")
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name="members")

    def is_manager(self): return self.role == self.ROLE_MANAGER
    def is_lead(self): return self.role == self.ROLE_LEAD
