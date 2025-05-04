"""
URL configuration for microgoals project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from goals.views import (
    RegisterationViewSet,
    LoginViewSet,
    GoalViewSet,
    AnalyticsViewSet,
    ReminderViewSet
)

router = DefaultRouter()
router.register(r"register", RegisterationViewSet, basename="register")
router.register(r"login", LoginViewSet, basename="login")
router.register(r'goals', GoalViewSet, basename='goal')
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('api/analytics/', AnalyticsViewSet.as_view({'get': 'list'})),
    path('api/', include(router.urls)),
]


