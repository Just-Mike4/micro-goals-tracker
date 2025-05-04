# serializers.py

from .models import Goal, GoalCheckIn, ReminderSettings
from rest_framework import serializers
from .forms import UserForm
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from django.contrib.auth.models import update_last_login
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

class RegisterationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        form = UserForm({
            "username": data.get("username"),
            "email": data.get("email"),
            "password1": data.get("password"),
        })
        if not form.is_valid():
            raise serializers.ValidationError(form.errors)


        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
        )

        # Generate JWT access token
        access = AccessToken.for_user(user)

        return {
            "username": validated_data['username'],
            "email": validated_data['email'],
            "token": str(access)
        }


class LoginSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

    def validate(self, attrs):
        data = {}
        email = attrs.get('email')
        password = attrs.get('password')

        user = User.objects.filter(email=email).first()

        if user and user.check_password(password):
            access = self.get_token(user).access_token
            data['token'] = str(access)
            
            if api_settings.UPDATE_LAST_LOGIN:
                update_last_login(None, user)

        else:
            raise serializers.ValidationError({
                "error": "Invalid email/password"
            })

        return data

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
