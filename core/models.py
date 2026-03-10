from django.db import models
from django.contrib.auth.models import User

class Team(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    
    # Tracks creator for role-based deletion logic
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_teams')
    
    # Through model allows tracking extra data (like roles) when adding members
    members = models.ManyToManyField(User, related_name='teams', through='TeamMember')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TeamMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('member', 'Member')
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Database Constraint: A user can only be added to a specific team once.
        This prevents duplicate member entries and data corruption.
        """
        unique_together = ('user', 'team')

    def __str__(self):
        return f"{self.user.username} in {self.team.name} ({self.get_role_display()})"

class Task(models.Model):
    STATUS_CHOICES = [
        ('todo', 'To Do'), 
        ('in_progress', 'In Progress'), 
        ('done', 'Done')
    ]
    
    title = models.CharField(max_length=255)
    # Made blank/null True to match our frontend UI where description is optional
    description = models.TextField(blank=True, null=True)
    
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='tasks')
    
    # Made blank=True so forms don't force an immediate assignment upon task creation
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    
    # Supports the optional "Task due date reminders" bonus feature
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.team.name}"