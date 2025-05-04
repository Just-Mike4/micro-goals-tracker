# models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_time = models.TimeField(null=True, blank=True)
    reminder_enabled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def current_streak(self):
        """Calculate current consecutive day streak"""
        checkins = self.checkins.filter(completed=True).order_by('-date')
        if not checkins.exists():
            return 0

        streak = 0
        current_date = timezone.now().date()
        
        for checkin in checkins:
            if checkin.date == current_date - timedelta(days=streak):
                streak += 1
            else:
                break
        return streak

    @property
    def longest_streak(self):
        """Calculate longest consecutive day streak"""
        dates = list(self.checkins.filter(completed=True)
                    .order_by('date')
                    .values_list('date', flat=True))
        
        if not dates:
            return 0

        longest = current = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    @property
    def last_checkin_date(self):
        last = self.checkins.filter(completed=True).order_by('-date').first()
        return last.date if last else None


class GoalCheckIn(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(default=timezone.now)
    completed = models.BooleanField(default=True)

    class Meta:
        unique_together = ('goal', 'date')
        ordering = ['-date']

    def __str__(self):
        status = "✓" if self.completed else "✗"
        return f"{self.goal.title} {self.date} {status}"


class ReminderSettings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    goal = models.OneToOneField(Goal, on_delete=models.CASCADE)
    time = models.TimeField()
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Reminder for {self.goal.title} at {self.time}"