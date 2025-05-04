# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Goal, GoalCheckIn, ReminderSettings
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class GoalCheckInSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")
    class Meta:
        model = GoalCheckIn
        fields = ['date', 'completed']
        read_only_fields = ['date']

class GoalSerializer(serializers.ModelSerializer):
    streak = serializers.SerializerMethodField()
    last_checkin = serializers.SerializerMethodField()
    
    class Meta:
        model = Goal
        fields = [
            'id', 'title', 'description', 'created_at', 
            'reminder_time', 'streak', 'last_checkin'
        ]
        read_only_fields = ['id', 'created_at', 'streak', 'last_checkin']

    def get_streak(self, obj):
        return {
            'current': obj.current_streak,
            'longest': obj.longest_streak
        }

    def get_last_checkin(self, obj):
        return obj.last_checkin_date

class GoalProgressSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = ['progress']

    def get_progress(self, obj):
        checkins = obj.checkins.all().order_by('-date')
        return [
            {'date': checkin.date, 'completed': checkin.completed}
            for checkin in checkins
        ]

class ReminderSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReminderSettings
        fields = ['goal', 'time', 'enabled']
        extra_kwargs = {'goal': {'read_only': True}}

class AnalyticsSerializer(serializers.Serializer):
    total_goals = serializers.IntegerField()
    active_goals = serializers.IntegerField()
    completed_today = serializers.IntegerField()
    longest_streak_overall = serializers.IntegerField()
    most_consistent_goal = serializers.DictField()
