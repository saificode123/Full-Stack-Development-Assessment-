from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    # Bonus: Tracks creator for role-based deletion logic [cite: 45]
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    members = models.ManyToManyField(User, related_name='teams', through='TeamMember')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    # Professional 'through' table for roles [cite: 45]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='member') # e.g., 'admin', 'member'

class Task(models.Model):
    STATUS_CHOICES = [('todo', 'To Do'), ('in_progress', 'In Progress'), ('done', 'Done')]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    # Bonus: For task reminders [cite: 44]
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)