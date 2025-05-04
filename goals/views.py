
# views.py
from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import Goal, GoalCheckIn,ReminderSettings
from .serializers import (
    UserSerializer, GoalSerializer,
    GoalProgressSerializer, AnalyticsSerializer, ReminderSettingsSerializer
)
from datetime import timezone


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    http_method_names = ['post']

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                         context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Goal.objects.filter(user=self.request.user)
        date = self.request.query_params.get('date')
        search = self.request.query_params.get('search')

        if date:
            queryset = queryset.filter(checkins__date=date)
        if search:
            queryset = queryset.filter(title__icontains=search)
            
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def checkin(self, request, pk=None):
        goal = self.get_object()
        date = request.data.get('date', timezone.now().date())
        
        checkin, created = GoalCheckIn.objects.update_or_create(
            goal=goal,
            date=date,
            defaults={'completed': True}
        )
        
        return Response({
            'message': 'Goal marked as completed for today.',
            'current_streak': goal.current_streak
        })

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        goal = self.get_object()
        serializer = GoalProgressSerializer(goal)
        return Response(serializer.data['progress'])

class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        goals = Goal.objects.filter(user=request.user)
        checkins_today = GoalCheckIn.objects.filter(
            goal__user=request.user,
            date=timezone.now().date(),
            completed=True
        ).count()

        analytics = {
            'total_goals': goals.count(),
            'active_goals': goals.count(),
            'completed_today': checkins_today,
            'longest_streak_overall': max(
                [goal.longest_streak for goal in goals], default=0
            ),
            'most_consistent_goal': goals.order_by('-current_streak')
                .values('title', 'current_streak').first()
        }
        serializer = AnalyticsSerializer(analytics)
        return Response(serializer.data)

class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReminderSettings.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

