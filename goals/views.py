
# views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Goal, GoalCheckIn,ReminderSettings
from .serializers import (
     GoalSerializer,
    GoalProgressSerializer, AnalyticsSerializer, ReminderSettingsSerializer
)
from datetime import timezone
from .serializers import (RegisterationSerializer,LoginSerializer)
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken






class RegisterationViewSet(viewsets.ModelViewSet):
    serializer_class = RegisterationSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post')
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result =serializer.save()
        return Response(
        result
        , status=status.HTTP_201_CREATED)
        
class LoginViewSet(viewsets.ModelViewSet):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ('post')
    
    def create(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


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

