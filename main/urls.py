from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('register/', views.register, name='register'),
    path("roster/", views.roster, name="roster"),
    path('schedule/', views.schedule, name='schedule'),
    path('statistics/', views.statistics, name='statistics'),
    path('team/', views.team, name='team'),
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout_view, name="logout"),
    path('social/', include('social.urls')),

]
